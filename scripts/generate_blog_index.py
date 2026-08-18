#!/usr/bin/env python3
"""Generates docs/blog/index.md by listing the posts in the docs/blog/posts/ folder.

Scans Markdown files (or files without an extension) in docs/blog/posts/,
reads their YAML front-matter (title, date, author, category) and produces an
index sorted in descending order by date. Preserves any manual content located
above the <!-- blog-index:generated:start --> marker.
No external dependencies: the front-matter is parsed manually.
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

# --- Configuration -----------------------------------------------------------
POSTS_DIR = Path("docs/blog/posts")
INDEX_FILE = Path("docs/blog/index.md")
START_MARKER = "<!-- blog-index:generated:start -->"
END_MARKER = "<!-- blog-index:generated:end -->"


# --- Parsing front-matter ----------------------------------------------------
def parse_front_matter(text: str) -> tuple[dict, str]:
    """Retourne (metadata, body). metadata = dict simple des champs YAML."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, text
    meta: dict[str, str] = {}
    i = 1
    while i < len(lines) and lines[i].strip() != "---":
        line = lines[i]
        if ":" in line:
            key, _, value = line.partition(":")
            meta[key.strip()] = value.strip().strip('"').strip("'")
        i += 1
    body = "\n".join(lines[i + 1 :]).lstrip("\n") if i < len(lines) else ""
    return meta, body


def parse_date(value: str) -> date:
    """Convert 'YYYY-MM-DD' Into date."""
    return date.fromisoformat(value.strip())


# --- read posts --------------------------------------------------------
def collect_posts() -> list[dict]:
    posts = []
    for path in sorted(POSTS_DIR.iterdir()):
        if not path.is_file():
            continue
        if path.suffix not in ("", ".md"):
            continue
        text = path.read_text(encoding="utf-8")
        meta, body = parse_front_matter(text)
        if not meta.get("date") or not meta.get("title"):
            continue  # if incomplet post, ignore
        try:
            d = parse_date(meta["date"])
        except ValueError:
            print(f"Invalid date {path.name}, ignored", file=sys.stderr)
            continue
        slug = path.stem if path.suffix else path.name
        posts.append(
            {
                "title": meta.get("title", path.stem),
                "date": d,
                "date_str": d.isoformat(),
                "author": meta.get("author", ""),
                "category": meta.get("category", ""),
                "slug": slug,
                "body": body,
            }
        )
    posts.sort(key=lambda p: p["date"], reverse=True)
    return posts


def excerpt(body: str, max_chars: int = 200) -> str:
    """Extract the first paragraph."""
    for block in body.split("\n\n"):
        block = block.strip()
        if block and not block.startswith(("![", "|", "#")):
            return block if len(block) <= max_chars else block[:max_chars].rsplit(" ", 1)[0] + "…"
    return ""


# --- Index generation ---------------------------------------------------
def render_index_full(posts: list[dict]) -> str: # Full version (all content in the index)
    lines = ["# Blog\n"]
    for p in posts:
        d = p["date"].strftime("%d %B %Y")
        link = f"posts/{p['slug']}/"
        lines.append(f"## [{p['title']}]({link})\n")
        meta_bits = [f"**{d}**"]
        if p["author"]:
            meta_bits.append(f"by {p['author']}")
        if p["category"]:
            meta_bits.append(f"· {p['category']}")
        lines.append(" ".join(meta_bits) + "\n")
        ex = p["body"]
        if ex:
            lines.append(ex + "\n")
        lines.append("---\n")
    return "\n".join(lines).rstrip() + "\n"

def render_index(posts: list[dict]) -> str: # only date and title
    lines = ["# Blog\n"]
    for p in posts:
        d = p["date"].strftime("%d %B %Y")
        link = f"posts/{p['slug']}/"
        lines.append(f"- **{d}** [{p['title']}]({link})")
    return "\n".join(lines).rstrip() + "\n"
    
def write_index(content: str) -> None:
    """Write index."""
    generated_block = f"{START_MARKER}\n{content}{END_MARKER}\n"
    if INDEX_FILE.exists():
        text = INDEX_FILE.read_text(encoding="utf-8")
        if START_MARKER in text and END_MARKER in text:
            pre = text.split(START_MARKER)[0]
            post = text.split(END_MARKER, 1)[1]
            INDEX_FILE.write_text(pre + generated_block + post, encoding="utf-8")
            return
    INDEX_FILE.parent.mkdir(parents=True, exist_ok=True)
    INDEX_FILE.write_text(generated_block, encoding="utf-8")


def main() -> int:
    if not POSTS_DIR.is_dir():
        print(f"❌ Directory dont font : {POSTS_DIR}", file=sys.stderr)
        return 1
    posts = collect_posts()
    if not posts:
        print("Nothing post found", file=sys.stderr)
        return 1
    write_index(render_index(posts))
    print(f"✅ {len(posts)} posts indexed in {INDEX_FILE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
