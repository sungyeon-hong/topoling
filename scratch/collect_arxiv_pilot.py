from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path

import arxiv
import pandas as pd
from tqdm import tqdm


OUT_DIR = Path("data/raw")
OUT_DIR.mkdir(parents=True, exist_ok=True)

CATEGORY = "math.CO"
START_DATE = "200001010000"
END_DATE = "200012312359"
MAX_RESULTS = 100


def normalize_whitespace(text: str | None) -> str:
    if not text:
        return ""
    return re.sub(r"\s+", " ", text).strip()


def strip_version(arxiv_id: str) -> str:
    return re.sub(r"v\d+$", "", arxiv_id)


def extract_version(arxiv_id: str) -> int | None:
    match = re.search(r"v(\d+)$", arxiv_id)
    return int(match.group(1)) if match else None


def paper_to_record(paper: arxiv.Result) -> dict:
    arxiv_id_versioned = paper.entry_id.rstrip("/").split("/")[-1]
    arxiv_id = strip_version(arxiv_id_versioned)

    title = normalize_whitespace(paper.title)
    abstract = normalize_whitespace(paper.summary)
    text_title_abstract = normalize_whitespace(f"{title}. {abstract}")

    return {
        "arxiv_id": arxiv_id,
        "arxiv_id_versioned": arxiv_id_versioned,
        "version": extract_version(arxiv_id_versioned),
        "entry_id": paper.entry_id,
        "title": title,
        "abstract": abstract,
        "text_title_abstract": text_title_abstract,
        "published": paper.published,
        "updated": paper.updated,
        "year": paper.published.year if paper.published else None,
        "month": paper.published.strftime("%Y-%m") if paper.published else None,
        "primary_category": paper.primary_category,
        "categories": list(paper.categories),
        "authors": [a.name for a in paper.authors],
        "doi": paper.doi,
        "journal_ref": paper.journal_ref,
        "comment": paper.comment,
        "pdf_url": paper.pdf_url,
        "is_withdrawn": "withdrawn" in text_title_abstract.lower(),
        "source": "arxiv_api",
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
    }


def main() -> None:
    query = (
        f"cat:{CATEGORY} "
        f"AND submittedDate:[{START_DATE} TO {END_DATE}]"
    )

    client = arxiv.Client(
        page_size=25,
        delay_seconds=5.0,
        num_retries=10,
    )

    search = arxiv.Search(
        query=query,
        max_results=MAX_RESULTS,
        sort_by=arxiv.SortCriterion.SubmittedDate,
        sort_order=arxiv.SortOrder.Ascending,
    )

    print(f"Running pilot query: {query}")
    print(f"Maximum records requested: {MAX_RESULTS}")

    records = []

    for paper in tqdm(client.results(search), desc="Collecting pilot records"):
        records.append(paper_to_record(paper))

    df = pd.DataFrame(records)

    if df.empty:
        print("No records collected.")
        return

    df["published"] = pd.to_datetime(df["published"], utc=True)
    df["updated"] = pd.to_datetime(df["updated"], utc=True)

    df = (
        df.sort_values(["arxiv_id", "published", "updated"])
        .drop_duplicates(subset=["arxiv_id"], keep="first")
        .reset_index(drop=True)
    )

    parquet_path = OUT_DIR / "arxiv_math_CO_2000_pilot.parquet"
    csv_path = OUT_DIR / "arxiv_math_CO_2000_pilot.csv"

    df.to_parquet(parquet_path, index=False)
    df.to_csv(csv_path, index=False)

    print("\nPilot complete.")
    print(f"Records collected: {len(df)}")
    print(f"Date range: {df['published'].min()} to {df['published'].max()}")
    print(f"Withdrawn-marked records: {df['is_withdrawn'].sum()}")

    print("\nRecords by year:")
    print(df.groupby("year").size().to_string())

    print("\nPrimary categories:")
    print(df["primary_category"].value_counts().to_string())

    print(f"\nSaved Parquet: {parquet_path}")
    print(f"Saved CSV: {csv_path}")


if __name__ == "__main__":
    main()
