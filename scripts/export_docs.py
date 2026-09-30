#!/usr/bin/env python3
"""Export the documentation of one language to a single self-contained file.

Reads docs/doc/<lang>/ according to the nav defined in zensical.toml, strips the
YAML front-matter from each page, concatenates them in nav order, rewrites image
paths to the local docs/images/ directory, converts cross-page links into
same-document anchors, and converts the result with pandoc to the requested
output format.

Examples:
    python scripts/export_docs.py en -o qualcoder-doc-en.html
    python scripts/export_docs.py fr -o qualcoder-doc-fr.docx
    python scripts/export_docs.py es -f pdf -o qualcoder-doc-es.pdf
    python scripts/export_docs.py de --standalone --toc -o qualcoder-doc-de.html

Supported languages: en, fr, es, de plus any single-page language
(eo, eu, fa, ht, it, ja, oc, pt, ro, sv, zh).

Requirements: pandoc installed. For PDF output, a LaTeX engine (pdflatex,
xelatex or lualatex) must also be available. No third-party Python
dependencies (tomllib is part of the standard library since Python 3.11).
"""
from __future__ import annotations

import argparse
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
IMAGE_RE = re.compile(r"(\!\[[^\]]*\]\()(/images/)")
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
    text = IMAGE_RE.sub(r"\1(images/", text)
    text = rewrite_internal_links(text, anchors)
    return text.strip()


def build_markdown(pages: list[Path]) -> str:
    anchors = {p.stem: frontmatter_path(p) for p in pages}
    parts = [page_to_markdown(p, anchors) for p in pages]
    return "\n\n".join(parts) + "\n"


def infer_format(output: Path) -> str:
    """Guess the pandoc output format from the output file extension."""
    suffix = output.suffix.lower().lstrip(".")
    mapping = {
        "html": "html", "htm": "html",
        "docx": "docx", "odt": "odt", "rtf": "rtf", "epub": "epub",
        "pdf": "pdf", "tex": "latex", "md": "markdown", "txt": "plain",
    }
    if suffix not in mapping:
        sys.exit(f"error: cannot infer output format from '{output.name}'; use --format")
    return mapping[suffix]


def run_pandoc(markdown: str, args: argparse.Namespace) -> None:
    """Convert the assembled Markdown via pandoc."""
    if shutil.which("pandoc") is None:
        sys.exit("error: pandoc is not installed (see https://pandoc.org/installing.html)")

    out_format = args.format or infer_format(args.output)
    command = [
        "pandoc",
        "--from", "markdown",
        "--to", out_format,
        "--resource-path", str(REPO_ROOT / "docs"),
    ]
    if args.standalone:
        command.append("--standalone")
    if args.toc:
        command.append("--toc")
    if args.title:
        command += ["--metadata", f"title={args.title}"]
    command.append("--output", str(args.output))

    if out_format == "pdf":
        engine = args.pdf_engine
        if engine is None:
            for candidate in ("xelatex", "lualatex", "pdflatex"):
                if shutil.which(candidate):
                    engine = candidate
                    break
        if engine is None:
            sys.exit(
                "error: PDF output requires a LaTeX engine (pdflatex, xelatex or lualatex)"
            )
        command += ["--pdf-engine", engine]

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
        description="Export the documentation of one language with pandoc.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "lang",
        help="documentation language: en, fr, es, de, or a single-page language",
    )
    parser.add_argument(
        "-o", "--output", type=Path,
        help="output file; format inferred from the extension unless --format is given"
             " (required unless --dry-run)",
    )
    parser.add_argument(
        "-f", "--format",
        help="pandoc output format (html, docx, pdf, odt, epub, ...)",
    )
    parser.add_argument(
        "--pdf-engine",
        help="LaTeX engine for PDF output (default: auto-detect xelatex/lualatex/pdflatex)",
    )
    parser.add_argument(
        "--standalone", action="store_true",
        help="produce a standalone HTML file (with header and styles) instead of a fragment",
    )
    parser.add_argument("--toc", action="store_true", help="add a table of contents")
    parser.add_argument(
        "--title",
        help="document title metadata (e.g. for the HTML <title> or PDF cover)",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="print the assembled Markdown to stdout instead of running pandoc",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    if args.output is None and not args.dry_run:
        sys.exit("error: -o/--output is required unless --dry-run is used")

    pages = load_lang_pages(args.lang)
    markdown = build_markdown(pages)

    if args.dry_run:
        sys.stdout.write(markdown)
        return 0

    args.output.parent.mkdir(parents=True, exist_ok=True)
    run_pandoc(markdown, args)
    print(f"exported {len(pages)} page(s) of '{args.lang}' to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
