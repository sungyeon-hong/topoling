"""Does persistent homology see *near*-duplicate lines, if not exact ones?

The synthetic sweep in synthetic.py repeats refrains verbatim, which turns out
to be the worst possible ground truth for this instrument: identical text gives
an identical embedding, the points coincide, ripser drops the zero-persistence
bars, and the refrain contributes nothing but a smaller cloud.

That is a fact about exact repetition, and Phase 1's target is not exact. A
corpus converging on the semantic mean produces lines that are *similar*, not
identical, and near-duplicate points do not collapse: they form a tight cluster
with real, short-lived persistence. So the question that matters is not "can PH
see a villanelle" but "how close do two lines have to be before PH stops
resolving them, and how close before it stops seeing them as related at all".

This sweeps that. A paraphrase is modelled as a small displacement of the
refrain in embedding space, renormalised back to the sphere. That is a
geometric model of paraphrase, not a linguistic one -- it measures the
instrument's resolving power, which is what Phase 1 needs, and makes no claim
about what a real paraphrase does.

Run from the project root:
    uv run python src/experiment_refrain_sensitivity.py --model nomic
"""

import argparse
import hashlib
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from tqdm import tqdm

sys.path.insert(0, str(Path(__file__).parent))
from embedding import add_model_arg, l2_normalise, tagged   # noqa: E402
from synthetic import A1_POSITIONS, A2_POSITIONS, VILLANELLE_LENGTH  # noqa: E402
from topology import analyse, corpus_control                # noqa: E402

PROCESSED = Path("data/processed")
EMB = PROCESSED / "embeddings.npz"
GEOM = PROCESSED / "cloud_geometry.parquet"
OUT = PROCESSED / "refrain_sensitivity.parquet"

SEED = 0

# 0.0 is verbatim repetition; the median distance between unrelated verse
# lines is ~0.80, so 0.4 is already half-way to "unrelated".
EPSILONS = [0.0, 0.02, 0.05, 0.10, 0.20, 0.40]
N_CONTROLS = 20


def donor_seed(donor: str) -> int:
    """A stable seed for one donor, identical in every process and every run.

    Python's built-in `hash()` is randomised per process for str, so seeding
    from it gave a different displacement on every run and made the sweep
    irreproducible. That does not matter much within one run, but it is fatal
    to task-1: the primary and robustness runs would draw different
    displacements, and a difference between the two models could not be told
    apart from a difference between two random draws. blake2b is stable.
    """
    digest = hashlib.blake2b(donor.encode(), digest_size=8).digest()
    return int.from_bytes(digest, "big") % (1 << 30)


def build_cloud(donor_cloud: np.ndarray, eps: float, rng) -> np.ndarray:
    """A 19-point villanelle whose refrains recur with displacement `eps`."""
    a1, a2, *filler = donor_cloud[:2 + VILLANELLE_LENGTH - 8]
    cloud = np.zeros((VILLANELLE_LENGTH, donor_cloud.shape[1]))
    fill = iter(filler)
    for i in range(VILLANELLE_LENGTH):
        if i in A1_POSITIONS:
            base = a1
        elif i in A2_POSITIONS:
            base = a2
        else:
            cloud[i] = next(fill)
            continue
        # Displace, then return to the sphere so the metric stays comparable.
        cloud[i] = base + eps * rng.standard_normal(len(base))
    return l2_normalise(cloud)


def main(model_key: str):
    out = tagged(OUT, model_key)
    clouds = np.load(tagged(EMB, model_key))
    geom = pd.read_parquet(tagged(GEOM, model_key))

    donors = geom[(~geom.is_synthetic) & (geom.n_distinct_points >= 19)].poem_id
    pool = np.vstack([clouds[i] for i in geom.loc[~geom.is_synthetic, "poem_id"]])
    print(f"{len(donors)} donor poems, control pool {len(pool)} lines\n")

    rng = np.random.default_rng(SEED)
    rows = []
    for donor in tqdm(list(donors), desc="sensitivity sweep"):
        dc = clouds[donor]
        for eps in EPSILONS:
            cloud = build_cloud(dc, eps, np.random.default_rng(donor_seed(donor)))
            uniq = np.unique(np.round(cloud, 9), axis=0)
            obs = analyse(uniq)
            ctrl = pd.DataFrame([analyse(corpus_control(pool, len(uniq), rng))
                                 for _ in range(N_CONTROLS)])
            rows.append({
                "donor": donor, "model_key": model_key,
                "eps": eps, "n_distinct": len(uniq),
                "h0_mean_life": obs["h0_mean_life_nondup"],
                "h0_mean_life_excess": obs["h0_mean_life_nondup"] - ctrl["h0_mean_life_nondup"].mean(),
                "n_h1": obs["n_h1"],
                "n_h1_excess": obs["n_h1"] - ctrl["n_h1"].mean(),
                "h1_max": obs["h1_max_persistence"],
                "h1_max_excess": obs["h1_max_persistence"] - ctrl["h1_max_persistence"].mean(),
            })

    df = pd.DataFrame(rows)
    df.to_parquet(out, index=False)

    pd.set_option("display.width", 200)
    print(f"\n=== [{model_key}] refrain displacement sweep (eps = 0 is verbatim) ===\n")
    print(df.groupby("eps").agg(
        n=("donor", "size"),
        distinct_pts=("n_distinct", "median"),
        h0_mean_life=("h0_mean_life", "mean"),
        h0_excess=("h0_mean_life_excess", "mean"),
        n_h1=("n_h1", "mean"),
        n_h1_excess=("n_h1_excess", "mean"),
        h1_max_excess=("h1_max_excess", "mean"),
    ).round(4).to_string())

    print("\n=== paired against verbatim (eps=0), same donor ===")
    base = df[df.eps == 0].set_index("donor")
    for eps in EPSILONS[1:]:
        cur = df[df.eps == eps].set_index("donor")
        common = base.index.intersection(cur.index)
        for stat in ["h0_mean_life_excess", "n_h1_excess"]:
            a, b = base.loc[common, stat], cur.loc[common, stat]
            p = stats.wilcoxon(a, b).pvalue
            flag = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "ns"
            print(f"  eps={eps:<5} {stat:22} diff {(b-a).mean():+.4f}  p={p:.4f} {flag}")

    print(f"\nWritten to {out}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    add_model_arg(ap)
    main(ap.parse_args().model)
