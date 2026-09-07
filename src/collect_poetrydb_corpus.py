"""Collect the full PoetryDB corpus, one request per author where possible.

PoetryDB exposes ~3000 poems by ~129 authors. Fetching by author costs ~129
requests rather than one per title, which is far kinder to a free public API.
Prolific authors are the exception: Byron has 324 poems and the bulk endpoint
returns 503 on that payload, so those authors fall back to one request per
title.

Poems are stored with their blank lines intact: PoetryDB's `linecount` counts
only non-blank lines, so the blanks are stanza separators and carry the
structural information Phase 0 relies on (a sonnet's volta, a villanelle's
tercets). Form detection happens downstream in `poetry_forms.py`; this script
only collects.

Responses are cached per author under data/interim/poetrydb_cache/, so a rerun
after a failure re-fetches only what is missing. Delete that directory to force
a clean pull.

Run from the project root:  uv run python src/collect_poetrydb_corpus.py
"""

import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests
from tqdm import tqdm

OUT_DIR = Path("data/raw")
OUT_DIR.mkdir(parents=True, exist_ok=True)

CACHE_DIR = Path("data/interim/poetrydb_cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

BASE_URL = "https://poetrydb.org"

# PoetryDB publishes no rate limit; be a good citizen anyway.
DELAY_SECONDS = 1.0
NUM_RETRIES = 3


def _hash(*parts: str) -> str:
    return hashlib.sha1("\x00".join(parts).encode("utf-8")).hexdigest()


def get_json(path: str, quiet: bool = False):
    """GET a PoetryDB path, retrying with exponential backoff."""
    url = f"{BASE_URL}/{path}"
    for attempt in range(NUM_RETRIES):
        try:
            r = requests.get(url, timeout=60)
            r.raise_for_status()
            return r.json()
        except (requests.RequestException, ValueError) as exc:
            if attempt == NUM_RETRIES - 1:
                raise
            wait = DELAY_SECONDS * (2 ** attempt)
            if not quiet:
                print(f"\n  retry {attempt + 1}/{NUM_RETRIES - 1} for {path}: "
                      f"{type(exc).__name__}; sleeping {wait:.1f}s")
            time.sleep(wait)


def fetch_all_authors():
    return get_json("author")["authors"]


def _as_poem_list(payload):
    """PoetryDB signals 'no match' with a dict body rather than an HTTP error."""
    return [] if isinstance(payload, dict) else payload


def fetch_poems_by_author(author: str):
    """All poems by one author, bulk if the server will serve it.

    Falls back to one request per title when the bulk payload fails, which is
    what happens for the most prolific authors.
    """
    quoted = requests.utils.quote(author)
    try:
        return _as_poem_list(get_json(f"author/{quoted}"))
    except (requests.RequestException, ValueError):
        pass

    print(f"\n  bulk fetch failed for {author!r}; falling back to per-title")
    titles = [t["title"] for t in _as_poem_list(get_json(f"author/{quoted}/title"))]
    print(f"  {author!r}: {len(titles)} titles to fetch individually")

    poems = []
    for title in tqdm(titles, desc=f"  {author}", leave=False):
        time.sleep(DELAY_SECONDS)
        try:
            path = f"author,title/{quoted};{requests.utils.quote(title)}"
            poems.extend(_as_poem_list(get_json(path, quiet=True)))
        except (requests.RequestException, ValueError) as exc:
            print(f"\n  skipped {author!r} / {title!r}: {type(exc).__name__}")
    return poems


def fetch_poems_cached(author: str):
    """fetch_poems_by_author, memoised on disk."""
    cache_path = CACHE_DIR / f"{_hash(author)}.json"
    if cache_path.exists():
        return json.loads(cache_path.read_text()), True

    poems = fetch_poems_by_author(author)
    cache_path.write_text(json.dumps(poems))
    return poems, False


def poem_id(author: str, title: str) -> str:
    """Stable 12-hex-character id, so reruns keep the same identifiers."""
    return _hash(author, title)[:12]


def main():
    authors = fetch_all_authors()
    print(f"Found {len(authors)} authors")

    retrieved_at = datetime.now(timezone.utc).isoformat()
    records = []
    empty_authors = []
    failed_authors = []
    n_cached = 0

    for author in tqdm(authors, desc="authors"):
        try:
            poems, was_cached = fetch_poems_cached(author)
        except Exception as exc:  # one bad author must not lose the whole run
            print(f"\n  FAILED {author!r}: {type(exc).__name__}: {exc}")
            failed_authors.append(author)
            continue

        n_cached += was_cached
        if not poems:
            empty_authors.append(author)

        for poem in poems:
            lines = poem.get("lines", [])
            title = poem.get("title")
            records.append({
                "source": "PoetryDB",
                "poem_id": poem_id(poem.get("author", author), title),
                "title": title,
                "author": poem.get("author", author),
                # PoetryDB's own count: non-blank lines only.
                "linecount": int(poem.get("linecount", 0)),
                # Every element, blanks included, so stanza breaks survive.
                "lines": lines,
                "n_raw_lines": len(lines),
                "text": "\n".join(lines),
                "retrieved_at": retrieved_at,
            })

        if not was_cached:
            time.sleep(DELAY_SECONDS)

    df = pd.DataFrame(records)

    # The same poem can surface under more than one author query; drop dupes.
    before = len(df)
    df = df.drop_duplicates(subset="poem_id").reset_index(drop=True)

    df.to_parquet(OUT_DIR / "poetrydb_full.parquet", index=False)
    df.to_csv(OUT_DIR / "poetrydb_full.csv", index=False)

    print(f"\nSaved {len(df)} poems by {df.author.nunique()} authors "
          f"({before - len(df)} duplicate ids dropped; "
          f"{n_cached}/{len(authors)} authors served from cache)")
    if empty_authors:
        print(f"Authors returning no poems: {empty_authors}")
    if failed_authors:
        print(f"Authors that FAILED and are missing from the corpus: {failed_authors}")
        print("Rerun the script to retry only these.")


if __name__ == "__main__":
    main()
