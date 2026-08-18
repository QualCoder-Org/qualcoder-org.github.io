#!/usr/bin/env python3
"""Generates docs/blog/index.md and docs/blog/atom.xml from docs/blog/posts/.

Scans Markdown files (or files without an extension) in docs/blog/posts/,
reads their YAML front-matter (title, date, author, category) and produces:
  - a Markdown index (index.md) sorted in descending order by date, preserving
    any manual content located above the <!-- blog-index:generated:start --> marker;
  - an Atom 1.0 feed (atom.xml) with the most recent posts.
No external dependencies: front-matter and XML are produced manually.
"""

from __future__ import annotations

import argparse
import sys
from datetime import date, datetime, timezone
from html import escape
from pathlib import Path

# --- Configuration -----------------------------------------------------------
POSTS_DIR = Path("docs/blog/posts")
INDEX_FILE = Path("docs/blog/index.md")
FEED_FILE = Path("docs/blog/atom.xml")
START_MARKER = "<!-- blog-index:generated:start -->"
END_MARKER = "<!-- blog-index:generated:end -->"

# Public base URL of the blog. Must end with a "/".
SITE_URL = "https://qualcoder.org/"
BLOG_URL = SITE_URL + "blog/"
# Stable feed id. Atom requires a unique, permanent id for the feed and each
# entry; using the canonical URL is the simplest reliable scheme.
FEED_ID = BLOG_URL
# How many of the most recent posts to include in the feed (0 = all).
MAX_ITEMS = 20
# Max characters of body used to build the excerpt shown in the feed.
EXCERPT_CHARS = 300


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


def to_rfc3339(d: date) -> str:
    """RFC 3339 / ISO-8601 datetime, e.g. '2002-10-02T00:00:00Z'.

    Atom requires an RFC 3339 construct. We publish posts as dated (no time
    information in the front-matter), so we use 00:00:00 UTC.
    """
    return datetime(d.year, d.month, d.day, tzinfo=timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )


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
                "date_rfc3339": to_rfc3339(d),
                "author": meta.get("author", ""),
                "category": meta.get("category", ""),
                "slug": slug,
                "body": body,
            }
        )
    posts.sort(key=lambda p: p["date"], reverse=True)
    return posts


def excerpt(body: str, max_chars: int = EXCERPT_CHARS) -> str:
    """Extract the first paragraph."""
    for block in body.split("\n\n"):
        block = block.strip()
        if block and not block.startswith(("![", "|", "#")):
            return block if len(block) <= max_chars else block[:max_chars].rsplit(" ", 1)[0] + "…"
    return ""


# --- Index generation ---------------------------------------------------
def render_index_full(posts: list[dict]) -> str:  # Full version (all content in the index)
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

def render_index(posts: list[dict]) -> str:  # only date and title
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


# --- Atom generation ---------------------------------------------------
def render_feed(posts: list[dict]) -> str:
    entries: list[str] = []
    shown = posts if MAX_ITEMS <= 0 else posts[:MAX_ITEMS]
    for p in shown:
        link = f"{BLOG_URL}posts/{p['slug']}/"
        entry_id = link  # stable, permanent id
        summary = escape(excerpt(p["body"]))
        content = escape(p["body"])
        author = escape(p["author"]) if p["author"] else "QualCoder"
        category = f"\n    <category term=\"{escape(p['category'])}\" />" if p["category"] else ""
        entries.append(
            "  <entry>\n"
            f"    <title>{escape(p['title'])}</title>\n"
            f"    <id>{escape(entry_id)}</id>\n"
            f"    <link href=\"{escape(link)}\" />\n"
            f"    <updated>{p['date_rfc3339']}</updated>\n"
            f"    <published>{p['date_rfc3339']}</published>\n"
            "    <author>\n"
            f"      <name>{author}</name>\n"
            "    </author>\n"
            f"    <summary type=\"html\">{summary}</summary>\n"
            f"    <content type=\"html\">{content}</content>{category}\n"
            "  </entry>"
        )
    updated = posts[0]["date_rfc3339"] if posts else to_rfc3339(date.today())
    body = "\n".join(entries)
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<feed xmlns="http://www.w3.org/2005/Atom">\n'
        f"  <title>QualCoder Blog</title>\n"
        f"  <id>{escape(FEED_ID)}</id>\n"
        f"  <link href=\"{escape(BLOG_URL)}\" />\n"
        f"  <link href=\"{escape(BLOG_URL)}atom.xml\" rel=\"self\" "
        f'type="application/atom+xml" />\n'
        f"  <updated>{updated}</updated>\n"
        f"{body}\n"
        "</feed>\n"
    )


def write_feed(content: str) -> None:
    FEED_FILE.parent.mkdir(parents=True, exist_ok=True)
    FEED_FILE.write_text(content, encoding="utf-8")


# --- main --------------------------------------------------------
def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--index", action="store_true", help="Generate the Markdown index.")
    parser.add_argument("--rss", action="store_true", help="Generate the Atom feed.")
    args = parser.parse_args()
    # Default: generate both.
    gen_index = args.index or not (args.index or args.rss)
    gen_atom = args.rss or not (args.index or args.rss)

    if not POSTS_DIR.is_dir():
        print(f"❌ Directory dont font : {POSTS_DIR}", file=sys.stderr)
        return 1
    posts = collect_posts()
    if not posts:
        print("Nothing post found", file=sys.stderr)
        return 1

    if gen_index:
        write_index(render_index(posts))
        print(f"✅ {len(posts)} posts indexed in {INDEX_FILE}")
    if gen_atom:
        count = min(len(posts), MAX_ITEMS if MAX_ITEMS > 0 else len(posts))
        write_feed(render_feed(posts))
        print(f"✅ {count} posts in {FEED_FILE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
