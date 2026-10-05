#!/usr/bin/env python3
"""Concatenate the documentation of each language into single Markdown pages.

Reads docs/doc/<lang>/ according to the nav defined in zensical.toml, strips
the YAML front-matter from each page, and concatenates them in nav order into
docs/doc/<lang>/print.md, preserving the authoring syntax (admonitions, tabs,
attr_list, icons) so that Zensical renders it with the usual styling.

Heading ids are prefixed with the page id (first h1 gets the bare page id) so
that anchors stay unique after concatenation; cross-page links are rewritten
to same-document anchors pointing at those ids. Site-root shortcut links
(/latest, /community...) are resolved to their real destinations when known
(download buttons keep their attr_list and render as buttons), and reduced to
their label otherwise.

Usage:
    python scripts/export_docs.py            # every multi-page language
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
# Site-root shortcut link: [label](/path){ .attr } — the path and the optional
# attr_list are captured separately so known shortcuts can be resolved to
# real URLs (keeping the attr_list, i.e. the button styling) while unknown
# ones are reduced to their label.
SITE_LINK_RE = re.compile(
    r"\[([^]]+)]\(/([^)#\s]+?)\)(\s*\{[^}]*})?")
DOC_LINK_RE = re.compile(r"\[([^]]+)]\(([^)#\s]+?)(?:\.md)?(?:/)?(?:#([^)]*))?\)")
# Root-absolute image paths (/images/...) become relative to /<lang>/print/.
IMAGE_RE = re.compile(r"(\!\[[^]]*]\()(/?images/)")

# Real destinations of the site shortcuts (download and community buttons).
SITE_SHORTCUTS = {
    "latest": "https://github.com/ccbogel/QualCoder/releases/latest",
    "latest-windows": "https://github.com/ccbogel/QualCoder/releases/latest",
    "latest-windows-portable": "https://github.com/ccbogel/QualCoder/releases/latest",
    "latest-mac": "https://github.com/ccbogel/QualCoder/releases/latest",
    "latest-linux": "https://github.com/ccbogel/QualCoder/releases/latest",
    "latest-linux-executable": "https://github.com/ccbogel/QualCoder/releases/latest",
    "community": "https://qualcoder.org/community/",
}

def load_config() -> dict:
    if not CONFIG_FILE.exists():
        sys.exit(f"error: {CONFIG_FILE} not found")
    with open(CONFIG_FILE, "rb") as fh:
        return tomllib.load(fh)


def load_nav_entries(config: dict) -> list:
    out = []
    for entry in config["project"]["nav"]:
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
    counts: dict[str, int] = {}
    for value in load_nav_entries(load_config()):
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


def iter_lines(text: str):
    """Yield (line, heading_match); headings inside fenced code are ignored."""
    fence = False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            fence = not fence
            yield line, None
            continue
        yield line, (None if fence else HEADING_RE.match(line))


def unique_id(base: str, used: set[str]) -> str:
    """Return base, or base-1, base-2... if it was already used."""
    if base not in used:
        used.add(base)
        return base
    suffix = 1
    while f"{base}-{suffix}" in used:
        suffix += 1
    hid = f"{base}-{suffix}"
    used.add(hid)
    return hid


def build_anchor_map(pages: list[Path]) -> dict[tuple[str, str | None], str]:
    """Map (page key, heading slug or None) -> same-document anchor id.

    The page key accepts both the file stem and the front-matter 'path' value
    so that links written either way keep working.
    """
    anchors: dict[tuple[str, str | None], str] = {}
    for page in pages:
        pid = page_id(page)
        keys = {page.stem, frontmatter_path(page)}
        for key in keys:
            anchors[(key, None)] = pid
        text = FRONT_MATTER_RE.sub("", page.read_text(encoding="utf-8"), count=1)
        used: set[str] = set()
        first_h1 = True
        for _, match in iter_lines(text):
            if not match:
                continue
            if first_h1 and len(match.group(1)) == 1:
                hid = pid
                first_h1 = False
            else:
                hid = f"{pid}-{slugify(match.group(2))}"
            hid = unique_id(hid, used)
            for key in keys:
                anchors[(key, slugify(match.group(2)))] = hid
    return anchors


def rewrite_links(text: str, anchors: dict[tuple[str, str | None], str]) -> str:
    """Rewrite cross-page links to anchors; resolve or reduce shortcut links."""
    def doc_link_sub(match: re.Match) -> str:
        label, target, heading = match.group(1), match.group(2), match.group(3)
        key = (target, slugify(heading) if heading else None)
        if key not in anchors:
            return match.group(0)
        return f"[{label}](#{anchors[key]})"

    def site_link_sub(match: re.Match) -> str:
        label, target, attr = match.group(1), match.group(2), match.group(3)
        if target in SITE_SHORTCUTS:
            return f"[{label}]({SITE_SHORTCUTS[target]}){attr or ''}"
        # Unknown shortcut: keep the label, drop the link and the attr_list.
        return label

    text = SITE_LINK_RE.sub(site_link_sub, text)
    return DOC_LINK_RE.sub(doc_link_sub, text)


def add_heading_ids(text: str, pid: str) -> str:
    """Give every heading an explicit id; the first h1 becomes the page id."""
    used: set[str] = set()
    first_h1 = True
    out_lines: list[str] = []
    for line, match in iter_lines(text):
        if match:
            if first_h1 and len(match.group(1)) == 1:
                hid = pid
                first_h1 = False
            else:
                hid = f"{pid}-{slugify(match.group(2))}"
            hid = unique_id(hid, used)
            out_lines.append(f"{match.group(1)} {match.group(2)} {{#{hid}}}")
        else:
            out_lines.append(line)
    return "\n".join(out_lines)


def page_to_markdown(path: Path, anchors: dict[tuple[str, str | None], str]) -> str:
    """Read one page: strip front-matter, rewrite images and links, add ids."""
    text = path.read_text(encoding="utf-8")
    text = FRONT_MATTER_RE.sub("", text, count=1)
    text = IMAGE_RE.sub(r"\1../../images/", text)
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
    """Concatenate the pages with a cover, a table of contents and content."""
    anchors = build_anchor_map(pages)
    lang_names = {"fr": "Français", "en": "English", "es": "Español",
                  "de": "Deutsch"}
    lang_label = lang_names.get(lang, lang.upper())
    parts = ["---", "path: print", "template: print.html", "---", "",
             # ---- Page de garde ----
             '<div class="print-cover" aria-hidden="true">', "",
             f'# Documentation QualCoder {{#top}}', "",
             f'**Version du {datetime.date.today().strftime("%d/%m/%Y")}**', "",
             f'_{lang_label}_', "",
             f'Documentation complète de QualCoder — {len(pages)} sections', "",
             "Manuel d'utilisation du logiciel d'analyse de données qualitatives",
             "",
             '<img src="../../images/logo.png" alt="" class="print-cover-logo">',
             "",
             "</div>", "",
             '<div class="print-toc">', "",
             "## Sommaire {#sommaire}", ""]
    # --- Sommaire 2 niveaux (inchangé) ---
    for page in pages:
        parts.append(f"- [{page_title(page)}](#{page_id(page)})")
        pid = page_id(page)
        for line, match in iter_lines(
                FRONT_MATTER_RE.sub("", page.read_text(encoding="utf-8"), count=1)):
            if match and len(match.group(1)) == 2:
                section = match.group(2)
                parts.append(f"  - [{section}](#{pid}-{slugify(section)})")
    parts += ["", "</div>", "", "---", ""]
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
