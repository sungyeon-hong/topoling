"""Step 5 - persistent homology, against controls matched on point count.

The Phase 0 question is whether persistent homology sees structure in a poem
that is not already explained by how many points the poem has. That last
clause is the whole difficulty. Verbatim refrains collapse to a single point
(see topology.py), so a villanelle with four-fold refrains presents 13 distinct
points where its 19-distinct-line control presents 19 -- and persistence
statistics move with cardinality for entirely trivial reasons.

So every poem is compared against a corpus control drawn to have **the same
number of distinct points**: real lines of real verse, sampled from other
poems, carrying the embedding model's geometry but none of this poem's
coherence. The reported quantity is the poem's statistic minus the mean of its
controls. If refrain structure is doing anything beyond thinning the cloud,
that difference moves with refrain strength. If it does not, the sweep is flat
and Phase 0 has its answer.

Run from the project root:  uv run python src/5_compute_ph.py
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from tqdm import tqdm

sys.path.insert(0, str(Path(__file__).parent))
from topology import analyse, corpus_control                # noqa: E402

PROCESSED = Path("data/processed")
EMB = PROCESSED / "embeddings.npz"
GEOM = PROCESSED / "cloud_geometry.parquet"
OUT = PROCESSED / "ph_results.parquet"

N_CONTROLS = 20
STATS = ["h0_total_persistence", "h0_mean_life_nondup",
         "n_h1", "h1_total_persistence", "h1_max_persistence"]


def dedup(cloud: np.ndarray) -> np.ndarray:
    """Distinct points only: what Rips actually sees."""
    _, idx = np.unique(np.round(cloud, 9), axis=0, return_index=True)
    return cloud[np.sort(idx)]


def main():
    clouds = np.load(EMB)
    geom = pd.read_parquet(GEOM)

    # Control pool: every line of every real poem.
    real_ids = geom.loc[~geom.is_synthetic, "poem_id"]
    pool = np.vstack([clouds[i] for i in real_ids])
    print(f"Control pool: {len(pool)} real verse lines\n")

    rng = np.random.default_rng(0)
    rows = []
    for rec in tqdm(list(geom.itertuples()), desc="persistent homology"):
        cloud = dedup(clouds[rec.poem_id])
        observed = analyse(cloud)

        ctrl = pd.DataFrame([
            analyse(corpus_control(pool, len(cloud), rng))
            for _ in range(N_CONTROLS)
        ])

        row = {"poem_id": rec.poem_id, "form_family": rec.form_family,
               "n_repeats": rec.n_repeats, "is_synthetic": rec.is_synthetic,
               "n_distinct_points": len(cloud)}
        for s in STATS:
            row[s] = observed[s]
            row[f"{s}__ctrl_mean"] = ctrl[s].mean()
            row[f"{s}__ctrl_sd"] = ctrl[s].std()
            # Excess over a size-matched bag of arbitrary verse.
            row[f"{s}__excess"] = observed[s] - ctrl[s].mean()
        rows.append(row)

    res = pd.DataFrame(rows)
    res.to_parquet(OUT, index=False)

    pd.set_option("display.width", 200)
    print("\n=== SYNTHETIC SWEEP: does refrain strength move anything? ===")
    print("(excess = poem minus mean of 20 controls matched on distinct point count)\n")
    syn = res[res.is_synthetic].groupby("n_repeats").agg(
        n=("poem_id", "size"),
        distinct_pts=("n_distinct_points", "median"),
        h0_excess=("h0_total_persistence__excess", "mean"),
        h0_mean_life_excess=("h0_mean_life_nondup__excess", "mean"),
        n_h1=("n_h1", "mean"),
        n_h1_excess=("n_h1__excess", "mean"),
        h1_tot_excess=("h1_total_persistence__excess", "mean"),
    )
    print(syn.round(4).to_string())

    print("\n=== REAL FORMS ===\n")
    realf = res[~res.is_synthetic].groupby("form_family").agg(
        n=("poem_id", "size"),
        distinct_pts=("n_distinct_points", "median"),
        h0_excess=("h0_total_persistence__excess", "mean"),
        h0_mean_life_excess=("h0_mean_life_nondup__excess", "mean"),
        n_h1=("n_h1", "mean"),
        n_h1_excess=("n_h1__excess", "mean"),
        h1_tot_excess=("h1_total_persistence__excess", "mean"),
    )
    print(realf.round(4).to_string())

    print(f"\nWritten to {OUT}")


if __name__ == "__main__":
    main()
