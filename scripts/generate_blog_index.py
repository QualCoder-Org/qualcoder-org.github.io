#!/usr/bin/env python3
"""Génère docs/blog/index.md en listant les posts du dossier docs/blog/posts/.

Scanne les fichiers Markdown (ou sans extension) dans docs/blog/posts/,
lit leur front-matter YAML (title, date, author, category) et produit un
index trié par date décroissante. Préserve tout contenu manuel situé
au-dessus de la sentinelle <!-- blog-index:generated:start -->.

Aucune dépendance externe : le front-matter est parsé à la main.
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
    """Convertit 'YYYY-MM-DD' en date. Échoue proprement si invalide."""
    return date.fromisoformat(value.strip())


# --- Lecture des posts --------------------------------------------------------
def collect_posts() -> list[dict]:
    posts = []
    for path in sorted(POSTS_DIR.iterdir()):
        if not path.is_file():
            continue
        # On accepte les .md et les fichiers sans extension (ex: open-curriculum)
        if path.suffix not in ("", ".md"):
            continue
        text = path.read_text(encoding="utf-8")
        meta, body = parse_front_matter(text)
        if not meta.get("date") or not meta.get("title"):
            continue  # post incomplet, on l'ignore
        try:
            d = parse_date(meta["date"])
        except ValueError:
            print(f"⚠️  Date invalide dans {path.name}, ignoré", file=sys.stderr)
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
    """Extrait le premier paragraphe de prose comme aperçu."""
    for block in body.split("\n\n"):
        block = block.strip()
        if block and not block.startswith(("![", "|", "#")):
            # Coupe propre et ajoute des points de suspension si tronqué
            return block if len(block) <= max_chars else block[:max_chars].rsplit(" ", 1)[0] + "…"
    return ""


# --- Génération de l'index ---------------------------------------------------
def render_index(posts: list[dict]) -> str:
    lines = ["# Blog\n"]
    for p in posts:
        d = p["date"].strftime("%d %B %Y")
        link = f"posts/{p['slug']}/"
        lines.append(f"### [{p['title']}]({link})\n")
        meta_bits = [f"**{d}**"]
        if p["author"]:
            meta_bits.append(f"par {p['author']}")
        if p["category"]:
            meta_bits.append(f"· {p['category']}")
        lines.append(" ".join(meta_bits) + "\n")
        ex = excerpt(p["body"])
        if ex:
            lines.append(ex + "\n")
        lines.append("---\n")
    return "\n".join(lines).rstrip() + "\n"


def write_index(content: str) -> None:
    """Écrit l'index en préservant le contenu manuel au-dessus des marqueurs."""
    generated_block = f"{START_MARKER}\n{content}{END_MARKER}\n"
    if INDEX_FILE.exists():
        text = INDEX_FILE.read_text(encoding="utf-8")
        if START_MARKER in text and END_MARKER in text:
            pre = text.split(START_MARKER)[0]
            post = text.split(END_MARKER, 1)[1]
            INDEX_FILE.write_text(pre + generated_block + post, encoding="utf-8")
            return
    # Premier cas : le fichier est vide ou n'a pas de sentinelle
    INDEX_FILE.parent.mkdir(parents=True, exist_ok=True)
    INDEX_FILE.write_text(generated_block, encoding="utf-8")


def main() -> int:
    if not POSTS_DIR.is_dir():
        print(f"❌ Dossier introuvable : {POSTS_DIR}", file=sys.stderr)
        return 1
    posts = collect_posts()
    if not posts:
        print("⚠️  Aucun post trouvé", file=sys.stderr)
        return 1
    write_index(render_index(posts))
    print(f"✅ {len(posts)} posts indexés dans {INDEX_FILE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
