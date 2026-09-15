#!/usr/bin/env python3
"""Quality check for Markdown files under docs/.

Emits a Markdown report (English, no emoji) to stdout. Redirect to a file to
save it:  python3 scripts/verify_quality.py > report.md

Checks performed (configurable):

Errors:
  --html              HTML tags detected (excluding comments and code blocks)
  --links-absolute    internal links written as absolute URLs to the site domain
  --links-broken      relative links whose target does not exist
  --images-missing    images (markdown or <img>) whose file does not exist
  --images-external   images not stored locally (external URL, or absolute URL
                      to the site domain instead of a relative path)
  --i18n              file-count consistency across languages (reference: "en")
  --frontmatter       presence of the `path:` key in the YAML front-matter

Warnings:
  --links-md-ext      inconsistency of the .md extension in relative links
  --anchors           anchors (#...) not found in the target file
  --placeholders      untranslated / placeholder text ("See page ...", TODO)
  --whitespace        trailing whitespace and multiple blank lines at EOF

By default all checks are active. No external dependencies (stdlib only).
Exit code: 0 if no errors, 1 otherwise (warnings alone do not fail, except
with --strict).
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse

# Site domain considered "internal". Absolute URLs to this domain must be
# rewritten as relative paths.
DEFAULT_SITE_DOMAIN = "qualcoder.org"

# Reference language for translation consistency.
DEFAULT_REF_LANG = "en"

# Placeholders / unfinished text left in English or not finalized.
PLACEHOLDER_PATTERNS = [
    re.compile(r"\bSee page\s*\.\.\.", re.IGNORECASE),
    re.compile(r"\bTODO\b"),
    re.compile(r"\bFIXME\b"),
    re.compile(r"\bTBD\b"),
    re.compile(r"\bXXX\b"),
]

# HTML tags: opening, closing or self-closing. Comments <!-- ... --> are
# handled separately (stripped before this regex runs).
HTML_TAG_RE = re.compile(r"</?[a-zA-Z][a-zA-Z0-9-]*(\s[^>]*?)?/?>")

# Markdown links and images.
MD_LINK_RE = re.compile(r"(?<!\!)\[([^\]]*)\]\(([^)]+?)\)")
MD_IMAGE_RE = re.compile(r"!\[([^\]]*)\]\(([^)]+?)\)")

# src attribute of an <img> tag.
IMG_SRC_RE = re.compile(r'<img\b[^>]*\bsrc\s*=\s*"([^"]+)"', re.IGNORECASE)

# YAML front-matter delimited by "---" lines.
FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*(?:\n|$)", re.DOTALL)


class Issue:
    """A detected problem. severity is 'error' or 'warning'."""

    def __init__(self, check: str, message: str, line: int, severity: str = "error"):
        self.check = check
        self.message = message
        self.line = line
        self.severity = severity

    def __repr__(self) -> str:
        return f"[{self.severity}] {self.check}: {self.message}"


def strip_code_blocks(text: str) -> str:
    """Return the text with fenced code blocks (``` or ~~~) replaced by blank
    lines, preserving line numbers."""
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


def strip_inline_code(text: str) -> str:
    """Mask inline code `...` (replace with spaces of the same length) to avoid
    HTML false positives while keeping line numbers intact."""
    def repl(m: re.Match) -> str:
        return " " * (m.end() - m.start())

    return re.sub(r"`[^`\n]+`", repl, text)


def strip_html_comments(text: str) -> str:
    """Mask HTML comments <!-- ... --> (replace with spaces)."""
    return re.sub(r"<!--.*?-->", lambda m: " " * (m.end() - m.start()), text, flags=re.DOTALL)


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


# --- Per-file checks ----------------------------------------------------------


def check_html(path: Path, text: str) -> list[Issue]:
    issues: list[Issue] = []
    body_front, body = split_front_matter(text)
    cleaned = strip_code_blocks(body)
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


def _is_internal_absolute(url: str, site_domain: str) -> bool:
    if url.startswith("#"):
        return False
    parsed = urlparse(url)
    if not parsed.scheme and not parsed.netloc:
        return False
    host = parsed.netloc.lower()
    return host == site_domain or host.endswith("." + site_domain)


def _abs_to_relative_target(docs_dir: Path, current_file: Path, url: str) -> str | None:
    """For an internal absolute URL, compute the suggested relative path from
    the current file to the resolved target. Returns None if not resolvable."""
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
    # Some absolute URLs omit the /doc/ segment (e.g. /de/2.3.-AI-Setup
    # actually resolves to docs/doc/de/2.3.-AI-Setup.md). Try with the doc/
    # prefix if the direct candidates failed and the path doesn't already
    # start with doc/.
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


def os_relpath(start: Path, target: Path) -> str:
    import os

    return os.path.relpath(target, start).replace(os.sep, "/")


def check_links_absolute(
    path: Path, text: str, docs_dir: Path, site_domain: str
) -> list[Issue]:
    issues: list[Issue] = []
    body_front, body = split_front_matter(text)
    cleaned = strip_code_blocks(body)
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


def _split_url_fragment(url: str) -> tuple[str, str]:
    if "#" in url:
        target, _, frag = url.partition("#")
        return target, frag
    return url, ""


def _resolve_md_target(
    docs_dir: Path, current_file: Path, url: str
) -> Path | None:
    """Resolve a relative link target to an existing .md file.
    Returns None if not found. Handles `folder/`, `file` and `file.md`."""
    target, _frag = _split_url_fragment(url)
    if not target:
        # Pure anchor link (#...) -> target is the current file.
        return current_file
    if target.startswith("http://") or target.startswith("https://") or target.startswith("mailto:"):
        return None  # external, not checked here
    base = current_file.parent
    candidate = (base / target).resolve()
    candidates = []
    if candidate.suffix == ".md":
        candidates.append(candidate)
    else:
        candidates.append(candidate.with_suffix(".md"))
        candidates.append(candidate / "index.md")
    for c in candidates:
        if c.exists():
            return c
    return None


def check_links_broken(path: Path, text: str, docs_dir: Path) -> list[Issue]:
    issues: list[Issue] = []
    body_front, body = split_front_matter(text)
    cleaned = strip_code_blocks(body)
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
    issues: list[Issue] = []
    body_front, body = split_front_matter(text)
    cleaned = strip_code_blocks(body)
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


def _slugify(heading: str) -> str:
    """Approximate MkDocs-compatible slug: lowercase, punctuation removed,
    spaces -> hyphens."""
    s = heading.strip().lower()
    s = re.sub(r"[`*_~]", "", s)
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"\s+", "-", s)
    return s.strip("-")


def collect_anchors(md_file: Path) -> set[str]:
    try:
        content = md_file.read_text(encoding="utf-8")
    except OSError:
        return set()
    _, body = split_front_matter(content)
    body = strip_code_blocks(body)
    anchors: set[str] = set()
    for line in body.splitlines():
        m = re.match(r"^\s{0,3}(#{1,6})\s+(.+?)\s*#*\s*$", line)
        if m:
            anchors.add(_slugify(m.group(2)))
    return anchors


def check_links_md_ext(path: Path, text: str, docs_dir: Path) -> list[Issue]:
    """Detect inconsistency: relative links to .md files sometimes with .md,
    sometimes without. Reports the minority style."""
    issues: list[Issue] = []
    body_front, body = split_front_matter(text)
    cleaned = strip_code_blocks(body)
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
    """Detect images not stored locally (external URL, or absolute URL to the
    site domain instead of a relative path)."""
    issues: list[Issue] = []
    body_front, body = split_front_matter(text)
    cleaned = strip_code_blocks(body)

    def _classify(url: str, line_no: int, kind: str) -> None:
        url = url.strip()
        url = re.sub(r'\s+"[^"]*"$', "", url)
        if not url.startswith(("http://", "https://")):
            return
        parsed = urlparse(url)
        host = parsed.netloc.lower()
        if host == site_domain or host.endswith("." + site_domain):
            suggestion = _abs_to_relative_resource(docs_dir, path, url)
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


def _abs_to_relative_resource(
    docs_dir: Path, current_file: Path, url: str
) -> str | None:
    """For an internal absolute URL pointing to a resource (image), compute the
    suggested relative path from the current file."""
    parsed = urlparse(url)
    target = unquote(parsed.path)
    if target.startswith("/"):
        # Absolute URL path from the site root = docs_dir root.
        candidate = (docs_dir / target.lstrip("/")).resolve()
    else:
        candidate = (current_file.parent / target).resolve()
    if not candidate.exists():
        return None
    rel = os_relpath(current_file.parent, candidate)
    if parsed.fragment:
        rel += f"#{parsed.fragment}"
    return rel


def check_images(path: Path, text: str, docs_dir: Path) -> list[Issue]:
    issues: list[Issue] = []
    body_front, body = split_front_matter(text)
    cleaned = strip_code_blocks(body)
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


def _resource_exists(docs_dir: Path, current_file: Path, url: str) -> bool:
    target, _frag = _split_url_fragment(url)
    if not target:
        return True
    # Strip a query string (e.g. ?w=473) which is not part of the path.
    target = target.split("?", 1)[0]
    # Absolute path from the site root (e.g. /images/x.png) resolves to
    # docs_dir/<path>; a relative path resolves from the file's directory.
    if target.startswith("/"):
        candidate = (docs_dir / target.lstrip("/")).resolve()
    else:
        candidate = (current_file.parent / target).resolve()
    return candidate.exists()


def check_frontmatter(path: Path, text: str) -> list[Issue]:
    # The `path:` front-matter key is a convention specific to the translated
    # docs under doc/<lang>/ (added by add_metadata.py). Other files
    # (about.md, blog/*, root pages) intentionally have no `path:` key, so we
    # do not report them.
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
    issues: list[Issue] = []
    _, body = split_front_matter(text)
    cleaned = strip_code_blocks(body)
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


# --- Cross-file checks (i18n) -------------------------------------------------


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


# --- Orchestration ------------------------------------------------------------


CHECKS = {
    "html": check_html,
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


def run_checks(
    docs_dir: Path,
    site_domain: str,
    ref_lang: str,
    enabled: set[str],
    quiet: bool,
) -> tuple[int, int, dict[str, list[Issue]], list[Issue]]:
    """Run all checks. Returns (error_count, warning_count, per_file_issues,
    cross_issues)."""
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
                elif name in ("links-broken", "links-md-ext", "images-missing"):
                    file_issues += fn(md_file, text, docs_dir)
                elif name == "anchors":
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
    """Escape characters that could break a Markdown table cell / inline."""
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
    import datetime

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

    # Counts per check.
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

    # Per-file details.
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

    # Cross-file (i18n) details.
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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Quality check for Markdown files under docs/."
    )
    parser.add_argument(
        "--docs-dir", type=Path, default=Path("docs"), help="Docs root directory (default: docs)."
    )
    parser.add_argument(
        "--site-domain", default=DEFAULT_SITE_DOMAIN, help="Domain considered internal."
    )
    parser.add_argument(
        "--ref-lang", default=DEFAULT_REF_LANG, help="Reference language for i18n consistency."
    )
    parser.add_argument(
        "--only", nargs="+", help="Run only these checks (space-separated names)."
    )
    parser.add_argument(
        "--skip", nargs="+", help="Checks to ignore (space-separated names)."
    )
    parser.add_argument(
        "--quiet", "-q", action="store_true", help="Only show files that have errors."
    )
    parser.add_argument(
        "--strict", action="store_true", help="Warnings also cause failure (exit 1)."
    )
    parser.add_argument(
        "--no-report", action="store_true", help="Do not print the Markdown report (still sets exit code)."
    )
    args = parser.parse_args(argv)

    docs_dir = args.docs_dir.resolve()
    if not docs_dir.is_dir():
        print(f"Directory not found: {docs_dir}", file=sys.stderr)
        return 2

    all_checks = set(CHECKS) | set(CROSS_CHECKS)
    if args.only:
        enabled = set(args.only) & all_checks
    else:
        enabled = set(all_checks)
    enabled -= set(args.skip or [])

    error_count, warning_count, per_file, cross_issues = run_checks(
        docs_dir, args.site_domain, args.ref_lang, enabled, args.quiet
    )

    exit_code = 1 if error_count or (args.strict and warning_count) else 0

    if not args.no_report:
        report = render_report(
            docs_dir,
            args.site_domain,
            args.ref_lang,
            enabled,
            error_count,
            warning_count,
            per_file,
            cross_issues,
            args.strict,
        )
        print(report)

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
