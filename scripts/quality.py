#!/usr/bin/env python3
"""Unified Markdown quality tool: use --check to verify, --fix to correct.

This script merges the functionality of verify_quality.py and fix_quality.py
into a single, optimized tool with shared logic and a simplified CLI.

## Modes (simplified)

### Default (no flags)
  Run verification and generate a Markdown report.
  Example: python quality_tool.py > report.md

### --check
  Verify Markdown quality and emit a report.
  Example: python quality_tool.py --check --docs-dir docs > report.md

### --fix
  Auto-fix safe issues in place.
  Example: python quality_tool.py --fix --docs-dir docs --dry-run

### --check --fix
  Run verification, then fix (in one command).
  Example: python quality_tool.py --check --fix --docs-dir docs

## Checks (verification)

### Errors (fail the check)
  --html              HTML tags detected (excluding comments and code blocks)
  --headings          multiple H1 headings or inconsistent heading hierarchy (level skips)
  --links-absolute    internal links written as absolute URLs to the site domain
  --links-broken      relative links whose target does not exist
  --images-missing    images (markdown or <img>) whose file does not exist
  --images-external   images not stored locally (external URL, or absolute URL to the site domain)
  --i18n              file-count consistency across languages (reference: "en")
  --frontmatter       presence of the `path:` key in the YAML front-matter

### Warnings (do not fail by default)
  --links-md-ext      inconsistency of the .md extension in relative links
  --anchors           anchors (#...) not found in the target file
  --placeholders      untranslated / placeholder text ("See page ...", TODO)
  --whitespace        trailing whitespace and multiple blank lines at EOF

## Fixes (automatic corrections)

  whitespace        -> rstrip each line, collapse trailing blank lines
  headings         -> ensure single H1, fix heading level skips
  img              -> convert <img> HTML tags to ![alt](src)
  links-absolute   -> rewrite internal absolute links to relative paths
  images-absolute  -> rewrite absolute image URLs (site domain) to relative paths
  links-md-ext     -> normalize relative .md link targets (majority style)
  frontmatter      -> add `path:` key to docs/doc/<lang>/*.md
  images-external  -> download external images (WP, GitHub, BuyMeACoffee) to docs/images/

## Usage Examples

# Generate a quality report
python quality_tool.py --check > report.md
python quality_tool.py > report.md  # --check is default

# Auto-fix issues in place
python quality_tool.py --fix --dry-run  # Preview changes
python quality_tool.py --fix            # Apply fixes

# Check then fix in one command
python quality_tool.py --check --fix

# Target specific checks/fixes
python quality_tool.py --check --only headings whitespace
python quality_tool.py --fix --only headings frontmatter

# Custom options
python quality_tool.py --check --strict --docs-dir mydocs
python quality_tool.py --fix --dry-run --only images-external

## Exit Codes

- check mode: 0 if no errors (or no warnings with --strict), 1 otherwise
- fix mode: 0 on success, 1 if any file could not be fixed cleanly
- check-fix mode: exit code from check mode

## Dependencies

No external dependencies (stdlib only). Network access is optional for
images-external fix (disabled with --no-network).
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import sys
import time
import urllib.request
from pathlib import Path
from urllib.parse import unquote, urlparse


# =============================================================================
# SHARED CONSTANTS
# =============================================================================

DEFAULT_SITE_DOMAIN = "qualcoder.org"
DEFAULT_REF_LANG = "en"

# Placeholders / unfinished text patterns
PLACEHOLDER_PATTERNS = [
    re.compile(r"\bSee page\s*\.\.\.", re.IGNORECASE),
    re.compile(r"\bTODO\b"),
    re.compile(r"\bFIXME\b"),
    re.compile(r"\bTBD\b"),
    re.compile(r"\bXXX\b"),
]

# Regex patterns
HTML_TAG_RE = re.compile(r"</?[a-zA-Z][a-zA-Z0-9-]*(\s[^>]*?)?/?>")
MD_LINK_RE = re.compile(r"(?<!\\)\[([^\]]*)\]\(([^)]+?)\)")
MD_IMAGE_RE = re.compile(r"!\[([^\]]*)\]\(([^)]+?)\)")
IMG_SRC_RE = re.compile(r'<img\b[^>]*\bsrc\s*=\s*"([^"]+)"', re.IGNORECASE)
IMG_TAG_RE = re.compile(r"<img\b[^>]*?/?>", re.IGNORECASE)
ATTR_RE = re.compile(r'(\w[\w-]*)\s*=\s*"([^"]*)"', re.IGNORECASE)
FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*(?:\n|$)", re.DOTALL)

# External image hosts
WP_RE = re.compile(
    r"https://qualcoder\.wordpress\.com/wp-content/uploads/"
    r"(?P<y>\d{4})/(?P<m>\d{2})/(?P<name>[^)\s]+)"
)
GH_RE = re.compile(r"https://github\.com/user-attachments/assets/(?P<uuid>[a-f0-9-]+)")
BMC_RE = re.compile(r"https://cdn\.buymeacoffee\.com/buttons/(?P<name>[^)\s]+)")
EXT_URL_RE = re.compile(
    r"https://(?:"
    r"qualcoder\.wordpress\.com/wp-content/uploads/[^)\s]+"
    r"|github\.com/user-attachments/assets/[a-f0-9-]+"
    r"|cdn\.buymeacoffee\.com/buttons/[^)\s]+"
    r")"
)

UA = "Mozilla/5.0 (X11; Linux x86_64) QualCoder-docs-quality-tool"

# Cache for fetched external images (URL -> local Path)
_FETCH_CACHE: dict[str, Path] = {}

# Cache for discovered doc languages
DOC_LANGS: set[str] | None = None


# =============================================================================
# SHARED DATA STRUCTURES
# =============================================================================

class Issue:
    """A detected problem. severity is 'error' or 'warning'."""

    def __init__(self, check: str, message: str, line: int, severity: str = "error"):
        self.check = check
        self.message = message
        self.line = line
        self.severity = severity

    def __repr__(self) -> str:
        return f"[{self.severity}] {self.check}: {self.message}"


# =============================================================================
# SHARED UTILITY FUNCTIONS
# =============================================================================

def os_relpath(start: Path, target: Path) -> str:
    """Cross-platform relative path from start to target, using forward slashes."""
    return os.path.relpath(target, start).replace(os.sep, "/")


def _split_url_fragment(url: str) -> tuple[str, str]:
    """Split a URL into (target_path, fragment)."""
    if "#" in url:
        target, _, frag = url.partition("#")
        return target, frag
    return url, ""


def split_front_matter(text: str) -> tuple[str, str]:
    """Split YAML front-matter from the body. Returns (frontmatter, body)."""
    m = FRONTMATTER_RE.match(text)
    if not m:
        return "", text
    return m.group(1), text[m.end():]


def parse_front_matter(fm: str) -> dict[str, str]:
    """Minimal YAML parser (key: value) sufficient to read `path:`."""
    data: dict[str, str] = {}
    for line in fm.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" in line:
            key, _, value = line.partition(":")
            data[key.strip()] = value.strip().strip("\"'")
    return data


def strip_code_blocks(text: str) -> tuple[str, list[bool]]:
    """Return text with fenced code blocks replaced by blank lines, and a mask.
    
    Returns (cleaned_text, is_code_line_list) where is_code_line_list[i] is True
    if line i was inside a code block.
    """
    lines = text.splitlines()
    out: list[str] = []
    code_mask: list[bool] = []
    in_fence = False
    fence_marker = ""
    
    for line in lines:
        stripped = line.lstrip()
        if not in_fence and re.match(r"^(```|~~~)", stripped):
            in_fence = True
            fence_marker = stripped[:3]
            out.append("")
            code_mask.append(True)
            continue
        if in_fence:
            if stripped.startswith(fence_marker):
                in_fence = False
                out.append("")
                code_mask.append(True)
            else:
                out.append("")
                code_mask.append(True)
            continue
        out.append(line)
        code_mask.append(False)
    
    return "\n".join(out), code_mask


def strip_code_blocks_simple(text: str) -> str:
    """Return text with fenced code blocks replaced by blank lines."""
    lines = text.splitlines()
    out: list[str] = []
    in_fence = False
    fence_marker = ""
    
    for line in lines:
        stripped = line.lstrip()
        if not in_fence and re.match(r"^(```|~~~)", stripped):
            in_fence = True
            fence_marker = stripped[:3]
            out.append("")
            continue
        if in_fence:
            if stripped.startswith(fence_marker):
                in_fence = False
                out.append("")
            else:
                out.append("")
            continue
        out.append(line)
    
    return "\n".join(out)


def strip_html_comments(text: str) -> str:
    """Mask HTML comments <!-- ... --> (replace with spaces)."""
    return re.sub(
        r"<!--.*?-->", lambda m: " " * (m.end() - m.start()), text, flags=re.DOTALL
    )


def strip_inline_code(text: str) -> str:
    """Mask inline code `...` (replace with spaces of the same length)."""
    def repl(m: re.Match) -> str:
        return " " * (m.end() - m.start())
    return re.sub(r"`[^`\n]+`", repl, text)


def _is_internal_absolute(url: str, site_domain: str) -> bool:
    """Check if URL is an absolute URL to the internal site domain."""
    if url.startswith("#"):
        return False
    parsed = urlparse(url)
    if not parsed.scheme and not parsed.netloc:
        return False
    host = parsed.netloc.lower()
    return host == site_domain or host.endswith("." + site_domain)


def _resolve_md_target(
    docs_dir: Path, current_file: Path, url: str
) -> Path | None:
    """Resolve a relative link target to an existing .md file."""
    target, _frag = _split_url_fragment(url)
    target = target.split("?", 1)[0]  # strip query string
    
    if not target:
        return current_file
    
    if target.startswith(("http://", "https://", "mailto:")):
        return None
    
    base = current_file.parent
    candidate = (base / target).resolve()
    candidates = []
    
    if candidate.suffix == ".md":
        candidates.append(candidate)
    else:
        candidates.append(Path(str(candidate) + ".md"))
        candidates.append(candidate / "index.md")
    
    for c in candidates:
        if c.exists():
            return c
    return None


def _resolve_resource(docs_dir: Path, current_file: Path, url: str) -> Path | None:
    """Resolve a resource URL (image) to an existing file."""
    target, _frag = _split_url_fragment(url)
    if not target:
        return current_file
    
    if target.startswith(("http://", "https://", "mailto:", "data:")):
        return None
    
    if target.startswith("/"):
        candidate = (docs_dir / target.lstrip("/")).resolve()
    else:
        candidate = (current_file.parent / target).resolve()
    
    return candidate if candidate.exists() else None


def _abs_to_relative_target(docs_dir: Path, current_file: Path, url: str) -> str | None:
    """For an internal absolute URL, compute the suggested relative path."""
    parsed = urlparse(url)
    path = unquote(parsed.path)
    
    if path.endswith("/"):
        path = path[:-1]
    if not path:
        return None
    
    rel_path = path.lstrip("/")
    candidates = [
        docs_dir / (rel_path + ".md"),
        docs_dir / rel_path / "index.md",
        docs_dir / (rel_path + "/index.md"),
    ]
    
    # Try with doc/ prefix if direct candidates failed
    if not any(c.exists() for c in candidates) and not rel_path.startswith("doc/"):
        doc_path = "doc/" + rel_path
        candidates = [
            docs_dir / (doc_path + ".md"),
            docs_dir / doc_path / "index.md",
            docs_dir / (doc_path + "/index.md"),
        ]
    
    target = next((c for c in candidates if c.exists()), None)
    if target is None:
        return None
    
    rel = os_relpath(current_file.parent, target)
    if parsed.fragment:
        rel += f"#{parsed.fragment}"
    return rel


def _abs_resource_to_relative(docs_dir: Path, current_file: Path, url: str) -> str | None:
    """For an internal absolute image URL, compute the suggested relative path."""
    parsed = urlparse(url)
    target = unquote(parsed.path)
    
    if target.startswith("/"):
        candidate = (docs_dir / target.lstrip("/")).resolve()
    else:
        candidate = (current_file.parent / target).resolve()
    
    if not candidate.exists():
        return None
    
    rel = os_relpath(current_file.parent, candidate)
    if parsed.fragment:
        rel += f"#{parsed.fragment}"
    return rel


def _resource_exists(docs_dir: Path, current_file: Path, url: str) -> bool:
    """Check if a resource (image) exists."""
    target, _frag = _split_url_fragment(url)
    if not target:
        return True
    
    target = target.split("?", 1)[0]  # strip query string
    
    if target.startswith("/"):
        candidate = (docs_dir / target.lstrip("/")).resolve()
    else:
        candidate = (current_file.parent / target).resolve()
    
    return candidate.exists()


def _slugify(heading: str) -> str:
    """Approximate MkDocs-compatible slug: lowercase, punctuation removed, spaces -> hyphens."""
    s = heading.strip().lower()
    s = re.sub(r"[`*_~]", "", s)
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"\s+", "-", s)
    return s.strip("-")


def collect_anchors(md_file: Path) -> set[str]:
    """Collect all heading anchors from a Markdown file."""
    try:
        content = md_file.read_text(encoding="utf-8")
    except OSError:
        return set()
    
    _, body = split_front_matter(content)
    body = strip_code_blocks_simple(body)
    anchors: set[str] = set()
    
    for line in body.splitlines():
        m = re.match(r"^\s{0,3}(#{1,6})\s+(.+?)\s*#*\s*$", line)
        if m:
            anchors.add(_slugify(m.group(2)))
    return anchors


def discover_doc_langs(docs_dir: Path) -> set[str]:
    """Return the set of language directories under docs/doc/. Cached."""
    global DOC_LANGS
    if DOC_LANGS is not None:
        return DOC_LANGS
    
    langs: set[str] = set()
    doc_dir = docs_dir / "doc"
    if doc_dir.is_dir():
        for child in doc_dir.iterdir():
            if child.is_dir() and not child.name.startswith("."):
                langs.add(child.name)
    
    DOC_LANGS = langs
    return langs


def _lang_of_file(docs_dir: Path, md_file: Path) -> str | None:
    """If md_file lives under docs/doc/<lang>/..., return <lang>; else None."""
    try:
        rel = md_file.relative_to(docs_dir / "doc")
    except ValueError:
        return None
    
    if not rel.parts:
        return None
    
    lang = rel.parts[0]
    if lang in discover_doc_langs(docs_dir):
        return lang
    return None


# =============================================================================
# CHECK FUNCTIONS (Verification Mode)
# =============================================================================

def check_headings(path: Path, text: str) -> list[Issue]:
    """Check heading structure: only one H1 (#), consistent heading levels (no skips)."""
    issues: list[Issue] = []
    _, body = split_front_matter(text)
    cleaned = strip_code_blocks_simple(body)
    
    headings: list[tuple[int, str, int]] = []  # (level, title, line_no)
    
    for line_no, line in enumerate(cleaned.splitlines(), start=1):
        m = re.match(r"^(#{1,6})\s+(.+?)\s*#*\s*$", line)
        if m:
            level = len(m.group(1))
            title = m.group(2)
            headings.append((level, title, line_no))
    
    if not headings:
        # No headings at all - this might be intentional (e.g., index files)
        return issues
    
    # Check 1: Only one H1 (level 1) per file
    h1_count = sum(1 for h in headings if h[0] == 1)
    if h1_count > 1:
        h1_positions = [h[2] for h in headings if h[0] == 1]
        issues.append(
            Issue(
                "headings",
                f"Multiple H1 headings found at lines: {h1_positions}. Only one H1 (#) allowed per file.",
                h1_positions[0],
            )
        )
    elif h1_count == 0:
        # No H1 at all - warning (might be intentional for some files)
        issues.append(
            Issue(
                "headings",
                "No H1 heading (#) found. Consider adding a main title.",
                1,
                severity="warning",
            )
        )
    
    # Check 2: Consistent heading hierarchy (no level skips)
    for i in range(1, len(headings)):
        prev_level = headings[i-1][0]
        curr_level = headings[i][0]
        
        # After H1, next can be H1, H2, H3, H4, H5, H6
        # After H2, next can be H2, H3, H4, H5, H6 (not H1 or skip to H4+)
        # General rule: curr_level should be <= prev_level + 1
        # Exception: can jump back to any level (H3 -> H1 is fine for section breaks)
        
        if curr_level > prev_level + 1:
            # Skipped a level (e.g., H1 -> H3, or H2 -> H4)
            issues.append(
                Issue(
                    "headings",
                    f"Heading level skip: from H{prev_level} to H{curr_level} (missing H{prev_level + 1}). "
                    f"Line {headings[i][2]}: {headings[i][1]!r}",
                    headings[i][2],
                    severity="warning",
                )
            )
    
    return issues




def check_html(path: Path, text: str) -> list[Issue]:
    """Check for HTML tags (excluding comments and code blocks)."""
    issues: list[Issue] = []
    body_front, body = split_front_matter(text)
    cleaned = strip_code_blocks_simple(body)
    cleaned = strip_html_comments(cleaned)
    cleaned = strip_inline_code(cleaned)
    
    for m in HTML_TAG_RE.finditer(cleaned):
        tag = m.group(0)
        line_no = cleaned[: m.start()].count("\n") + 1
        name = re.match(r"</?([a-zA-Z][a-zA-Z0-9-]*)", tag).group(1).lower()
        
        if name == "img":
            suggestion = "use Markdown syntax `![alt](src)`"
            issues.append(
                Issue("html", f"HTML <img> tag -> {suggestion}: {tag!r}", line_no)
            )
        else:
            issues.append(Issue("html", f"forbidden HTML tag: {tag!r}", line_no))
    
    return issues


def check_links_absolute(
    path: Path, text: str, docs_dir: Path, site_domain: str
) -> list[Issue]:
    """Check for internal links written as absolute URLs."""
    issues: list[Issue] = []
    body_front, body = split_front_matter(text)
    cleaned = strip_code_blocks_simple(body)
    
    for m in MD_LINK_RE.finditer(cleaned):
        url = m.group(2).strip()
        url = re.sub(r'\s+"[^"]*"$', "", url)
        
        if _is_internal_absolute(url, site_domain):
            line_no = cleaned[: m.start()].count("\n") + 1
            suggestion = _abs_to_relative_target(docs_dir, path, url)
            hint = f" -> suggested: {suggestion!r}" if suggestion else ""
            issues.append(
                Issue(
                    "links-absolute",
                    f"internal link written as absolute URL to the site: {url!r}{hint}",
                    line_no,
                )
            )
    
    return issues


def check_links_broken(path: Path, text: str, docs_dir: Path) -> list[Issue]:
    """Check for broken relative links (target does not exist)."""
    issues: list[Issue] = []
    body_front, body = split_front_matter(text)
    cleaned = strip_code_blocks_simple(body)
    
    for m in MD_LINK_RE.finditer(cleaned):
        url = m.group(2).strip()
        url = re.sub(r'\s+"[^"]*"$', "", url)
        
        if not url or url.startswith("#"):
            continue
        if url.startswith(("http://", "https://", "mailto:")):
            continue
        
        resolved = _resolve_md_target(docs_dir, path, url)
        line_no = cleaned[: m.start()].count("\n") + 1
        
        if resolved is None:
            issues.append(
                Issue("links-broken", f"broken relative link (target not found): {url!r}", line_no)
            )
    
    return issues


def check_anchors(path: Path, text: str, docs_dir: Path) -> list[Issue]:
    """Check for anchors (#...) not found in the target file."""
    issues: list[Issue] = []
    body_front, body = split_front_matter(text)
    cleaned = strip_code_blocks_simple(body)
    
    for m in MD_LINK_RE.finditer(cleaned):
        url = m.group(2).strip()
        url = re.sub(r'\s+"[^"]*"$', "", url)
        
        if not url.startswith("#") and "#" not in url:
            continue
        if url.startswith(("http://", "https://", "mailto:")):
            continue
        
        target, frag = _split_url_fragment(url)
        if not frag:
            continue
        
        resolved = _resolve_md_target(docs_dir, path, url)
        if resolved is None:
            continue  # already reported by links-broken
        
        anchors = collect_anchors(resolved)
        line_no = cleaned[: m.start()].count("\n") + 1
        
        if frag not in anchors:
            issues.append(
                Issue(
                    "anchors",
                    f"anchor not found in {resolved.name}: #{frag}",
                    line_no,
                    severity="warning",
                )
            )
    
    return issues


def check_links_md_ext(path: Path, text: str, docs_dir: Path) -> list[Issue]:
    """Detect inconsistency in .md extension usage in relative links."""
    issues: list[Issue] = []
    body_front, body = split_front_matter(text)
    cleaned = strip_code_blocks_simple(body)
    
    with_ext: list[tuple[int, str]] = []
    without_ext: list[tuple[int, str]] = []
    
    for m in MD_LINK_RE.finditer(cleaned):
        url = m.group(2).strip()
        url = re.sub(r'\s+"[^"]*"$', "", url)
        
        if not url or url.startswith("#"):
            continue
        if url.startswith(("http://", "https://", "mailto:")):
            continue
        
        target, _frag = _split_url_fragment(url)
        if not target:
            continue
        
        resolved = _resolve_md_target(docs_dir, path, url)
        if resolved is None or resolved.suffix != ".md":
            continue
        
        line_no = cleaned[: m.start()].count("\n") + 1
        
        if target.endswith(".md"):
            with_ext.append((line_no, url))
        else:
            without_ext.append((line_no, url))
    
    if not with_ext and not without_ext:
        return issues
    
    if len(with_ext) >= len(without_ext):
        for line_no, url in without_ext:
            issues.append(
                Issue(
                    "links-md-ext",
                    f"link without .md extension (majority style: with .md): {url!r}",
                    line_no,
                    severity="warning",
                )
            )
    else:
        for line_no, url in with_ext:
            issues.append(
                Issue(
                    "links-md-ext",
                    f"link with .md extension (majority style: without .md): {url!r}",
                    line_no,
                    severity="warning",
                )
            )
    
    return issues


def check_images_external(
    path: Path, text: str, docs_dir: Path, site_domain: str
) -> list[Issue]:
    """Detect images not stored locally (external URL or absolute URL to site domain)."""
    issues: list[Issue] = []
    body_front, body = split_front_matter(text)
    cleaned = strip_code_blocks_simple(body)
    
    def _classify(url: str, line_no: int, kind: str) -> None:
        url = url.strip()
        url = re.sub(r'\s+"[^"]*"$', "", url)
        
        if not url.startswith(("http://", "https://")):
            return
        
        parsed = urlparse(url)
        host = parsed.netloc.lower()
        
        if host == site_domain or host.endswith("." + site_domain):
            suggestion = _abs_resource_to_relative(docs_dir, path, url)
            hint = f" -> suggested: {suggestion!r}" if suggestion else ""
            issues.append(
                Issue(
                    "images-external",
                    f"image as absolute URL to the site (use a relative path): {url!r}{hint}",
                    line_no,
                )
            )
        else:
            issues.append(
                Issue(
                    "images-external",
                    f"image hosted outside the site (must be stored locally): {url!r}",
                    line_no,
                )
            )
    
    for m in MD_IMAGE_RE.finditer(cleaned):
        line_no = cleaned[: m.start()].count("\n") + 1
        _classify(m.group(2), line_no, "md")
    
    for m in IMG_SRC_RE.finditer(cleaned):
        line_no = cleaned[: m.start()].count("\n") + 1
        _classify(m.group(1), line_no, "img")
    
    return issues


def check_images(path: Path, text: str, docs_dir: Path) -> list[Issue]:
    """Check for missing image files."""
    issues: list[Issue] = []
    body_front, body = split_front_matter(text)
    cleaned = strip_code_blocks_simple(body)
    
    for m in MD_IMAGE_RE.finditer(cleaned):
        url = m.group(2).strip()
        url = re.sub(r'\s+"[^"]*"$', "", url)
        
        if not url or url.startswith(("http://", "https://", "data:", "mailto:")):
            continue
        
        line_no = cleaned[: m.start()].count("\n") + 1
        
        if not _resource_exists(docs_dir, path, url):
            issues.append(Issue("images-missing", f"image not found: {url!r}", line_no))
    
    for m in IMG_SRC_RE.finditer(cleaned):
        url = m.group(1).strip()
        
        if not url or url.startswith(("http://", "https://", "data:")):
            continue
        
        line_no = cleaned[: m.start()].count("\n") + 1
        
        if not _resource_exists(docs_dir, path, url):
            issues.append(Issue("images-missing", f"<img> image not found: {url!r}", line_no))
    
    return issues


def check_frontmatter(path: Path, text: str) -> list[Issue]:
    """Check for presence of `path:` key in YAML front-matter for translated docs."""
    if "doc" not in path.parts:
        return []
    
    issues: list[Issue] = []
    fm, _body = split_front_matter(text)
    
    if not fm:
        return [Issue("frontmatter", "missing YAML front-matter (no `path:` key)", 1)]
    
    data = parse_front_matter(fm)
    if "path" not in data:
        issues.append(Issue("frontmatter", "`path:` key missing from front-matter", 1))
    
    return issues


def check_placeholders(path: Path, text: str) -> list[Issue]:
    """Check for placeholder/unfinished text."""
    issues: list[Issue] = []
    _, body = split_front_matter(text)
    cleaned = strip_code_blocks_simple(body)
    
    for line_no, line in enumerate(cleaned.splitlines(), start=1):
        for pat in PLACEHOLDER_PATTERNS:
            for m in pat.finditer(line):
                issues.append(
                    Issue(
                        "placeholders",
                        f"placeholder / unfinished text: {m.group(0)!r}",
                        line_no,
                        severity="warning",
                    )
                )
    
    return issues


def check_whitespace(path: Path, text: str) -> list[Issue]:
    """Check for trailing whitespace and multiple blank lines at EOF."""
    issues: list[Issue] = []
    lines = text.splitlines()
    
    for line_no, line in enumerate(lines, start=1):
        if line != line.rstrip():
            issues.append(
                Issue(
                    "whitespace",
                    "trailing whitespace",
                    line_no,
                    severity="warning",
                )
            )
    
    trailing_blank = 0
    for line in reversed(lines):
        if line.strip() == "":
            trailing_blank += 1
        else:
            break
    
    if trailing_blank > 1:
        issues.append(
            Issue(
                "whitespace",
                f"{trailing_blank} consecutive blank lines at end of file",
                len(lines),
                severity="warning",
            )
        )
    
    return issues


def collect_md_by_lang(docs_dir: Path) -> dict[str, dict[str, Path]]:
    """Return {lang: {filename: path}} for the doc/ subdirectory."""
    result: dict[str, dict[str, Path]] = {}
    doc_dir = docs_dir / "doc"
    
    if not doc_dir.is_dir():
        return result
    
    for lang_dir in sorted(doc_dir.iterdir()):
        if not lang_dir.is_dir() or lang_dir.name.startswith("."):
            continue
        
        files: dict[str, Path] = {}
        for md in lang_dir.rglob("*.md"):
            rel = md.relative_to(lang_dir).as_posix()
            files[rel] = md
        
        if files:
            result[lang_dir.name] = files
    
    return result


def check_i18n(docs_dir: Path, ref_lang: str) -> list[Issue]:
    """Check translation consistency across languages."""
    issues: list[Issue] = []
    by_lang = collect_md_by_lang(docs_dir)
    
    if ref_lang not in by_lang:
        return issues
    
    ref_files = set(by_lang[ref_lang])
    
    for lang, files in sorted(by_lang.items()):
        if lang == ref_lang:
            continue
        
        names = set(files)
        missing = sorted(ref_files - names)
        extra = sorted(names - ref_files)
        
        for name in missing:
            issues.append(
                Issue(
                    "i18n",
                    f"missing translation vs {ref_lang}: {lang}/{name}",
                    0,
                )
            )
        
        for name in extra:
            issues.append(
                Issue(
                    "i18n",
                    f"file with no equivalent in {ref_lang}: {lang}/{name}",
                    0,
                    severity="warning",
                )
            )
    
    return issues


# =============================================================================
# FIX FUNCTIONS (Auto-fix Mode)
# =============================================================================

def _local_name_for(url: str) -> str:
    """Generate a local filename for an external image URL."""
    m = WP_RE.search(url)
    if m:
        name = m.group("name").split("?")[0]
        return f"wp-{m.group('y')}-{m.group('m')}-{name}"
    
    m = GH_RE.search(url)
    if m:
        return f"gh-{m.group('uuid')}.png"
    
    m = BMC_RE.search(url)
    if m:
        return f"buymeacoffee-{m.group('name').split('?')[0]}"
    
    base = url.split("/")[-1].split("?")[0]
    return f"ext-{base}"


def _unique_local_path(out_dir: Path, name: str) -> Path:
    """Generate a unique path for a local file, appending -1, -2, etc. if needed."""
    base = out_dir / name
    if not base.exists():
        return base
    
    stem, dot, ext = name.rpartition(".")
    i = 1
    while True:
        cand = out_dir / f"{stem}-{i}{dot}{ext}"
        if not cand.exists():
            return cand
        i += 1


def _resolve_external_local(out_dir: Path, url: str) -> str | None:
    """Return '/images/<name>' if a local file exists for this external URL."""
    name = _local_name_for(url)
    
    if (out_dir / name).exists():
        return f"/images/{name}"
    
    stem, dot, ext = name.rpartition(".")
    i = 1
    if (out_dir / f"{stem}-{i}{dot}{ext}").exists():
        return f"/images/{stem}-{i}{dot}{ext}"
    
    return None


def _fetch(url: str, timeout: int = 30) -> bytes:
    """Fetch content from a URL."""
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    return urllib.request.urlopen(req, timeout=timeout).read()


def _wayback(url: str) -> str | None:
    """Try to find a Wayback Machine snapshot for a URL."""
    api = "https://archive.org/wayback/available?url=" + urllib.request.quote(url, safe="")
    try:
        req = urllib.request.Request(api, headers={"User-Agent": UA})
        data = json.loads(urllib.request.urlopen(req, timeout=25).read())
        snap = data.get("archived_snapshots", {}).get("closest", {})
        return snap.get("url") if snap.get("available") else None
    except Exception:
        return None


def _fetch_to_local(url: str, out_dir: Path, allow_network: bool) -> Path | None:
    """Download an external image to out_dir if not already present.
    
    Returns the absolute local Path, or None if it could not be fetched.
    Honors allow_network=False (only reuse existing files).
    """
    if url in _FETCH_CACHE:
        return _FETCH_CACHE[url]
    
    local = _resolve_external_local(out_dir, url)
    if local:
        p = out_dir.parent / local.lstrip("/")  # docs/images/<name>
        _FETCH_CACHE[url] = p
        return p
    
    if not allow_network:
        return None
    
    name = _local_name_for(url)
    data: bytes | None = None
    candidates = [url]
    
    if url.startswith("https://qualcoder.wordpress.com/") and "?" in url:
        candidates.append(url.split("?", 1)[0])
    
    for cand in candidates:
        try:
            data = _fetch(cand)
            break
        except Exception:
            continue
    
    if data is None:
        wb = _wayback(url.split("?", 1)[0])
        if wb:
            try:
                data = _fetch(wb)
            except Exception:
                data = None
    
    if data is None:
        return None
    
    target = _unique_local_path(out_dir, name)
    target.write_bytes(data)
    _FETCH_CACHE[url] = target
    return target


def fix_frontmatter(text: str, docs_dir: Path, current_file: Path) -> tuple[str, int]:
    """Add the `path:` front-matter key to translated docs under doc/<lang>/."""
    lang = _lang_of_file(docs_dir, current_file)
    if lang is None:
        return text, 0
    
    try:
        rel = current_file.relative_to(docs_dir / "doc" / lang)
    except ValueError:
        return text, 0
    
    path_value = rel.as_posix()
    if path_value.endswith(".md"):
        path_value = path_value[:-3]
    
    fm, body = split_front_matter(text)
    if fm:
        data = parse_front_matter(fm)
        if "path" in data:
            return text, 0  # already present
        
        # Insert `path:` inside the existing YAML block
        lines = text.splitlines()
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                lines.insert(i, f"path: {path_value}")
                return "\n".join(lines), 1
        return text, 0  # malformed front-matter
    else:
        # No front-matter: prepend one
        return f"---\npath: {path_value}\n---\n\n{text}", 1


def fix_whitespace(text: str) -> tuple[str, int]:
    """Remove trailing whitespace and collapse multiple trailing blank lines."""
    count = 0
    lines = text.splitlines()
    new_lines: list[str] = []
    
    for line in lines:
        if line != line.rstrip():
            count += 1
        new_lines.append(line.rstrip())
    
    # Collapse trailing blank lines
    while len(new_lines) > 1 and new_lines[-1] == "" and new_lines[-2] == "":
        new_lines.pop()
        count += 1
    
    # Preserve final newline
    had_final_newline = text.endswith("\n")
    new_text = "\n".join(new_lines)
    if had_final_newline:
        new_text += "\n"
    
    return new_text, count


def _rewrite_img_in_line(line: str, line_no: int) -> tuple[str, int, list[str]]:
    """Rewrite all <img ...> tags in a single line to Markdown syntax."""
    errors: list[str] = []
    count = 0
    
    def repl(m: re.Match) -> str:
        nonlocal count
        tag = m.group(0)
        attrs = dict(ATTR_RE.findall(tag))
        src = attrs.get("src")
        if not src:
            errors.append(f"line {line_no}: <img> without src, left untouched: {tag!r}")
            return tag
        alt = attrs.get("alt", "")
        count += 1
        return f"![{alt}]({src})"
    
    new_line = IMG_TAG_RE.sub(repl, line)
    return new_line, count, errors


def fix_img_tags(text: str) -> tuple[str, int, list[str]]:
    """Convert <img> HTML tags to ![alt](src) Markdown syntax."""
    errors: list[str] = []
    cleaned, code_mask = strip_code_blocks(text)
    
    if not IMG_TAG_RE.search(cleaned):
        return text, 0, errors
    
    lines = text.splitlines()
    new_lines: list[str] = []
    count = 0
    
    for idx, line in enumerate(lines):
        if code_mask[idx]:
            new_lines.append(line)
            continue
        if "<img" not in line.lower():
            new_lines.append(line)
            continue
        new_line, n, errs = _rewrite_img_in_line(line, idx + 1)
        new_lines.append(new_line)
        count += n
        errors.extend(errs)
    
    return "\n".join(new_lines), count, errors


def _rewrite_links_in_line(
    line: str, docs_dir: Path, current_file: Path, site_domain: str
) -> tuple[str, int]:
    """Rewrite internal absolute links to relative paths in a single line."""
    count = 0
    
    def repl(m: re.Match) -> str:
        nonlocal count
        label = m.group(1)
        url = m.group(2).strip()
        title_match = re.search(r'\s+"([^"]*)"$', url)
        title = title_match.group(1) if title_match else None
        url_clean = re.sub(r'\s+"[^"]*"$', "", url)
        
        if not _is_internal_absolute(url_clean, site_domain):
            return m.group(0)
        
        suggestion = _abs_to_relative_target(docs_dir, current_file, url_clean)
        if not suggestion:
            return m.group(0)
        
        count += 1
        if title:
            return f"[{label}]({suggestion} \"{title}\")"
        return f"[{label}]({suggestion})"
    
    new_line = MD_LINK_RE.sub(repl, line)
    return new_line, count


def fix_links_absolute(
    text: str, docs_dir: Path, current_file: Path, site_domain: str
) -> tuple[str, int]:
    """Rewrite internal absolute links to relative paths."""
    count = 0
    cleaned, code_mask = strip_code_blocks(text)
    
    if not MD_LINK_RE.search(cleaned):
        return text, 0
    
    lines = text.splitlines()
    new_lines: list[str] = []
    
    for idx, line in enumerate(lines):
        if code_mask[idx] or "[" not in line:
            new_lines.append(line)
            continue
        new_line, n = _rewrite_links_in_line(line, docs_dir, current_file, site_domain)
        new_lines.append(new_line)
        count += n
    
    return "\n".join(new_lines), count


def _rewrite_images_in_line(
    line: str, docs_dir: Path, current_file: Path, site_domain: str
) -> tuple[str, int]:
    """Rewrite absolute image URLs (to site domain) to relative paths in a single line."""
    count = 0
    
    def repl(m: re.Match) -> str:
        nonlocal count
        alt = m.group(1)
        url = m.group(2).strip()
        title_match = re.search(r'\s+"([^"]*)"$', url)
        title = title_match.group(1) if title_match else None
        url_clean = re.sub(r'\s+"[^"]*"$', "", url)
        
        if not _is_internal_absolute(url_clean, site_domain):
            return m.group(0)
        
        suggestion = _abs_resource_to_relative(docs_dir, current_file, url_clean)
        if not suggestion:
            return m.group(0)
        
        count += 1
        if title:
            return f"![{alt}]({suggestion} \"{title}\")"
        return f"![{alt}]({suggestion})"
    
    new_line = MD_IMAGE_RE.sub(repl, line)
    return new_line, count


def fix_images_absolute(
    text: str, docs_dir: Path, current_file: Path, site_domain: str
) -> tuple[str, int]:
    """Rewrite absolute image URLs (to the site domain) to relative paths."""
    count = 0
    cleaned, code_mask = strip_code_blocks(text)
    
    if not MD_IMAGE_RE.search(cleaned):
        return text, 0
    
    lines = text.splitlines()
    new_lines: list[str] = []
    
    for idx, line in enumerate(lines):
        if code_mask[idx] or "![" not in line:
            new_lines.append(line)
            continue
        new_line, n = _rewrite_images_in_line(line, docs_dir, current_file, site_domain)
        new_lines.append(new_line)
        count += n
    
    return "\n".join(new_lines), count


def _normalize_md_ext_in_line(
    line: str, docs_dir: Path, current_file: Path, with_ext: bool
) -> tuple[str, int]:
    """Normalize .md extension in relative links in a single line."""
    count = 0
    
    def repl(m: re.Match) -> str:
        nonlocal count
        label = m.group(1)
        url = m.group(2).strip()
        title_match = re.search(r'\s+"([^"]*)"$', url)
        title = title_match.group(1) if title_match else None
        url_clean = re.sub(r'\s+"[^"]*"$', "", url)
        
        if not url_clean or url_clean.startswith("#"):
            return m.group(0)
        if url_clean.startswith(("http://", "https://", "mailto:")):
            return m.group(0)
        
        target, frag = _split_url_fragment(url_clean)
        if not target:
            return m.group(0)
        
        resolved = _resolve_md_target(docs_dir, current_file, url_clean)
        if resolved is None or resolved.suffix != ".md":
            return m.group(0)
        
        # Only rewrite if there is an actual change to make
        if with_ext and not target.endswith(".md"):
            new_target = target + ".md"
            count += 1
        elif not with_ext and target.endswith(".md"):
            new_target = target[:-3]
            count += 1
        else:
            return m.group(0)
        
        new_url = new_target
        if frag:
            new_url += f"#{frag}"
        if title:
            new_url += f' "{title}"'
        return f"[{label}]({new_url})"
    
    new_line = MD_LINK_RE.sub(repl, line)
    return new_line, count


def fix_links_md_ext(
    text: str, docs_dir: Path, current_file: Path, with_ext: bool
) -> tuple[str, int]:
    """Normalize relative .md link targets to the majority style."""
    count = 0
    cleaned, code_mask = strip_code_blocks(text)
    
    if not MD_LINK_RE.search(cleaned):
        return text, 0
    
    lines = text.splitlines()
    new_lines: list[str] = []
    
    for idx, line in enumerate(lines):
        if code_mask[idx] or "[" not in line:
            new_lines.append(line)
            continue
        new_line, n = _normalize_md_ext_in_line(line, docs_dir, current_file, with_ext)
        new_lines.append(new_line)
        count += n
    
    return "\n".join(new_lines), count


def _rewrite_external_in_line(
    line: str,
    line_no: int,
    images_out: Path,
    allow_network: bool,
    delay: float,
) -> tuple[str, int, list[str]]:
    """Rewrite external image URLs to local /images/<name> in a single line."""
    warnings: list[str] = []
    count = 0
    
    def repl(m: re.Match) -> str:
        nonlocal count
        url = m.group(0)
        local = _fetch_to_local(url, images_out, allow_network=allow_network)
        
        if local is None:
            warnings.append(
                f"line {line_no}: external image not local & not fetchable, left as-is: {url!r}"
            )
            return url
        
        rel = "/images/" + local.name
        count += 1
        return rel
    
    new_line = EXT_URL_RE.sub(repl, line)
    if count and allow_network and delay:
        time.sleep(delay)
    
    return new_line, count, warnings


def fix_images_external(
    text: str,
    images_out: Path,
    allow_network: bool,
    delay: float,
) -> tuple[str, int, list[str]]:
    """Download external images and rewrite their URLs to local /images/<name>."""
    warnings: list[str] = []
    cleaned, code_mask = strip_code_blocks(text)
    
    if not EXT_URL_RE.search(cleaned):
        return text, 0, warnings
    
    lines = text.splitlines()
    new_lines: list[str] = []
    count = 0
    
    for idx, line in enumerate(lines):
        if code_mask[idx] or "https://" not in line:
            new_lines.append(line)
            continue
        new_line, n, warns = _rewrite_external_in_line(
            line, idx + 1, images_out, allow_network, delay
        )
        new_lines.append(new_line)
        count += n
        warnings.extend(warns)
    
    return "\n".join(new_lines), count, warnings


def fix_headings(text: str) -> tuple[str, int]:
    """Fix heading structure: ensure only one H1 (#), replace subsequent H1s with H2.
    
    Rules:
    - Keep only the first H1 (#), replace others with H2 (##)
    - Do NOT modify other heading levels (H3-H6)
    - Do NOT fix level skips
    
    Returns (new_text, count_of_fixes).
    """
    lines = text.splitlines()
    new_lines: list[str] = []
    count = 0
    
    # Track if we've seen the first H1
    h1_found = False
    
    for line in lines:
        # Check if this line is a heading
        m = re.match(r"^(#{1,6})\s+(.+?)\s*#*\s*$", line)
        
        if m:
            level = len(m.group(1))
            title = m.group(2)
            
            # Only process H1 (level 1)
            if level == 1:
                if h1_found:
                    # Replace with H2
                    new_line = f"## {title}"
                    new_lines.append(new_line)
                    count += 1
                    continue
                else:
                    # Keep the first H1
                    h1_found = True
            # For other levels (2-6), keep as-is
        
        new_lines.append(line)
    
    # Preserve final newline
    had_final_newline = text.endswith("\n")
    new_text = "\n".join(new_lines)
    if had_final_newline and not new_text.endswith("\n"):
        new_text += "\n"
    
    return new_text, count


def majority_md_ext(docs_dir: Path) -> bool:
    """Return True if the majority of relative .md links use the .md suffix."""
    with_ext = 0
    without_ext = 0
    
    for md_file in docs_dir.rglob("*.md"):
        try:
            text = md_file.read_text(encoding="utf-8")
        except OSError:
            continue
        
        _, body = split_front_matter(text)
        cleaned, _ = strip_code_blocks(body)
        
        for m in MD_LINK_RE.finditer(cleaned):
            url = m.group(2).strip()
            url = re.sub(r'\s+"[^"]*"$', "", url)
            
            if not url or url.startswith("#"):
                continue
            if url.startswith(("http://", "https://", "mailto:")):
                continue
            
            target, _frag = _split_url_fragment(url)
            if not target:
                continue
            
            resolved = _resolve_md_target(docs_dir, md_file, url)
            if resolved is None or resolved.suffix != ".md":
                continue
            
            if target.endswith(".md"):
                with_ext += 1
            else:
                without_ext += 1
    
    return with_ext >= without_ext


# =============================================================================
# ORCHESTRATION
# =============================================================================

CHECKS = {
    "html": check_html,
    "headings": check_headings,
    "links-absolute": check_links_absolute,
    "links-broken": check_links_broken,
    "anchors": check_anchors,
    "links-md-ext": check_links_md_ext,
    "images-missing": check_images,
    "images-external": check_images_external,
    "frontmatter": check_frontmatter,
    "placeholders": check_placeholders,
    "whitespace": check_whitespace,
}

CROSS_CHECKS = {
    "i18n": check_i18n,
}

FIX_NAMES = (
    "whitespace",
    "img",
    "headings",
    "links-absolute",
    "images-absolute",
    "links-md-ext",
    "frontmatter",
    "images-external",
)

FIX_FUNCTIONS = {
    "whitespace": fix_whitespace,
    "img": fix_img_tags,
    "links-absolute": fix_links_absolute,
    "images-absolute": fix_images_absolute,
    "links-md-ext": fix_links_md_ext,
    "frontmatter": fix_frontmatter,
    "images-external": fix_images_external,
    "headings": fix_headings,
}


def run_checks(
    docs_dir: Path,
    site_domain: str,
    ref_lang: str,
    enabled: set[str],
    quiet: bool,
) -> tuple[int, int, dict[str, list[Issue]], list[Issue]]:
    """Run all enabled checks. Returns (error_count, warning_count, per_file_issues, cross_issues)."""
    md_files = sorted(p for p in docs_dir.rglob("*.md"))
    error_count = 0
    warning_count = 0
    per_file: dict[str, list[Issue]] = {}
    cross_issues: list[Issue] = []
    
    for md_file in md_files:
        rel = md_file.relative_to(docs_dir).as_posix()
        try:
            text = md_file.read_text(encoding="utf-8")
        except OSError as e:
            per_file[rel] = [Issue("read", f"could not read file: {e}", 1)]
            error_count += 1
            continue
        
        file_issues: list[Issue] = []
        for name, fn in CHECKS.items():
            if name not in enabled:
                continue
            try:
                if name == "links-absolute":
                    file_issues += fn(md_file, text, docs_dir, site_domain)
                elif name == "images-external":
                    file_issues += fn(md_file, text, docs_dir, site_domain)
                elif name in ("links-broken", "links-md-ext", "images-missing", "anchors"):
                    file_issues += fn(md_file, text, docs_dir)
                else:
                    file_issues += fn(md_file, text)
            except Exception as e:  # noqa: BLE001
                file_issues.append(Issue(name, f"check crashed: {e}", 1))
        
        file_errors = [i for i in file_issues if i.severity == "error"]
        file_warnings = [i for i in file_issues if i.severity == "warning"]
        
        if file_issues and (file_errors or not quiet):
            per_file[rel] = file_issues
        
        error_count += len(file_errors)
        warning_count += len(file_warnings)
    
    if "i18n" in enabled:
        cross_issues = check_i18n(docs_dir, ref_lang)
        error_count += sum(1 for i in cross_issues if i.severity == "error")
        warning_count += sum(1 for i in cross_issues if i.severity == "warning")
    
    return error_count, warning_count, per_file, cross_issues


def _md_inline(text: str) -> str:
    """Escape characters that could break a Markdown table cell."""
    return text.replace("|", "\\|").replace("\n", " ")


def render_report(
    docs_dir: Path,
    site_domain: str,
    ref_lang: str,
    enabled: set[str],
    error_count: int,
    warning_count: int,
    per_file: dict[str, list[Issue]],
    cross_issues: list[Issue],
    strict: bool,
) -> str:
    """Render a Markdown report of all issues found."""
    lines: list[str] = []
    lines.append("# Markdown Quality Report")
    lines.append("")
    
    generated = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    lines.append(f"Generated: {generated}")
    lines.append("")
    
    lines.append("## Configuration")
    lines.append("")
    lines.append(f"- **Docs directory:** `{docs_dir}`")
    lines.append(f"- **Internal site domain:** `{site_domain}`")
    lines.append(f"- **Reference language (i18n):** `{ref_lang}`")
    lines.append(f"- **Active checks:** {', '.join(sorted(enabled)) if enabled else 'none'}")
    lines.append("")
    
    lines.append("## Summary")
    lines.append("")
    status = "FAIL" if (error_count or (strict and warning_count)) else "PASS"
    lines.append(f"- **Status:** {status}")
    lines.append(f"- **Errors:** {error_count}")
    lines.append(f"- **Warnings:** {warning_count}")
    lines.append(f"- **Files with issues:** {len(per_file)}")
    lines.append("")
    
    # Counts per check
    all_issues = [i for issues in per_file.values() for i in issues] + cross_issues
    by_check: dict[str, dict[str, int]] = {}
    for iss in all_issues:
        by_check.setdefault(iss.check, {"error": 0, "warning": 0})
        by_check[iss.check][iss.severity] += 1
    
    if by_check:
        lines.append("### Issues by check")
        lines.append("")
        lines.append("| Check | Errors | Warnings |")
        lines.append("|---|---:|---:|")
        for check in sorted(by_check):
            lines.append(
                f"| `{_md_inline(check)}` "
                f"| {by_check[check]['error']} | {by_check[check]['warning']} |"
            )
        lines.append("")
    
    # Per-file details
    if per_file:
        lines.append("## Files")
        lines.append("")
        lines.append("| File | Errors | Warnings |")
        lines.append("|---|---:|---:|")
        for rel in sorted(per_file):
            errs = sum(1 for i in per_file[rel] if i.severity == "error")
            warns = sum(1 for i in per_file[rel] if i.severity == "warning")
            lines.append(f"| `{_md_inline(rel)}` | {errs} | {warns} |")
        lines.append("")
        
        lines.append("## Details")
        lines.append("")
        for rel in sorted(per_file):
            issues = per_file[rel]
            errs = [i for i in issues if i.severity == "error"]
            warns = [i for i in issues if i.severity == "warning"]
            lines.append(f"### `{_md_inline(rel)}`")
            lines.append("")
            lines.append(f"- Errors: {len(errs)}")
            lines.append(f"- Warnings: {len(warns)}")
            lines.append("")
            if issues:
                lines.append("| Severity | Line | Check | Message |")
                lines.append("|---|---:|---|---|")
                for iss in issues:
                    sev = "error" if iss.severity == "error" else "warning"
                    loc = str(iss.line) if iss.line > 0 else "-"
                    lines.append(
                        f"| {sev} | {loc} | `{_md_inline(iss.check)}` "
                        f"| {_md_inline(iss.message)} |"
                    )
                lines.append("")
    
    # Cross-file (i18n) details
    if cross_issues:
        lines.append("## Translation consistency (`docs/doc/`)")
        lines.append("")
        lines.append("| Severity | Check | Message |")
        lines.append("|---|---|---|")
        for iss in cross_issues:
            sev = "error" if iss.severity == "error" else "warning"
            lines.append(
                f"| {sev} | `{_md_inline(iss.check)}` | {_md_inline(iss.message)} |"
            )
        lines.append("")
    
    lines.append("---")
    lines.append("")
    lines.append(f"Result: **{status}**")
    lines.append("")
    
    return "\n".join(lines)


def fix_file(
    text: str,
    docs_dir: Path,
    current_file: Path,
    site_domain: str,
    with_ext: bool,
    enabled: set[str],
    images_out: Path,
    allow_network: bool,
    delay: float,
) -> tuple[str, dict[str, int], list[str]]:
    """Apply all enabled fixes to a file's content. Returns (new_text, counts, errors)."""
    counts = {k: 0 for k in FIX_NAMES}
    errors: list[str] = []
    
    if "frontmatter" in enabled:
        text, n = fix_frontmatter(text, docs_dir, current_file)
        counts["frontmatter"] = n
    
    if "headings" in enabled:
        text, n = fix_headings(text)
        counts["headings"] = n
    
    if "whitespace" in enabled:
        text, n = fix_whitespace(text)
        counts["whitespace"] = n
    
    if "img" in enabled:
        text, n, errs = fix_img_tags(text)
        counts["img"] = n
        errors.extend(errs)
    
    if "links-absolute" in enabled:
        text, n = fix_links_absolute(text, docs_dir, current_file, site_domain)
        counts["links-absolute"] = n
    
    if "images-absolute" in enabled:
        text, n = fix_images_absolute(text, docs_dir, current_file, site_domain)
        counts["images-absolute"] = n
    
    if "links-md-ext" in enabled:
        text, n = fix_links_md_ext(text, docs_dir, current_file, with_ext)
        counts["links-md-ext"] = n
    
    if "images-external" in enabled:
        text, n, warns = fix_images_external(text, images_out, allow_network, delay)
        counts["images-external"] = n
        errors.extend(warns)
    
    return text, counts, errors


# =============================================================================
# CLI
# =============================================================================

def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser with simplified flags."""
    parser = argparse.ArgumentParser(
        description="Unified Markdown quality tool: use --check to verify, --fix to correct.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    # Mode selection
    parser.add_argument(
        "--check",
        action="store_true",
        help="Run verification and generate a Markdown report (default: enabled if no --fix).",
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Run auto-fix on safe issues. Use with --check to run both.",
    )
    
    # Common options
    parser.add_argument(
        "--docs-dir", type=Path, default=Path("docs"),
        help="Docs root directory (default: docs).",
    )
    parser.add_argument(
        "--site-domain", default=DEFAULT_SITE_DOMAIN,
        help="Domain considered internal (default: %s)." % DEFAULT_SITE_DOMAIN,
    )
    parser.add_argument(
        "--ref-lang", default=DEFAULT_REF_LANG,
        help="Reference language for i18n consistency (default: %s)." % DEFAULT_REF_LANG,
    )
    
    # Check-specific options
    parser.add_argument(
        "--only", nargs="+",
        help="Run only these checks/fixes (space-separated names).",
    )
    parser.add_argument(
        "--skip", nargs="+",
        help="Checks/fixes to ignore (space-separated names).",
    )
    parser.add_argument(
        "--quiet", "-q", action="store_true",
        help="Only show files that have errors (check mode).",
    )
    parser.add_argument(
        "--strict", action="store_true",
        help="Warnings also cause failure (exit 1) in check mode.",
    )
    parser.add_argument(
        "--no-report", action="store_true",
        help="Do not print the Markdown report (still sets exit code).",
    )
    
    # Fix-specific options
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would change without writing any file (fix mode).",
    )
    parser.add_argument(
        "--md-ext-style",
        choices=["auto", "with", "without"],
        default="auto",
        help="Target .md extension style for relative links (default: auto).",
    )
    parser.add_argument(
        "--images-out",
        type=Path,
        default=None,
        help="Directory for downloaded external images (default: <docs-dir>/images).",
    )
    parser.add_argument(
        "--no-network",
        action="store_true",
        help="Disable downloading external images; only rewrite URLs whose local file already exists.",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.3,
        help="Seconds to wait between external image downloads (default: 0.3).",
    )
    
    return parser


def run_check(
    docs_dir: Path,
    site_domain: str,
    ref_lang: str,
    enabled: set[str],
    quiet: bool,
    no_report: bool,
    strict: bool,
) -> tuple[int, int, dict[str, list[Issue]], list[Issue]]:
    """Run verification checks and optionally print report."""
    error_count, warning_count, per_file, cross_issues = run_checks(
        docs_dir, site_domain, ref_lang, enabled, quiet
    )
    
    exit_code = 1 if error_count or (strict and warning_count) else 0
    
    if not no_report:
        report = render_report(
            docs_dir,
            site_domain,
            ref_lang,
            enabled,
            error_count,
            warning_count,
            per_file,
            cross_issues,
            strict,
        )
        print(report)
    
    return exit_code, error_count, warning_count, per_file, cross_issues


def run_fix(
    docs_dir: Path,
    site_domain: str,
    enabled: set[str],
    md_ext_style: str,
    images_out: Path,
    dry_run: bool,
    no_network: bool,
    delay: float,
) -> tuple[int, bool]:
    """Run auto-fix on files. Returns (exit_code, had_error)."""
    images_out_resolved = images_out.resolve() if images_out else (docs_dir / "images")
    if "images-external" in enabled:
        images_out_resolved.mkdir(parents=True, exist_ok=True)
    
    # Determine .md extension style
    if md_ext_style == "auto":
        with_ext = majority_md_ext(docs_dir)
    else:
        with_ext = md_ext_style == "with"
    
    apply = not dry_run
    allow_network = apply and not no_network
    mode = "APPLY" if apply else "DRY-RUN"
    
    print(f"Markdown quality fixer [{mode}]")
    print(f"  Docs directory: {docs_dir}")
    print(f"  Internal site domain: {site_domain}")
    print(f"  .md extension style: {'with .md' if with_ext else 'without .md'}")
    print(f"  Images out dir: {images_out_resolved}")
    print(f"  Network download: {'enabled' if allow_network else 'disabled (reuse local only)'}")
    print(f"  Active fixes: {', '.join(sorted(enabled)) if enabled else 'none'}")
    print()
    
    total_counts = {k: 0 for k in FIX_NAMES}
    files_changed = 0
    total_errors = 0
    had_error = False
    
    md_files = sorted(p for p in docs_dir.rglob("*.md"))
    for md_file in md_files:
        rel = md_file.relative_to(docs_dir).as_posix()
        try:
            original = md_file.read_text(encoding="utf-8")
        except OSError as e:
            print(f"  ERROR reading {rel}: {e}", file=sys.stderr)
            had_error = True
            continue
        
        new_text, counts, errors = fix_file(
            original, docs_dir, md_file, site_domain, with_ext, enabled,
            images_out_resolved, allow_network, delay,
        )
        for k, v in counts.items():
            total_counts[k] += v
        total_errors += len(errors)
        
        if new_text != original:
            files_changed += 1
            print(f"### {rel}")
            for k, v in counts.items():
                if v:
                    print(f"  - {k}: {v} fix(es)")
            for err in errors:
                print(f"  - WARNING: {err}")
            if apply:
                md_file.write_text(new_text, encoding="utf-8")
        else:
            for err in errors:
                print(f"### {rel}")
                print(f"  - WARNING: {err}")
    
    print("\n" + "=" * 60)
    print("Summary:")
    print(f"  Files scanned: {len(md_files)}")
    print(f"  Files changed: {files_changed}")
    for k, v in sorted(total_counts.items()):
        print(f"  {k}: {v} fix(es)")
    print(f"  Warnings (untouched issues): {total_errors}")
    print("Result: " + ("DONE" if not had_error else "DONE with warnings"))
    
    return 1 if had_error else 0, had_error


def main(argv: list[str] | None = None) -> int:
    """Main entry point with simplified CLI."""
    parser = create_parser()
    args = parser.parse_args(argv)
    
    docs_dir = args.docs_dir.resolve()
    if not docs_dir.is_dir():
        print(f"Directory not found: {docs_dir}", file=sys.stderr)
        return 2
    
    # Determine mode
    do_check = args.check or (not args.fix)
    do_fix = args.fix
    
    # Prepare enabled checks/fixes
    all_items = set(CHECKS) | set(CROSS_CHECKS) | set(FIX_NAMES)
    if args.only:
        enabled = set(args.only) & all_items
    else:
        enabled = all_items
    enabled -= set(args.skip or [])
    
    # Split into check-enabled and fix-enabled
    check_enabled = enabled & (set(CHECKS) | set(CROSS_CHECKS))
    fix_enabled = enabled & set(FIX_NAMES)
    
    exit_code = 0
    
    # Run check if requested
    if do_check:
        check_exit, _, _, _, _ = run_check(
            docs_dir,
            args.site_domain,
            args.ref_lang,
            check_enabled,
            args.quiet,
            args.no_report,
            args.strict,
        )
        exit_code = check_exit
    
    # Run fix if requested
    if do_fix:
        fix_exit, had_error = run_fix(
            docs_dir,
            args.site_domain,
            fix_enabled,
            args.md_ext_style,
            args.images_out.resolve() if args.images_out else None,
            args.dry_run,
            args.no_network,
            args.delay,
        )
        if had_error:
            exit_code = 1
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
