#!/usr/bin/env python3
"""Concatenate the documentation of each language into single Markdown pages.

Reads docs/doc/<lang>/ according to the nav defined in zensical.toml, strips
the YAML front-matter from each page, and concatenates them in nav order into
docs/doc/<lang>/print.md, preserving the authoring syntax (admonitions, tabs,
attr_list, icons) so that Zensical renders it with the usual styling.

To survive concatenation, every heading gets an explicit id prefixed with the
page id (e.g. "{#2-2-settings}" on page 2.2.-Settings), and cross-page links
are rewritten to same-document anchors pointing at those ids.

Usage:
    python scripts/export_docs.py            # -> print.md for every multi-page language
    python scripts/export_docs.py fr        # -> docs/doc/fr/print.md only
    python scripts/export_docs.py fr -o t.md
"""

from __future__ import annotations

import argparse
import re
import sys
import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CONFIG_FILE = REPO_ROOT / "zensical.toml"
DOC_DIR = REPO_ROOT / "docs" / "doc"

FRONT_MATTER_RE = re.compile(r"\A---\s*\n.*?\n---\s*\n", re.DOTALL)
HEADING_RE = re.compile(r"^(#{1,6}) (.+?)\s*(\{[^}]*})?\s*$")
ATTR_LIST_RE = re.compile(r"\s*(\{[^}]*})\s*$")
SITE_LINK_RE = re.compile(r"\[([^]]+)]\(/[^)]*\)")
DOC_LINK_RE = re.compile(
    r"\[([^]]+)]\(([^)#\s]+?)(?:\.md)?(?:/)?(?:#([^)]*))?\)")


def load_config() -> dict:
    """Parse zensical.toml or exit with an error."""
    if not CONFIG_FILE.exists():
        sys.exit(f"error: {CONFIG_FILE} not found")
    with open(CONFIG_FILE, "rb") as fh:
        return tomllib.load(fh)


def load_nav_entries(config: dict) -> list:
    """Flat list of the top-level nav entries of zensical.toml."""
    entries = config["project"]["nav"]
    out = []
    for entry in entries:
        out.extend(entry.values() if isinstance(entry, dict) else [entry])
    return out


def collect_pages(node, lang: str, pages: list[Path]) -> None:
    """Recursively gather doc/<lang>/ page paths from a nav subtree."""
    if isinstance(node, str):
        if node.startswith(f"doc/{lang}/") and not node.endswith(f"{lang}/print.md"):
            pages.append(DOC_DIR.parent / node)
    elif isinstance(node, list):
        for item in node:
            collect_pages(item, lang, pages)
    elif isinstance(node, dict):
        for item in node.values():
            collect_pages(item, lang, pages)


def load_lang_pages(lang: str) -> list[Path]:
    """Return the documentation pages of a language in nav order."""
    if not (DOC_DIR / lang).is_dir():
        sys.exit(f"error: unknown language '{lang}' (no {DOC_DIR / lang}/ directory)")
    pages: list[Path] = []
    for value in load_nav_entries(load_config()):
        collect_pages(value, lang, pages)
    if not pages:
        sys.exit(f"error: language '{lang}' not found in the nav of zensical.toml")
    missing = [p for p in pages if not p.exists()]
    if missing:
        listing = "\n  ".join(str(m) for m in missing)
        sys.exit(f"error: pages listed in the nav are missing:\n  {listing}")
    return pages


def collect_lang_counts(node, counts: dict[str, int]) -> None:
    """Recursively count doc/<lang>/ pages in a nav subtree."""
    if isinstance(node, str) and node.startswith("doc/"):
        parts = node.split("/")
        if len(parts) > 2 and not node.endswith("/print.md"):
            lang = parts[1]
            counts[lang] = counts.get(lang, 0) + 1
    elif isinstance(node, list):
        for item in node:
            collect_lang_counts(item, counts)
    elif isinstance(node, dict):
        for item in node.values():
            collect_lang_counts(item, counts)


def nav_langs() -> dict[str, int]:
    """Count the pages per language found in the nav of zensical.toml."""
    config = load_config()
    counts: dict[str, int] = {}
    for value in load_nav_entries(config):
        collect_lang_counts(value, counts)
    return counts


def slugify(text: str) -> str:
    """Lowercase ASCII-ish slug, similar to common site generators."""
    text = text.strip().lower()
    text = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE)
    return re.sub(r"[\s_-]+", "-", text).strip("-")


def page_id(page: Path) -> str:
    """Deterministic id for a page, derived from its file stem."""
    return slugify(page.stem)


def frontmatter_path(page: Path) -> str:
    """Value of the 'path' front-matter key, falling back to the file stem."""
    match = re.search(
        r"^path:\s*(.+?)\s*$", page.read_text(encoding="utf-8"), re.MULTILINE)
    return match.group(1) if match else page.stem


def build_anchor_map(pages: list[Path]) -> dict[tuple[str, str | None], str]:
    """Map (page key, heading or None) -> same-document anchor id.

    The page key accepts both the file stem and the front-matter 'path' value
    so that links written either way keep working.
    """
    anchors: dict[tuple[str, str | None], str] = {}
    for page in pages:
        pid = page_id(page)
        for key in {page.stem, frontmatter_path(page)}:
            anchors[(key, None)] = pid
        used: set[str] = set()
        for line in page.read_text(encoding="utf-8").splitlines():
            match = HEADING_RE.match(line)
            if not match:
                continue
            hid = f"{pid}-{slugify(match.group(2))}"
            if hid in used:
                suffix = 1
                while f"{hid}-{suffix}" in used:
                    suffix += 1
                hid = f"{hid}-{suffix}"
            used.add(hid)
            for key in {page.stem, frontmatter_path(page)}:
                anchors[(key, slugify(match.group(2)))] = hid
    return anchors


def rewrite_links(text: str, anchors: dict[tuple[str, str | None], str]) -> str:
    """Rewrite cross-page Markdown links to same-document anchors."""
    def doc_link_sub(match: re.Match) -> str:
        label, target, heading = match.group(1), match.group(2), match.group(3)
        key = (target, slugify(heading) if heading else None)
        if key not in anchors:
            return match.group(0)
        return f"[{label}](#{anchors[key]})"

    text = SITE_LINK_RE.sub(lambda m: m.group(1), text)
    return DOC_LINK_RE.sub(doc_link_sub, text)


def add_heading_ids(text: str, pid: str) -> str:
    """Give every heading an explicit attr_list id prefixed with the page id."""
    used: set[str] = set()
    out_lines: list[str] = []
    in_fence = False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            out_lines.append(line)
            continue
        match = HEADING_RE.match(line) if not in_fence else None
        if match:
            heading_id = f"{pid}-{slugify(match.group(2))}"
            if heading_id in used:
                suffix = 1
                while f"{heading_id}-{suffix}" in used:
                    suffix += 1
                heading_id = f"{heading_id}-{suffix}"
            used.add(heading_id)
            out_lines.append(f"{match.group(1)} {match.group(2)} {{#{heading_id}}}")
        else:
            out_lines.append(line)
    return "\n".join(out_lines)


def page_to_markdown(path: Path, anchors: dict[tuple[str, str | None], str]) -> str:
    """Read one page: strip front-matter, rewrite links, add heading ids."""
    text = path.read_text(encoding="utf-8")
    text = FRONT_MATTER_RE.sub("", text, count=1)
    text = rewrite_links(text, anchors)
    text = add_heading_ids(text, page_id(path))
    return text.strip()


def page_title(page: Path) -> str:
    """Level-1 heading of a page (or its stem as a fallback)."""
    for line in page.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            return ATTR_LIST_RE.sub("", line[2:]).strip()
    return page.stem


def build_markdown(lang: str, pages: list[Path]) -> str:
    """Concatenate the pages with a table of contents and a front-matter."""
    anchors = build_anchor_map(pages)
    parts = ["---", "path: print", "---", "",
             f"# Documentation QualCoder ({lang.upper()})", "",
             "## Sommaire {#sommaire}", ""]
    for page in pages:
        parts.append(f"- [{page_title(page)}](#{page_id(page)})")
    parts += ["", "---", ""]
    for page in pages:
        parts.append(page_to_markdown(page, anchors))
    return "\n\n".join(parts) + "\n"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Concatenate the documentation of one language into"
                    " docs/doc/<lang>/print.md, keeping authoring syntax and"
                    " unique heading anchors. Without a language argument,"
                    " every multi-page language is exported.")
    parser.add_argument(
        "lang", nargs="?",
        help="documentation language (en, fr, es, de, ...); if omitted,"
             " all multi-page languages are exported")
    parser.add_argument(
        "-o", "--output", type=Path,
        help="output Markdown file (default: docs/doc/<lang>/print.md;"
             " only valid with a single language)")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    if args.output and not args.lang:
        sys.exit("error: -o/--output requires a single language argument")

    if args.lang:
        langs = [args.lang]
    else:
        counts = nav_langs()
        langs = sorted(lang for lang, count in counts.items() if count > 1)
        if not langs:
            sys.exit("error: no multi-page language found in the nav of zensical.toml")
        print(f"languages to export: {', '.join(langs)}")

    for lang in langs:
        pages = load_lang_pages(lang)
        markdown = build_markdown(lang, pages)
        output = args.output or DOC_DIR / lang / "print.md"
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(markdown, encoding="utf-8")
        print(f"exported {len(pages)} page(s) of '{lang}' to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
