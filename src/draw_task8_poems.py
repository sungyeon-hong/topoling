"""The seeded draw of poems for task-8, the poem-versus-same-author-prose test.

Implements the selection rule fixed on 2026-11-06 in
`backlog/docs/task-8-segmentation-rule.md` ("Which poems and which prose"):

- the 12 first-pass poets;
- eligible poems: wrap fraction <= MAX_WRAP_FRACTION, and 4-200 *distinct*
  lines after wrap fragments are dropped (what the persistence diagram sees);
- 10 poems per poet, uniformly at random, seed 20261106, no redraws.

"No redraws" is enforced by drawing a full ordering of each poet's pool, not
just ten poems. The first ten are the draw. If one later proves unusable (a
duplicate, a translation, ...) it is replaced by the next poem *in that same
ordering*, never by a fresh draw, and the replacement is recorded. The reserve
ranks are written out with the draw so the replacement is fixed now.

Each poet gets an independent generator, seeded from the master seed plus a
CRC32 of the poet's name. CRC32 is deterministic across processes, unlike
Python's hash() (which caused a reproducibility bug in an earlier sweep). Adding
a poet later therefore cannot change any existing poet's draw.

Run from the project root:

    uv run python src/draw_task8_poems.py
"""

import re
import zlib
from pathlib import Path

import numpy as np
import pandas as pd

from poetry_forms import MAX_WRAP_FRACTION, is_wrap_fragment, normalise_line

LABELLED = Path("data/processed/poetrydb_labelled.parquet")
OUT = Path("data/processed/task8_poem_draw.parquet")
# A tracked copy: data/ is gitignored, and the draw should be on the public
# record, dated, before any prose is matched to it.
RECORD = Path("backlog/docs/task-8-poem-draw.csv")

SEED = 20261106
PER_POET = 10
RESERVE = 5                    # reserve ranks written to the record
MIN_LINES, MAX_LINES = 4, 200

POETS = [
    "Percy Bysshe Shelley", "George Gordon, Lord Byron", "Edward Thomas",
    "Robert Burns", "Robert Browning", "Robert Louis Stevenson",
    "Algernon Charles Swinburne", "Elizabeth Barrett Browning",
    "Edgar Allan Poe", "Walt Whitman", "Samuel Coleridge", "John Keats",
]

# Flags for review, never automatic exclusions: the rule says a drawn poem is
# replaced only once it is judged unusable, and that judgement is recorded.
TRANSLATION_HINT = re.compile(
    r"translat|imitat|paraphrase|from the (greek|latin|italian|spanish|german)"
    r"|homer|goethe|calderon|dante|pulci|petrarch|euripides|virgil|horace"
    r"|catullus|anacreon|moschus|bion|theocritus|plato|ariosto|tasso",
    re.IGNORECASE,
)
FRAGMENT_HINT = re.compile(r"fragment", re.IGNORECASE)

# Drawn poems judged unusable on inspection, 2026-11-06, agreed with Sungyeon.
# Each is skipped and the next poem in the same seeded order takes its place.
# Fragments were inspected too and kept: they are the poet's own words, and
# length is already governed by MIN_LINES.
EXCLUDED = {
    "1769943e63a9": "misattributed: Felicia Hemans's 'The Landing of the "
                    "Pilgrim Fathers', not Barrett Browning's",
    "1b5da18259b8": "misattributed: second copy of the Hemans poem",
    "6123f6a513af": "duplicate: same poem as 'Ode To Autumn' under another title",
    "43800496a439": "translation: from the Greek of Moschus",
    "2b0dfe472a41": "translation: from the Greek of Callistratus",
    "afc5780a197b": "translation: from Vittorelli",
    "55ce291db32e": "imitation of Catullus; treated as translation",
}


def verse_lines(lines) -> list[str]:
    """Same rule as src/3_embed_text.py: non-blank, not a wrap continuation."""
    return [l.strip() for l in lines if l.strip() and not is_wrap_fragment(l)]


def first_line_key(lines) -> str:
    """First verse line of three or more words, normalised.

    Catches the same poem stored twice under different titles or headings,
    which an exact-text comparison misses ('Ode To Autumn' / 'To Autumn').
    """
    for line in verse_lines(lines):
        key = normalise_line(line)
        if len(key.split()) >= 3:
            return key
    return ""


def poet_rng(poet: str) -> np.random.Generator:
    return np.random.default_rng([SEED, zlib.crc32(poet.encode("utf-8"))])


def main():
    labelled = pd.read_parquet(LABELLED)

    df = labelled[labelled.author.isin(POETS)].copy()
    df["verse"] = df["lines"].map(verse_lines)
    df["n_distinct"] = df["verse"].map(lambda v: len(set(v)))
    df["n_words"] = df["verse"].map(lambda v: sum(len(l.split()) for l in v))
    # Exact-duplicate texts anywhere in the corpus (PoetryDB carries some
    # poems twice under different titles).
    key = df["verse"].map(lambda v: "\n".join(v))
    corpus_key = labelled["lines"].map(lambda l: "\n".join(verse_lines(l)))
    counts = corpus_key.value_counts()
    df["dup_in_corpus"] = key.map(counts).fillna(1).astype(int) > 1
    first_counts = labelled["lines"].map(first_line_key).value_counts()
    first = df["lines"].map(first_line_key)
    df["shares_first_line"] = (first != "") & (first.map(first_counts) > 1)

    eligible = df[(df.wrap_fraction <= MAX_WRAP_FRACTION)
                  & df.n_distinct.between(MIN_LINES, MAX_LINES)]

    drawn = []
    for poet in POETS:
        # Sort first, so the draw depends on the pool's contents and never on
        # the row order of the parquet file.
        pool = eligible[eligible.author == poet].sort_values("poem_id")
        order = poet_rng(poet).permutation(len(pool))
        ranked = pool.iloc[order].assign(rank=np.arange(1, len(pool) + 1))

        # Walk the seeded order: skip exclusions, take the first PER_POET.
        # A poem taken from beyond rank PER_POET is a replacement.
        status, reason, taken = [], [], 0
        for pid, rank in zip(ranked.poem_id, ranked["rank"]):
            if pid in EXCLUDED:
                status.append("excluded"); reason.append(EXCLUDED[pid])
            elif taken < PER_POET:
                taken += 1
                status.append("drawn" if rank <= PER_POET else "replacement")
                reason.append("")
            else:
                status.append("reserve"); reason.append("")
        ranked = ranked.assign(status=status, excluded_because=reason)
        drawn.append(ranked)
        print(f"{poet:30s} pool {len(pool):4d}  "
              f"excluded {status.count('excluded')}  "
              f"replacements {status.count('replacement')}")
    drawn = pd.concat(drawn, ignore_index=True)

    unknown = set(EXCLUDED) - set(drawn.poem_id)
    if unknown:
        raise SystemExit(f"EXCLUDED names poems not in any pool: {unknown}")

    drawn["flag"] = [
        ";".join(f for f, hit in (
            ("translation?", bool(TRANSLATION_HINT.search(str(t)))),
            ("fragment?", bool(FRAGMENT_HINT.search(str(t)))),
            ("duplicate-text", d),
            ("shares-first-line", s),
        ) if hit)
        for t, d, s in zip(drawn.title, drawn.dup_in_corpus,
                           drawn.shares_first_line)
    ]
    drawn["k"] = (drawn.n_words / drawn.n_distinct).round().astype(int)

    cols = ["author", "rank", "status", "poem_id", "title", "n_distinct",
            "n_words", "k", "form_family", "flag", "excluded_because"]
    drawn[cols + ["lines"]].to_parquet(OUT, index=False)

    RECORD.parent.mkdir(parents=True, exist_ok=True)
    # Every poem in the final selection, every exclusion, and the next
    # RESERVE poems in order, so later replacements are fixed now.
    in_play = drawn.status.isin(["drawn", "replacement", "excluded"])
    upto = drawn.author.map(drawn[in_play].groupby("author")["rank"].max())
    record = drawn[in_play | (drawn["rank"] <= upto + RESERVE)][cols]
    record.to_csv(RECORD, index=False)

    picked = drawn[drawn.status.isin(["drawn", "replacement"])]
    print(f"\n{len(picked)} poems selected, seed {SEED}. "
          f"Full orderings -> {OUT}; record -> {RECORD}")
    print("flagged among the selected:")
    print(picked[picked.flag != ""][["author", "rank", "title", "flag"]]
          .to_string(index=False))


if __name__ == "__main__":
    main()
