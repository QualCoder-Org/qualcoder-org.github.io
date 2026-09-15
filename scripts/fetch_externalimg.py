#!/usr/bin/env python3
"""
Fetch external images referenced in the docs and store them locally under docs/images/.

Sources handled:
  - https://qualcoder.wordpress.com/wp-content/uploads/<YYYY>/<MM>/<name>.<ext>[?w=NNN]
  - https://github.com/user-attachments/assets/<uuid>
  - https://cdn.buymeacoffee.com/buttons/default-orange.png

Behaviour:
  - Scans the given Markdown file(s) for image URLs hosted on the above domains.
  - Skips URLs whose target file is already present in docs/images/ (by exact URL->name map).
  - Downloads with a User-Agent header. For WordPress, tries the URL as-is, then without
    the query string (older uploads 404 when ?w=NNN is present but the original is fine).
  - Names files uniquely using the upload date path (WordPress) so that several distinct
    `image.png` uploaded at different months do not collide:
        wp-<YYYY>-<MM>-<name>.<ext>
    For GitHub user-attachments: gh-<uuid>.<ext>
    For Buy Me a Coffee: buymeacoffee-default-orange.png
  - Never overwrites an existing file in docs/images/; if a name collision occurs it
    appends a numeric suffix.
  - Prints a manifest to stdout: <local path>\t<source URL>\t<status>
  - The 7 WordPress images known to be 404 (see report) are retried via Wayback Machine
    as a last resort; if still missing they are reported as FAILED and left untouched.

With --rewrite, also rewrites the Markdown files in place to point at the local
/images/<name> paths (only for URLs whose local file exists; others left unchanged).

Usage:
    python3 scripts/fetch_external_images.py [docs/blog/misc.md ...] [--out docs/images] [--rewrite] [--dry-run]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

WP_RE = re.compile(
    r"https://qualcoder\.wordpress\.com/wp-content/uploads/"
    r"(?P<y>\d{4})/(?P<m>\d{2})/(?P<name>[^)\"]+)"
)
GH_RE = re.compile(r"https://github\.com/user-attachments/assets/(?P<uuid>[a-f0-9-]+)")
BMC_RE = re.compile(
    r"https://cdn\.buymeacoffee\.com/buttons/(?P<name>[^)\"]+)"
)
# Match any URL from the supported external hosts, anywhere in the text. Many lines
# look like `[![](URL1?w=NNN)](URL2)` containing two distinct URLs (resized + original);
# a per-link regex would only capture one of them, so we scan for the raw URLs.
EXT_URL_RE = re.compile(
    r"https://(?:"
    r"qualcoder\.wordpress\.com/wp-content/uploads/[^)\"\s]+"
    r"|github\.com/user-attachments/assets/[a-f0-9-]+"
    r"|cdn\.buymeacoffee\.com/buttons/[^)\"\s]+"
    r")"
)

UA = "Mozilla/5.0 (X11; Linux x86_64) QualCoder-docs-image-fetcher"


def fetch(url: str, timeout: int = 30) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    return urllib.request.urlopen(req, timeout=timeout).read()


def wayback(url: str) -> str | None:
    api = "https://archive.org/wayback/available?url=" + urllib.request.quote(url, safe="")
    try:
        req = urllib.request.Request(api, headers={"User-Agent": UA})
        data = json.loads(urllib.request.urlopen(req, timeout=25).read())
        snap = data.get("archived_snapshots", {}).get("closest", {})
        return snap.get("url") if snap.get("available") else None
    except Exception:
        return None


def local_name_for(url: str) -> str:
    m = WP_RE.search(url)
    if m:
        name = m.group("name").split("?")[0]
        return f"wp-{m.group('y')}-{m.group('m')}-{name}"
    m = GH_RE.search(url)
    if m:
        ext = "png"
        return f"gh-{m.group('uuid')}.{ext}"
    m = BMC_RE.search(url)
    if m:
        return f"buymeacoffee-{m.group('name').split('?')[0]}"
    # Fallback: derive from path
    base = url.split("/")[-1].split("?")[0]
    return f"ext-{base}"


def collect_urls(md_path: Path) -> list[str]:
    text = md_path.read_text(encoding="utf-8", errors="replace")
    urls: list[str] = [m.group(0).strip() for m in EXT_URL_RE.finditer(text)]
    # de-dup, preserve order
    seen: set[str] = set()
    uniq: list[str] = []
    for u in urls:
        if u not in seen:
            seen.add(u)
            uniq.append(u)
    return uniq


def unique_path(out_dir: Path, name: str) -> Path:
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


def resolve_local(out_dir: Path, url: str) -> str | None:
    """Return the absolute site path '/images/<name>' if a local file exists for this
    external URL (canonical name, then suffixed variants), else None."""
    name = local_name_for(url)
    if (out_dir / name).exists():
        return f"/images/{name}"
    stem, dot, ext = name.rpartition(".")
    i = 1
    while (out_dir / f"{stem}-{i}{dot}{ext}").exists():
        return f"/images/{stem}-{i}{dot}{ext}"
    return None


def rewrite_md(md_path: Path, out_dir: Path, dry_run: bool = False) -> int:
    """Replace external image URLs in md_path with local '/images/<name>' paths.
    Only URLs that resolve to an existing local file are replaced; others are left
    untouched and reported. Returns the number of replacements made."""
    text = md_path.read_text(encoding="utf-8", errors="replace")
    replacements = 0
    unresolved: list[tuple[str, str]] = []

    def repl(m: re.Match) -> str:
        nonlocal replacements
        url = m.group(0)
        local = resolve_local(out_dir, url)
        if local is None:
            unresolved.append((url, "not downloaded / missing locally"))
            return url  # leave unchanged
        replacements += 1
        return local

    new_text = EXT_URL_RE.sub(repl, text)
    if replacements and not dry_run:
        md_path.write_text(new_text, encoding="utf-8")
    for url, why in unresolved:
        print(f"#  rewrite: left unchanged ({why}): {url}", file=sys.stderr)
    return replacements


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("files", nargs="*", default=["docs/blog/misc.md"])
    ap.add_argument("--out", default="docs/images")
    ap.add_argument("--delay", type=float, default=0.3, help="seconds between requests")
    ap.add_argument(
        "--rewrite",
        action="store_true",
        help="After fetching, rewrite Markdown files to point at the local images "
        "(/images/<name>) instead of the external URLs.",
    )
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="With --rewrite, print what would change without writing the .md files.",
    )
    args = ap.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    urls: list[str] = []
    for f in args.files:
        p = Path(f)
        if not p.exists():
            print(f"SKIP missing file: {f}", file=sys.stderr)
            continue
        urls.extend(collect_urls(p))

    # de-dup across files
    seen: set[str] = set()
    uniq: list[str] = []
    for u in urls:
        if u not in seen:
            seen.add(u)
            uniq.append(u)

    print(f"# {len(uniq)} unique external URLs to fetch -> {out_dir}", file=sys.stderr)

    ok = skip = failed = 0
    print("local_path\tstatus\tsource_url")
    for url in uniq:
        name = local_name_for(url)
        # Already present under the canonical name? skip.
        if (out_dir / name).exists():
            print(f"{out_dir / name}\tSKIP-EXISTS\t{url}")
            skip += 1
            continue

        data: bytes | None = None
        candidates = [url]
        if url.startswith("https://qualcoder.wordpress.com/"):
            # Older uploads 404 with the ?w= resize query; the original is fine.
            if "?" in url:
                candidates.append(url.split("?", 1)[0])

        for cand in candidates:
            try:
                data = fetch(cand)
                break
            except Exception:
                continue

        if data is None:
            # Last resort: Wayback Machine (no query string).
            wb = wayback(url.split("?", 1)[0])
            if wb:
                try:
                    data = fetch(wb)
                except Exception:
                    data = None

        if data is None:
            print(f"{out_dir / name}\tFAILED\t{url}")
            failed += 1
            time.sleep(args.delay)
            continue

        target = unique_path(out_dir, name)
        target.write_bytes(data)
        print(f"{target}\tOK\t{url}")
        ok += 1
        time.sleep(args.delay)

    print(
        f"# done: ok={ok} skipped(existing)={skip} failed={failed}",
        file=sys.stderr,
    )

    if args.rewrite:
        total_repl = 0
        for f in args.files:
            p = Path(f)
            if not p.exists():
                continue
            n = rewrite_md(p, out_dir, dry_run=args.dry_run)
            verb = "would rewrite" if args.dry_run else "rewrote"
            print(f"# {verb} {n} URL(s) in {f}", file=sys.stderr)
            total_repl += n
        print(f"# rewrite total: {total_repl} URL(s)", file=sys.stderr)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
