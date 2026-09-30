#!/usr/bin/env python3
"""Export the documentation of one language to a standalone PDF.

Reads docs/doc/<lang>/ according to the nav defined in zensical.toml, strips the
YAML front-matter from each page, concatenates them in nav order, rewrites image
paths to the local docs/images/ directory, converts cross-page links into
same-document anchors, and converts the result with pandoc into a standalone
PDF with a table of contents, titled "QualCoder - <generation date>".

Usage:
    python scripts/export_docs.py fr             # -> qualcoder-doc-fr.pdf
    python scripts/export_docs.py en -o doc.pdf  # -> doc.pdf

Requirements: pandoc and a LaTeX engine (pdflatex, xelatex or lualatex).
No third-party Python dependencies (tomllib is in the standard library since
Python 3.11).
"""
from __future__ import annotations

import argparse
import datetime
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CONFIG_FILE = REPO_ROOT / "zensical.toml"
DOC_DIR = REPO_ROOT / "docs" / "doc"

FRONT_MATTER_RE = re.compile(r"\A---\s*\n.*?\n---\s*\n", re.DOTALL)
IMAGE_RE = re.compile(r"(\!\[[^\]]*\]\()/images/")
# Site-wide links such as (/latest) or (/community) are resolved by the
# website generator; keep only their label in the exported document.
SITE_LINK_RE = re.compile(r"\[([^\]]+)\]\(/[^)]*\)")
# Cross-page links: (2.4.-Working-in-a-Team), (4.2.-AI-Assisted-Coding#anchor),
# (2.4.-Working-in-a-Team.md/#anchor) or (index). The ".md" part is optional.
DOC_LINK_RE = re.compile(
    r"\[([^\]]+)\]\(([^)#\s]+?)(?:\.md)?(?:/)?(?:#([^)]*))?\)"
)


def load_lang_pages(lang: str) -> list[Path]:
    """Return the documentation pages of a language in nav order."""
    if not CONFIG_FILE.exists():
        sys.exit(f"error: {CONFIG_FILE} not found")
    if not (DOC_DIR / lang).is_dir():
        sys.exit(f"error: unknown language '{lang}' (no {DOC_DIR / lang}/ directory)")

    with open(CONFIG_FILE, "rb") as fh:
        config = tomllib.load(fh)

    pages: list[Path] = []
    for entry in config["project"]["nav"]:
        items = entry.values() if isinstance(entry, dict) else [entry]
        for value in items:
            collect_pages(value, lang, pages)

    if not pages:
        sys.exit(f"error: language '{lang}' not found in the nav of zensical.toml")

    missing = [p for p in pages if not p.exists()]
    if missing:
        listing = "\n  ".join(str(m) for m in missing)
        sys.exit(f"error: pages listed in the nav are missing:\n  {listing}")
    return pages


def collect_pages(node, lang: str, pages: list[Path]) -> None:
    """Recursively gather doc/<lang>/ page paths from a nav subtree."""
    if isinstance(node, str):
        if node.startswith(f"doc/{lang}/"):
            pages.append(DOC_DIR.parent / node)
    elif isinstance(node, list):
        for item in node:
            collect_pages(item, lang, pages)
    elif isinstance(node, dict):
        for item in node.values():
            collect_pages(item, lang, pages)


def frontmatter_path(page: Path) -> str:
    """Value of the 'path' front-matter key, falling back to the file stem."""
    match = re.search(
        r"^path:\s*(.+?)\s*$", page.read_text(encoding="utf-8"), re.MULTILINE
    )
    return match.group(1) if match else page.stem


def page_anchor(page_url: str, heading: str) -> str:
    """Deterministic anchor identifying a page (and optionally a heading)."""
    base = page_url.strip("/").rpartition("/")[2]
    slug = slugify(heading) if heading else ""
    return f"{base}-{slug}" if slug else base


def slugify(text: str) -> str:
    """Lowercase ASCII-ish slug, similar to common site generators."""
    text = text.strip().lower()
    text = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE)
    return re.sub(r"[\s_-]+", "-", text)


def rewrite_internal_links(text: str, anchors: dict[str, str]) -> str:
    """Turn cross-page links into same-document anchors; keep the label of
    unresolvable site links."""

    def site_link_sub(match: re.Match) -> str:
        return match.group(1)

    def doc_link_sub(match: re.Match) -> str:
        label, target, heading = match.group(1), match.group(2), match.group(3)
        if target not in anchors:
            return match.group(0)
        return f"[{label}](#{page_anchor(anchors[target], heading or '')})"

    text = SITE_LINK_RE.sub(site_link_sub, text)
    return DOC_LINK_RE.sub(doc_link_sub, text)


def page_to_markdown(path: Path, anchors: dict[str, str]) -> str:
    """Read one page: strip front-matter, rewrite images and cross-page links.

    Pages already contain their own level-1 heading, so no title is inserted.
    """
    text = path.read_text(encoding="utf-8")
    text = FRONT_MATTER_RE.sub("", text, count=1)
    text = IMAGE_RE.sub(r"\1images/", text)
    text = rewrite_internal_links(text, anchors)
    return text.strip()


def build_markdown(pages: list[Path]) -> str:
    anchors = {p.stem: frontmatter_path(p) for p in pages}
    parts = [page_to_markdown(p, anchors) for p in pages]
    return "\n\n".join(parts) + "\n"


def find_pdf_engine() -> str:
    """Return the first available LaTeX engine."""
    for engine in ("xelatex", "lualatex", "pdflatex"):
        if shutil.which(engine):
            return engine
    sys.exit("error: PDF output requires a LaTeX engine (pdflatex, xelatex or lualatex)")


def run_pandoc(markdown: str, output: Path, title: str) -> None:
    """Convert the assembled Markdown into a standalone PDF with pandoc."""
    if shutil.which("pandoc") is None:
        sys.exit("error: pandoc is not installed (see https://pandoc.org/installing.html)")

    command = [
        "pandoc",
        "--from", "markdown",
        "--to", "pdf",
        "--standalone",
        "--toc",
        "--metadata", f"title={title}",
        "--resource-path", str(REPO_ROOT / "docs"),
        "--pdf-engine", find_pdf_engine(),
        "--output", str(output),
    ]

    with tempfile.NamedTemporaryFile(
        "w", suffix=".md", encoding="utf-8", delete=False
    ) as tmp:
        tmp.write(markdown)
        tmp_path = tmp.name

    command.append(tmp_path)
    try:
        result = subprocess.run(command, check=False, capture_output=True, text=True)
    finally:
        Path(tmp_path).unlink(missing_ok=True)

    if result.returncode != 0:
        sys.exit(f"error: pandoc failed:\n{result.stderr}")
    if result.stderr.strip():
        print(result.stderr, file=sys.stderr)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export the documentation of one language as a standalone PDF"
                    " with a table of contents.",
    )
    parser.add_argument(
        "lang",
        help="documentation language: en, fr, es, de, or a single-page language",
    )
    parser.add_argument(
        "-o", "--output", type=Path,
        help="output PDF file (default: qualcoder-doc-<lang>.pdf in the current"
             " directory)",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    output = args.output or Path(f"qualcoder-doc-{args.lang}.pdf")
    if output.suffix.lower() != ".pdf":
        sys.exit("error: the output file must end in .pdf")

    pages = load_lang_pages(args.lang)
    markdown = build_markdown(pages)

    generation_date = datetime.date.today().isoformat()
    title = f"QualCoder - {generation_date}"

    output.parent.mkdir(parents=True, exist_ok=True)
    run_pandoc(markdown, output, title)
    print(f"exported {len(pages)} page(s) of '{args.lang}' to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
