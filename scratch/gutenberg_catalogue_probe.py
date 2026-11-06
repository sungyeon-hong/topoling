"""Which PoetryDB poets have non-fiction prose on Project Gutenberg?

Written 2026-11-06 for task-8, to choose the poets whose letters and essays
form the same-author prose corpus. Findings are in
`backlog/docs/task-8-prose-sources.md`; this script exists so the table there
can be re-derived when Gutenberg's catalogue grows.

It reads Gutenberg's own catalogue file (the one Gutendex is built from; the
Gutendex API took ~77 s per request when tried). Download it once:

    mkdir -p scratch/data/gutenberg
    curl -o scratch/data/gutenberg/pg_catalog.csv \
        https://www.gutenberg.org/cache/epub/feeds/pg_catalog.csv

then run from the project root:

    uv run python scratch/gutenberg_catalogue_probe.py

The tags are keyword hints from subjects, shelves and titles, not a
classification: every title was judged by hand for the findings document.
Name patterns can mis-match -- "Herrick, Robert" finds the American novelist,
not the poet -- so check authorship before using any hit.
"""

from pathlib import Path

import re

import pandas as pd

CAT = Path("scratch/data/gutenberg/pg_catalog.csv")
OUT = Path("scratch/output/gutenberg_poet_books.csv")

cat = pd.read_csv(CAT, dtype=str).fillna("")
cat = cat[(cat.Type=="Text") & (cat.Language.str.contains("en"))]
# PoetryDB authors with >=20 poems -> Gutenberg author-name regex (surname, given)
POETS = {
 "Emily Dickinson": r"Dickinson, Emily", "George Gordon, Lord Byron": r"Byron, George Gordon",
 "Percy Bysshe Shelley": r"Shelley, Percy Bysshe", "William Shakespeare": r"Shakespeare, William",
 "Edward Thomas": r"Thomas, Edward, 1878", "John Clare": r"Clare, John", "Robert Burns": r"Burns, Robert, 1759",
 "William Topaz McGonagall": r"McGonagall", "Walt Whitman": r"Whitman, Walt", "Robert Browning": r"Browning, Robert",
 "Alexander Pope": r"Pope, Alexander", "Robert Herrick": r"Herrick, Robert", "Robinson": r"Robinson, Mary, 1758",
 "William Blake": r"Blake, William, 1757", "Edgar Allan Poe": r"Poe, Edgar Allan", "Lord Alfred Tennyson": r"Tennyson, Alfred",
 "Robert Louis Stevenson": r"Stevenson, Robert Louis", "Michael Drayton": r"Drayton, Michael",
 "Algernon Charles Swinburne": r"Swinburne, Algernon", "Henry Wadsworth Longfellow": r"Longfellow, Henry Wadsworth",
 "Elizabeth Barrett Browning": r"Browning, Elizabeth Barrett", "Eugene Field": r"Field, Eugene", "Thomas Moore": r"Moore, Thomas, 1779",
 "Geoffrey Chaucer": r"Chaucer, Geoffrey", "John Donne": r"Donne, John", "Gerard Manley Hopkins": r"Hopkins, Gerard Manley",
 "John Milton": r"Milton, John", "Rupert Brooke": r"Brooke, Rupert", "John Keats": r"Keats, John",
 "Stephen Crane": r"Crane, Stephen", "Samuel Coleridge": r"Coleridge, Samuel Taylor", "William Cowper": r"Cowper, William",
}
def tag(r):
    s = (r.Subjects+" | "+r.LoCC+" | "+r.Bookshelves+" | "+r.Title).lower()
    t=[]
    if re.search(r"correspondence|letters|journal|diar|autobiograph", s): t.append("LETTERS/LIFE")
    if re.search(r"essays|criticism|prose|lecture|preface|literature -- history", s): t.append("ESSAY")
    if re.search(r"fiction|novel|short stories|tales", s): t.append("fiction")
    if re.search(r"drama|plays|tragedies|comedies", s): t.append("drama")
    if re.search(r"poetry|poems|verse|poetical|sonnets|songs", s): t.append("poetry")
    return ",".join(t) or "?"
rows=[]
for poet, pat in POETS.items():
    sub = cat[cat.Authors.str.contains(pat, regex=True)]
    for r in sub.itertuples():
        # role of the poet in this record
        m = re.search(r"(?:%s)[^;]*" % pat, r.Authors); role = re.findall(r"\[([^\]]+)\]", m.group(0)) if m else []
        rows.append(dict(poet=poet, id=r._1, title=r.Title.replace("\n"," ")[:110], role=";".join(role) or "Author",
                         tags=tag(r), shelves=r.Bookshelves[:80]))
out = pd.DataFrame(rows); OUT.parent.mkdir(parents=True, exist_ok=True); out.to_csv(OUT, index=False)
print(out.groupby("poet").size().sort_values().to_string())
