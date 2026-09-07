import arxiv
import pandas as pd
from pathlib import Path
from tqdm import tqdm

OUT = Path("data/raw")
OUT.mkdir(parents=True, exist_ok=True)

client = arxiv.Client(
    page_size=100,
    delay_seconds=3,
    num_retries=5
)

def collect_category(category: str, max_results: int = 5000):
    search = arxiv.Search(
        query=f"cat:{category}",
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate,
        sort_order=arxiv.SortOrder.Ascending
    )

    rows = []

    for paper in tqdm(client.results(search), desc=category):
        rows.append({
            "arxiv_id": paper.entry_id.split("/")[-1],
            "entry_id": paper.entry_id,
            "title": paper.title,
            "summary": paper.summary,
            "published": paper.published,
            "updated": paper.updated,
            "primary_category": paper.primary_category,
            "categories": list(paper.categories),
            "authors": [a.name for a in paper.authors],
            "doi": paper.doi,
            "journal_ref": paper.journal_ref,
            "pdf_url": paper.pdf_url,
            "comment": paper.comment,
        })

    df = pd.DataFrame(rows)
    df.to_parquet(OUT / f"arxiv_{category.replace('.', '_')}.parquet", index=False)
    return df

if __name__ == "__main__":
    collect_category("math.AT", max_results=5000)
