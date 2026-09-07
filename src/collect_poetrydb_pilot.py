from pathlib import Path
from datetime import datetime, timezone

import requests
import pandas as pd


OUT_DIR = Path("data/raw")
OUT_DIR.mkdir(parents=True, exist_ok=True)

BASE_URL = "https://poetrydb.org"


def fetch_all_titles():
    r = requests.get(f"{BASE_URL}/title", timeout=60)
    r.raise_for_status()
    return r.json()["titles"]


def fetch_poem_by_title(title: str):
    url_title = requests.utils.quote(title)
    r = requests.get(f"{BASE_URL}/title/{url_title}", timeout=60)
    r.raise_for_status()
    return r.json()


def main():
    records = []
    titles = fetch_all_titles()

    print(f"Found {len(titles)} titles")

    for title in titles[:100]:  # small pilot
        poems = fetch_poem_by_title(title)

        for poem in poems:
            lines = poem.get("lines", [])
            text = "\n".join(lines)

            records.append({
                "source": "PoetryDB",
                "title": poem.get("title"),
                "author": poem.get("author"),
                "linecount": int(poem.get("linecount", 0)),
                "lines": lines,
                "text": text,
                "retrieved_at": datetime.now(timezone.utc).isoformat(),
            })

    df = pd.DataFrame(records)
    df.to_parquet(OUT_DIR / "poetrydb_pilot.parquet", index=False)
    df.to_csv(OUT_DIR / "poetrydb_pilot.csv", index=False)

    print(f"Saved {len(df)} poems")


if __name__ == "__main__":
    main()
