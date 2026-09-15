#!/usr/bin/env python3
"""Auto-fix safe Markdown quality issues under docs/.

Applies only corrections that have no side effects:
  1. trailing whitespace        -> rstrip each line
  2. trailing blank lines (EOF) -> collapse to a single trailing newline
  3. <img> HTML tags            -> Markdown image syntax ![alt](src)
  4. internal absolute links    -> relative links (to the site domain)
  5. absolute image URLs (site) -> relative paths (when the file exists)
  6. .md extension consistency  -> normalize relative .md link targets
  7. frontmatter path:         -> add the `path:` key to docs/doc/<lang>/*.md
                                (matches the add_metadata.py convention)

Dry run by default (prints a diff-like summary, writes nothing).
Use --apply to modify files in place. No external dependencies.

Exit code: 0 on success, 1 if any file could not be fixed cleanly (e.g. an
<img> without a parseable src/alt is left untouched and reported).
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse

# Shared logic with verify_quality.py. To keep this script self-contained,
# the helpers are duplicated here (stdlib only).

DEFAULT_SITE_DOMAIN = "qualcoder.org"

IMG_TAG_RE = re.compile(r"<img\b[^>]*?/?>", re.IGNORECASE)
ATTR_RE = re.compile(r'(\w[\w-]*)\s*=\s*"([^"]*)"', re.IGNORECASE)
MD_LINK_RE = re.compile(r"(?<!\!)\[([^\]]*)\]\(([^)]+?)\)")
MD_IMAGE_RE = re.compile(r"!\[([^\]]*)\]\(([^)]+?)\)")
FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*(?:\n|$)", re.DOTALL)

# Languages present under docs/doc/. A file under docs/doc/<lang>/ gets a
# `path:` front-matter key matching the add_metadata.py convention. Populated
# lazily on first run.
DOC_LANGS: set[str] | None = None


def split_front_matter(text: str) -> tuple[str, str]:
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


def discover_doc_langs(docs_dir: Path) -> set[str]:
    """Return the set of language directories under docs/doc/ (one level).
    Cached in the module-level DOC_LANGS."""
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


def strip_code_blocks(text: str) -> tuple[str, list[bool]]:
    """Return text with fenced code blocks replaced by blank lines, preserving
    line numbers, AND a parallel mask marking code lines (so we never rewrite
    inside a code block). Returns (cleaned_for_detection, is_code_line_list)."""
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


def os_relpath(start: Path, target: Path) -> str:
    import os

    return os.path.relpath(target, start).replace(os.sep, "/")


def _split_url_fragment(url: str) -> tuple[str, str]:
    if "#" in url:
        target, _, frag = url.partition("#")
        return target, frag
    return url, ""


def _resolve_md_target(docs_dir: Path, current_file: Path, url: str) -> Path | None:
    target, _frag = _split_url_fragment(url)
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
        candidates.append(candidate.with_suffix(".md"))
        candidates.append(candidate / "index.md")
    for c in candidates:
        if c.exists():
            return c
    return None


def _abs_to_relative_target(docs_dir: Path, current_file: Path, url: str) -> str | None:
    """Resolve an internal absolute URL to a suggested relative .md path."""
    parsed = urlparse(url)
    path = unquote(parsed.path)
    # Drop a trailing query like "?h=translate" by ignoring parsed.query.
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


def _abs_resource_to_relative(docs_dir: Path, current_file: Path, url: str) -> str | None:
    """Resolve an internal absolute image URL to a suggested relative path."""
    parsed = urlparse(url)
    target = unquote(parsed.path)
    if target.startswith("/"):
        candidate = (docs_dir / target.lstrip("/")).resolve()
    else:
        candidate = (current_file.parent / target).resolve()
    if not candidate.exists():
        return None
    return os_relpath(current_file.parent, candidate)


def _is_internal_absolute(url: str, site_domain: str) -> bool:
    if url.startswith("#"):
        return False
    parsed = urlparse(url)
    if not parsed.scheme and not parsed.netloc:
        return False
    host = parsed.netloc.lower()
    return host == site_domain or host.endswith("." + site_domain)


# --- Fixers ------------------------------------------------------------------


def fix_frontmatter(text: str, docs_dir: Path, current_file: Path) -> tuple[str, int]:
    """Add the `path:` front-matter key to translated docs under doc/<lang>/,
    matching the add_metadata.py convention. Idempotent: no-op if `path:` is
    already present."""
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
        # Insert `path:` inside the existing YAML block, before the closing ---.
        lines = text.splitlines()
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                lines.insert(i, f"path: {path_value}")
                return "\n".join(lines), 1
        return text, 0  # malformed front-matter, leave untouched
    else:
        # No front-matter: prepend one.
        return f"---\npath: {path_value}\n---\n\n{text}", 1


def fix_whitespace(text: str) -> tuple[str, int]:
    """rstrip each line; collapse multiple trailing blank lines to one."""
    count = 0
    lines = text.splitlines()
    new_lines: list[str] = []
    for line in lines:
        if line != line.rstrip():
            count += 1
        new_lines.append(line.rstrip())
    # Collapse trailing blank lines.
    while len(new_lines) > 1 and new_lines[-1] == "" and new_lines[-2] == "":
        new_lines.pop()
        count += 1
    # Preserve the original final-newline presence.
    had_final_newline = text.endswith("\n")
    new_text = "\n".join(new_lines)
    if had_final_newline:
        new_text += "\n"
    return new_text, count


def fix_img_tags(text: str) -> tuple[str, int, list[str]]:
    """Convert <img ...> HTML tags to ![alt](src). Returns (text, count, errors)."""
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


def _rewrite_img_in_line(line: str, line_no: int) -> tuple[str, int, list[str]]:
    """Rewrite all <img ...> in a single line."""
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


def _rewrite_links_in_line(
    line: str, docs_dir: Path, current_file: Path, site_domain: str
) -> tuple[str, int]:
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


def _rewrite_images_in_line(
    line: str, docs_dir: Path, current_file: Path, site_domain: str
) -> tuple[str, int]:
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


def _normalize_md_ext_in_line(
    line: str, docs_dir: Path, current_file: Path, with_ext: bool
) -> tuple[str, int]:
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
        # Only rewrite if there is an actual change to make.
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


# --- Determining majority .md style across docs ------------------------------


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


# --- Orchestration -----------------------------------------------------------


def fix_file(
    text: str,
    docs_dir: Path,
    current_file: Path,
    site_domain: str,
    with_ext: bool,
    enabled: set[str],
) -> tuple[str, dict[str, int], list[str]]:
    """Apply all enabled fixes to a file's content. Returns (new_text, counts, errors)."""
    counts = {k: 0 for k in ("whitespace", "img", "links-absolute", "images-absolute", "links-md-ext", "frontmatter")}
    errors: list[str] = []

    if "frontmatter" in enabled:
        text, n = fix_frontmatter(text, docs_dir, current_file)
        counts["frontmatter"] = n
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

    return text, counts, errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Auto-fix safe Markdown quality issues under docs/."
    )
    parser.add_argument(
        "--docs-dir", type=Path, default=Path("docs"), help="Docs root directory (default: docs)."
    )
    parser.add_argument(
        "--site-domain", default=DEFAULT_SITE_DOMAIN, help="Domain considered internal."
    )
    parser.add_argument(
        "--only", nargs="+", help="Run only these fixes (space-separated names)."
    )
    parser.add_argument(
        "--skip", nargs="+", help="Fixes to ignore (space-separated names)."
    )
    parser.add_argument(
        "--apply", action="store_true", help="Modify files in place (default: dry run)."
    )
    parser.add_argument(
        "--md-ext-style",
        choices=["auto", "with", "without"],
        default="auto",
        help="Target .md extension style for relative links (auto = majority across docs).",
    )
    args = parser.parse_args(argv)

    docs_dir = args.docs_dir.resolve()
    if not docs_dir.is_dir():
        print(f"Directory not found: {docs_dir}", file=sys.stderr)
        return 2

    all_fixes = {"whitespace", "img", "links-absolute", "images-absolute", "links-md-ext", "frontmatter"}
    if args.only:
        enabled = set(args.only) & all_fixes
    else:
        enabled = set(all_fixes)
    enabled -= set(args.skip or [])

    if args.md_ext_style == "auto":
        with_ext = majority_md_ext(docs_dir)
    else:
        with_ext = args.md_ext_style == "with"

    mode = "APPLY" if args.apply else "DRY-RUN"
    print(f"Markdown quality fixer [{mode}]")
    print(f"  Docs directory: {docs_dir}")
    print(f"  Internal site domain: {args.site_domain}")
    print(f"  .md extension style: {'with .md' if with_ext else 'without .md'}")
    print(f"  Active fixes: {', '.join(sorted(enabled)) if enabled else 'none'}")
    print()

    total_counts = {k: 0 for k in ("whitespace", "img", "links-absolute", "images-absolute", "links-md-ext", "frontmatter")}
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
            original, docs_dir, md_file, args.site_domain, with_ext, enabled
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
            if args.apply:
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
    return 1 if had_error else 0


if __name__ == "__main__":
    sys.exit(main())
