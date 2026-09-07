"""Mechanical form detection and form-stratified sampling for Phase 0.

Phase 0 uses fixed poetic forms as ground truth: a villanelle repeats two
refrains verbatim, so those lines are near-duplicate points in embedding space
and should show a predictable H0/H1 signature; a sonnet is 14 lines with a
volta near line 8-9. PoetryDB carries no form labels, but form is recoverable
from structure alone -- line count, stanza lengths, and exactly repeated lines
-- so nothing here needs hand-labelling.

Two structural facts about PoetryDB make this work. Its `linecount` field
counts only non-blank lines, and the blank lines that remain in the `lines`
array are stanza separators. So stanza structure is free.

One finding from the full pull constrains the Phase 0 design. **PoetryDB
contains no villanelles.** Of 3092 poems, 22 have the villanelle's 19 lines and
none of those carries two recurring refrains. This is expected rather than a
detection failure: the villanelle only became a common English form in the
twentieth century, and PoetryDB holds public-domain material that predates it.
The villanelle detector below is kept because it is correct and costs nothing,
but the near-duplicate-line geometry villanelles were wanted for is supplied
instead by `refrain_song` -- songs and hymns whose chorus recurs verbatim.
Those are longer, so unlike villanelles they also clear the H1 point floor.

This module is importable (unlike the digit-prefixed pipeline scripts). Run it
directly to label the full corpus and write a stratified Phase 0 sample:

    uv run python src/poetry_forms.py
"""

import re
import unicodedata
from collections import Counter
from pathlib import Path

import pandas as pd

RAW_PATH = Path("data/raw/poetrydb_full.parquet")
OUT_DIR = Path("data/processed")

# A line repeated this many times is a refrain rather than a coincidence.
REFRAIN_MIN_REPEATS = 3
# A villanelle's two refrains recur across its five tercets and final quatrain.
VILLANELLE_LINECOUNT = 19
VILLANELLE_STANZAS = (3, 3, 3, 3, 3, 4)
SONNET_LINECOUNT = 14

# CLAUDE.md sets a floor of ~25 points below which no document-level H1 claim
# is made: Vietoris-Rips H1 on a handful of points in high dimension is
# sampling noise. Line-level clouds smaller than this cannot carry an H1 claim.
H1_POINT_FLOOR = 25

# PoetryDB wraps long lines, leaving indented continuation fragments -- a line
# of Whitman can trail off into entries like "  the" and "    of". These are
# not lines of verse. They matter twice over: they register as repeated
# refrains, and because Phase 0 embeds one line per point, each fragment would
# become a meaningless point in the cloud.
MIN_REFRAIN_WORDS = 3          # content floor for a repeat to count as a refrain
WRAP_FRAGMENT_MAX_WORDS = 4    # an indented line this short is a continuation
MAX_WRAP_FRACTION = 0.10       # poems wrapped worse than this leave the sample


# --------------------------------------------------------------------------
# structure
# --------------------------------------------------------------------------

def normalise_line(line: str) -> str:
    """Fold a line to a key for exact-repeat detection.

    Refrains recur with drifting punctuation and capitalisation, so those are
    stripped; word content is left untouched.
    """
    line = unicodedata.normalize("NFKD", line).lower()
    line = re.sub(r"[^\w\s]", "", line)
    return re.sub(r"\s+", " ", line).strip()


def split_stanzas(lines) -> list[list[str]]:
    """Split on blank lines into stanzas of non-blank lines."""
    stanzas, current = [], []
    for line in lines:
        if line.strip():
            current.append(line)
        elif current:
            stanzas.append(current)
            current = []
    if current:
        stanzas.append(current)
    return stanzas


def line_repeats(lines) -> Counter:
    """How often each distinct normalised line occurs."""
    return Counter(
        key for key in (normalise_line(l) for l in lines) if key
    )


def is_wrap_fragment(line: str) -> bool:
    """Is this an indented continuation of the previous line rather than a line?"""
    return (line.startswith("  ")
            and 0 < len(normalise_line(line).split()) <= WRAP_FRAGMENT_MAX_WORDS)


def describe_structure(lines) -> dict:
    """Structural features of one poem, before any form label is applied."""
    stanzas = split_stanzas(lines)
    profile = tuple(len(s) for s in stanzas)
    repeats = line_repeats(lines)
    n_lines = sum(repeats.values())

    # A refrain must carry enough words to be one; see MIN_REFRAIN_WORDS.
    refrains = {
        k: v for k, v in repeats.items()
        if v >= REFRAIN_MIN_REPEATS and len(k.split()) >= MIN_REFRAIN_WORDS
    }

    non_blank = [l for l in lines if l.strip()]
    n_fragments = sum(1 for l in non_blank if is_wrap_fragment(l))
    # Lines that are a second-or-later occurrence of something already said.
    n_repeated_lines = sum(v - 1 for v in repeats.values() if v > 1)

    return {
        "n_stanzas": len(stanzas),
        "stanza_profile": profile,
        "modal_stanza_len": Counter(profile).most_common(1)[0][0] if profile else 0,
        "uniform_stanzas": len(set(profile)) == 1 and len(profile) > 1,
        "n_distinct_lines": len(repeats),
        "n_refrains": len(refrains),
        "max_line_repeats": max(repeats.values()) if repeats else 0,
        # Share of lines that merely restate an earlier line. This is the
        # quantity the topology should see as near-duplicate points.
        "repeat_fraction": n_repeated_lines / n_lines if n_lines else 0.0,
        "meets_h1_floor": n_lines >= H1_POINT_FLOOR,
        "n_wrap_fragments": n_fragments,
        "wrap_fraction": n_fragments / len(non_blank) if non_blank else 0.0,
    }


# --------------------------------------------------------------------------
# form labels
# --------------------------------------------------------------------------

def sonnet_subtype(profile: tuple) -> str:
    """Shakespearean and Petrarchan sonnets differ in where the volta falls."""
    if profile in {(4, 4, 4, 2), (12, 2)}:
        return "sonnet_shakespearean"
    if profile in {(8, 6), (4, 4, 3, 3), (4, 4, 6)}:
        return "sonnet_petrarchan"
    return "sonnet_unsplit" if len(profile) <= 1 else "sonnet_other"


def classify_form(row) -> str:
    """One primary form label per poem, by explicit precedence.

    Precedence matters and is not arbitrary: villanelle before sonnet before
    refrain_song, because the earlier labels are the more specific structural
    claims. A poem gets exactly one label; the underlying features stay
    available as columns for anyone who wants to slice differently.
    """
    profile = tuple(row["stanza_profile"])
    n = row["linecount"]

    if (n == VILLANELLE_LINECOUNT
            and row["n_refrains"] >= 2
            and profile == VILLANELLE_STANZAS):
        return "villanelle"

    # 19 lines with genuine refrains but an irregular stanza layout.
    if n == VILLANELLE_LINECOUNT and row["n_refrains"] >= 2:
        return "villanelle_like"

    if n == SONNET_LINECOUNT:
        return sonnet_subtype(profile)

    # Songs and hymns with a chorus: the same near-duplicate geometry as a
    # villanelle, but without the fixed length. A much larger class here.
    if row["n_refrains"] >= 1:
        return "refrain_song"

    if row["n_stanzas"] >= 3 and row["uniform_stanzas"]:
        if row["modal_stanza_len"] == 4:
            return "ballad_stanza"
        if row["modal_stanza_len"] == 2:
            return "couplets"
        return "regular_stanzaic"

    if row["n_stanzas"] <= 1:
        return "single_block"

    return "irregular"


# Sonnet subtypes are one arm for sampling; the subtype stays in `form` for
# anyone who wants to split Shakespearean from Petrarchan later. Printing a
# sonnet as an unbroken block is the normal convention for sequences
# (Shakespeare, Donne, Drayton, Barrett Browning), so `sonnet_unsplit` belongs
# here rather than being treated as proxy noise.
FORM_FAMILY = {
    "sonnet_shakespearean": "sonnet",
    "sonnet_petrarchan": "sonnet",
    "sonnet_unsplit": "sonnet",
    "sonnet_other": "sonnet",
    "villanelle": "villanelle",
    "villanelle_like": "villanelle",
}

# The four contrasting arms Phase 0 can actually build from PoetryDB:
# a fixed-length form with a volta; verbatim refrain repetition; regular
# quatrains without refrains; and no regular structure at all.
PHASE0_FORMS = ["sonnet", "refrain_song", "ballad_stanza", "irregular"]


def label_forms(df: pd.DataFrame) -> pd.DataFrame:
    """Attach structural features and a primary form label to every poem."""
    features = pd.DataFrame(
        [describe_structure(lines) for lines in df["lines"]],
        index=df.index,
    )
    out = pd.concat([df, features], axis=1)
    out["form"] = out.apply(classify_form, axis=1)
    out["form_family"] = out["form"].map(FORM_FAMILY).fillna(out["form"])
    return out


# --------------------------------------------------------------------------
# stratified sampling
# --------------------------------------------------------------------------

def stratified_sample(
    df: pd.DataFrame,
    forms: list[str],
    per_form: int = 60,
    max_per_author: int = 5,
    seed: int = 0,
    column: str = "form_family",
) -> pd.DataFrame:
    """Sample up to `per_form` poems of each form, spreading across authors.

    The author cap is the point of this function. The earlier pilot took the
    first 100 titles in PoetryDB's default order and got 71 Robert Burns
    poems; any topological difference found in such a sample confounds form
    with authorial voice.
    """
    chunks = []
    for form in forms:
        pool = df[df[column] == form]
        if pool.empty:
            continue
        # Shuffle first, then take at most `max_per_author` per author, so the
        # cap falls on a random subset of each author's poems rather than the
        # alphabetically first ones.
        shuffled = pool.sample(frac=1.0, random_state=seed)
        capped = shuffled.groupby("author", group_keys=False, sort=False).head(max_per_author)
        chunks.append(capped.head(per_form))

    if not chunks:
        return df.iloc[0:0]
    return pd.concat(chunks).reset_index(drop=True)


# --------------------------------------------------------------------------

def main():
    if not RAW_PATH.exists():
        raise SystemExit(
            f"{RAW_PATH} not found. Run src/collect_poetrydb_corpus.py first."
        )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_parquet(RAW_PATH)
    labelled = label_forms(df)
    labelled.to_parquet(OUT_DIR / "poetrydb_labelled.parquet", index=False)

    print(f"Labelled {len(labelled)} poems by {labelled.author.nunique()} authors\n")
    print("--- full corpus by form ---")
    print(labelled.groupby("form").agg(
        n=("poem_id", "size"),
        authors=("author", "nunique"),
        median_lines=("linecount", "median"),
        clears_h1_floor=("meets_h1_floor", "sum"),
    ).sort_values("n", ascending=False).to_string())

    # Poems whose text is badly line-wrapped would contribute fragment points
    # to the line-level cloud, so they are held out of the sample rather than
    # silently embedded.
    eligible = labelled[labelled.wrap_fraction <= MAX_WRAP_FRACTION]
    n_dropped = len(labelled) - len(eligible)
    print(f"\nHeld out {n_dropped} poems wrapped worse than "
          f"{MAX_WRAP_FRACTION:.0%} (fragment lines are not verse lines)")

    sample = stratified_sample(eligible, PHASE0_FORMS)
    sample.to_parquet(OUT_DIR / "poetry_phase0_sample.parquet", index=False)

    print(f"\n--- Phase 0 stratified sample ({len(sample)} poems) ---")
    print(sample.groupby("form_family").agg(
        n=("poem_id", "size"),
        authors=("author", "nunique"),
        median_lines=("linecount", "median"),
        median_repeat_frac=("repeat_fraction", "median"),
        clears_h1_floor=("meets_h1_floor", "sum"),
    ).to_string())

    top = sample.author.value_counts()
    print(f"\nAuthor concentration: {sample.author.nunique()} authors, "
          f"largest share {top.iloc[0]}/{len(sample)} "
          f"({100 * top.iloc[0] / len(sample):.0f}%) — {top.index[0]}")
    print("  (the earlier 100-poem pilot was 71% Robert Burns)")

    print(f"\nDocument-level H1 needs >= {H1_POINT_FLOOR} lines. Sonnets are 14 "
          "lines by definition and can never clear it, so the sonnet arm\n"
          "supports H0 and volta structure only. Decide per arm, not globally.")


if __name__ == "__main__":
    main()
