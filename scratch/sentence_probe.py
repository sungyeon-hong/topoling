"""Is a poem's line a sentence? And would sentence-level clouds have points?

Written 2026-11-06 for the task-8 segmentation decision. It answers the two
questions that decided how poems and prose are cut into points:

1. **Where does a line sit relative to a sentence?** If lineation is a partition
   imposed on running syntax, then cutting prose sub-sententially is the
   faithful analogue of what a poem does to itself, rather than a mutilation of
   prose. Measured over 121,544 lines: 68.0% of lines sit wholly inside a
   sentence, 21.6% end at a boundary, 10.4% straddle one.
2. **How many sentences does a poem have?** Sentence-against-sentence is only
   available where a sentence-level cloud still has points. Median sentences
   per poem, Dickinson excluded: refrain_song 15, irregular 12, ballad_stanza 7,
   sonnet 4 -- the last below the 4-point minimum in src/3_embed_text.py.

Conclusions are in `backlog/docs/task-8-segmentation-rule.md`; this script
exists so those numbers can be re-derived.

**This is a probe, not pipeline code.** It samples the first N authors
alphabetically rather than the Phase 0 stratified sample, because it was run
before data/ was regenerated. Point it at the real sample when data/ exists --
see `use_phase0_sample` below -- and amend the findings document if the arm
medians move.

Responses are cached under scratch/data/, which is gitignored. Run from the
project root:

    uv run python scratch/sentence_probe.py
"""

import json
import re
import sys
import time
from collections import Counter
from pathlib import Path

import pandas as pd
import requests

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from poetry_forms import (                                   # noqa: E402
    PHASE0_FORMS, is_wrap_fragment, label_forms,
)

CACHE = Path("scratch/data/sentence_probe_cache")
OUT_DIR = Path("scratch/output")
SAMPLE = Path("data/processed/poetry_phase0_sample.parquet")

BASE_URL = "https://poetrydb.org"
DELAY_SECONDS = 0.5          # PoetryDB publishes no rate limit; be kind anyway

# Enough authors to populate all four arms without hammering a free API. The
# most prolific (Byron, Shelley) 503 on the bulk endpoint and are skipped
# rather than re-fetched per title: this is a distributional probe, not the
# corpus. src/collect_poetrydb_corpus.py is the real collector.
N_AUTHORS = 40

# src/3_embed_text.py refuses to build a cloud below this many points.
MIN_POINTS = 4
# Minimum sentences for a poem to enter the sentence-level comparison. Above
# the 4-point minimum, well below the 25-point H1 floor -- which does not bind,
# because the task-8 claim is H0-only.
SENTENCE_FLOOR = 8

# Three notions of a sentence boundary. "strict" is the real one; the others
# measure how much dash-heavy punctuation (Dickinson) changes the answer.
BOUNDARY = {
    "strict": r"(?<=[.!?])\s+",
    "semi":   r"(?<=[.!?;])\s+",
    "dash":   r"(?<=[.!?;])\s+|\s+[—–-]{1,2}\s+",
}

TERMINAL = re.compile(r"[.!?]")
# Closing quotes and brackets may trail the stop: "and so he fell." )
TRAILING = ' "\'’”)]'


def get_json(path: str):
    r = requests.get(f"{BASE_URL}/{path}", timeout=60)
    r.raise_for_status()
    return r.json()


def fetch_author(author: str) -> list:
    """Bulk poems for one author, cached on disk. [] if the bulk call fails."""
    CACHE.mkdir(parents=True, exist_ok=True)
    key = CACHE / (re.sub(r"\W+", "_", author) + ".json")
    if key.exists():
        return json.loads(key.read_text())

    try:
        payload = get_json(f"author/{requests.utils.quote(author)}")
        # PoetryDB signals 'no match' with a dict body rather than an error.
        poems = [] if isinstance(payload, dict) else payload
    except (requests.RequestException, ValueError):
        poems = []                 # prolific authors 503; skip, do not per-title
    key.write_text(json.dumps(poems))
    time.sleep(DELAY_SECONDS)
    return poems


def verse_lines(lines) -> list[str]:
    """Same rule as src/3_embed_text.py: non-blank, not a wrap continuation."""
    return [l.strip() for l in lines if l.strip() and not is_wrap_fragment(l)]


def sentences(text: str, mode: str = "strict") -> list[str]:
    return [s.strip() for s in re.split(BOUNDARY[mode], text) if s.strip()]


def line_position(line: str) -> str:
    """Does this line end a sentence, sit inside one, or straddle a boundary?"""
    hits = list(TERMINAL.finditer(line))
    if not hits:
        return "inside_sentence"
    end_of_line = len(line.rstrip(TRAILING))
    return ("ends_at_boundary" if all(h.end() >= end_of_line - 1 for h in hits)
            else "straddles")


def load_poems(use_phase0_sample: bool) -> pd.DataFrame:
    """The Phase 0 sample if it exists and is asked for, else an author slice."""
    if use_phase0_sample and SAMPLE.exists():
        print(f"Using the Phase 0 stratified sample: {SAMPLE}")
        return pd.read_parquet(SAMPLE)

    authors = get_json("author")["authors"][:N_AUTHORS]
    print(f"Probing the first {len(authors)} authors alphabetically "
          "(NOT the Phase 0 sample)")
    rows = [
        {"poem_id": f"{p.get('author', a)}|{p.get('title')}",
         "title": p.get("title"), "author": p.get("author", a),
         "linecount": int(p.get("linecount", 0)), "lines": p.get("lines", [])}
        for a in authors for p in fetch_author(a)
    ]
    return pd.DataFrame(rows).drop_duplicates(subset="poem_id").reset_index(drop=True)


def main(use_phase0_sample: bool = False):
    df = load_poems(use_phase0_sample)
    print(f"{len(df)} poems by {df.author.nunique()} authors")

    if "form_family" not in df.columns:
        df = label_forms(df)
    df = df[df.form_family.isin(PHASE0_FORMS)].copy()
    print(f"{len(df)} in the four Phase 0 arms\n")

    positions, recs = Counter(), []
    for rec in df.itertuples():
        lines = verse_lines(rec.lines)
        if not lines:
            continue
        for line in lines:
            positions[line_position(line)] += 1

        text = " ".join(lines)
        n_words = len(text.split())
        row = {
            "form_family": rec.form_family, "author": rec.author,
            "n_lines": len(lines), "n_distinct_lines": len(set(lines)),
            "words": n_words, "words_per_line": n_words / len(lines),
            "has_terminal_punct": bool(TERMINAL.search(text)),
            # Dickinson is ~34% of an alphabetical slice and her short,
            # dash-punctuated poems halve two arm medians. The Phase 0 sampler
            # caps any author at five poems, so the excluding-her figures are
            # the better proxy for what will actually be measured.
            "is_dickinson": "Dickinson" in str(rec.author),
        }
        for mode in BOUNDARY:
            sents = sentences(text, mode)
            row[f"n_sent_{mode}"] = len(sents)
            row[f"wps_{mode}"] = n_words / len(sents) if sents else float("nan")
        recs.append(row)

    out = pd.DataFrame(recs)
    pd.set_option("display.width", 200)

    total = sum(positions.values())
    print("=== WHERE A POEM'S LINE SITS RELATIVE TO SENTENCES ===")
    print("(the premise: is lineation a partition imposed on running syntax?)\n")
    for key in ("ends_at_boundary", "inside_sentence", "straddles"):
        print(f"  {key:20s} {positions[key]:7d}  {100 * positions[key] / total:5.1f}%")
    print(f"  {'total lines':20s} {total:7d}")

    print("\n\n=== POINTS PER CLOUD, by arm ===")
    print("(lines = the current unit; sent_* = what sentence-splitting leaves)\n")
    for label, sub in (("ALL", out), ("EXCLUDING DICKINSON", out[~out.is_dickinson])):
        print(f"--- {label} ---")
        print(sub.groupby("form_family").agg(
            n_poems=("n_lines", "size"),
            med_lines=("n_distinct_lines", "median"),
            med_sent=("n_sent_strict", "median"),
            med_words_per_line=("words_per_line", "median"),
            med_words_per_sent=("wps_strict", "median"),
        ).round(1).to_string(), end="\n\n")

    print(f"=== SHARE OF POEMS RETAINED AT EACH FLOOR (excluding Dickinson) ===")
    print(f"(the {MIN_POINTS}-point minimum is src/3_embed_text.py's; "
          f"{SENTENCE_FLOOR} is the sentence-level entry bar)\n")
    print(out[~out.is_dickinson].groupby("form_family").apply(
        lambda g: pd.Series({
            "n_poems": len(g),
            f"lines >= {MIN_POINTS} %": round(100 * (g.n_distinct_lines >= MIN_POINTS).mean(), 1),
            f"sent >= {MIN_POINTS} %": round(100 * (g.n_sent_strict >= MIN_POINTS).mean(), 1),
            f"sent >= {SENTENCE_FLOOR} %": round(100 * (g.n_sent_strict >= SENTENCE_FLOOR).mean(), 1),
            "sent >= 12 %": round(100 * (g.n_sent_strict >= 12).mean(), 1),
        }), include_groups=False).to_string())

    print("\n\n=== PUNCTUATION RELIABILITY ===")
    print("(the objection that dash-punctuated verse cannot be split)\n")
    unpunctuated = out[~out.has_terminal_punct]
    print(f"  poems with no .!? at all: {len(unpunctuated)} / {len(out)} "
          f"({100 * len(unpunctuated) / len(out):.1f}%)")
    if len(unpunctuated):
        print(f"  most affected: {Counter(unpunctuated.author).most_common(5)}")

    per_author = out.groupby("author").agg(
        n=("n_lines", "size"), med_sent=("n_sent_strict", "median"))
    suspect = per_author[(per_author.n >= 5) & (per_author.med_sent < 3)]
    print("\n  authors where splitting looks suspect (>= 5 poems, median < 3 "
          f"sentences): {len(suspect)}")
    print(suspect.to_string() if len(suspect) else "    none")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    dest = OUT_DIR / "sentence_probe.csv"
    out.to_csv(dest, index=False)
    print(f"\nPer-poem rows written to {dest}")


if __name__ == "__main__":
    main(use_phase0_sample="--phase0-sample" in sys.argv)
