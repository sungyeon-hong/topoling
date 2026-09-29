"""task-1 - does Phase 0 survive a change of embedding model?

Everything known about Phase 0 came from one model, `nomic-embed-text-v1.5`.
`CLAUDE.md` sets the rule: if a topological finding flips under
`all-mpnet-base-v2`, it is an artifact of how one model spaces its embeddings
rather than a property of the text.

Absolute values are *not* comparable between the two. The models place
unrelated verse lines at different distances, so every filtration value shifts.
What must be compared is shape: the ordering of the form arms, the sign and
monotonicity of the displacement response, the presence or absence of an H1
signal, and whether the same individual poems come out extreme under both.

Reads the model-tagged outputs of steps 4-5 and the displacement sweep, and
runs the four checks task-1 asks for. Run from the project root, after both
models have been through the pipeline:

    uv run python src/compare_models.py
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

sys.path.insert(0, str(Path(__file__).parent))
from embedding import MODEL_KEYS, tagged                    # noqa: E402

PROCESSED = Path("data/processed")
PH = PROCESSED / "ph_results.parquet"
SENS = PROCESSED / "refrain_sensitivity.parquet"

KEYS = ["nomic", "mpnet"]
ARMS = ["sonnet", "refrain_song", "ballad_stanza", "irregular"]

# The H0 statistic Phase 0 reported its form separation on.
H0 = "h0_mean_life_nondup__excess"
H1_STATS = ["n_h1__excess", "h1_total_persistence__excess",
            "h1_max_persistence__excess"]


def rule(title: str) -> None:
    print(f"\n{'=' * 78}\n{title}\n{'=' * 78}")


def load(path: Path) -> dict[str, pd.DataFrame]:
    out = {}
    for key in KEYS:
        p = tagged(path, key)
        if not p.exists():
            raise SystemExit(f"missing {p} -- run the pipeline for --model {key}")
        out[key] = pd.read_parquet(p)
    return out


# --------------------------------------------------------------- check 2
def compare_form_arms(ph: dict[str, pd.DataFrame]) -> None:
    rule("CHECK 2 - do the four real form arms still separate?")
    print("Statistic: H0 mean bar life, excess over 20 size-matched corpus "
          "controls.\nUnder nomic on 2026-09-07: Kruskal-Wallis p = 6.8e-05.\n")

    medians = {}
    for key in KEYS:
        real = ph[key][~ph[key].is_synthetic]
        groups = [real.loc[real.form_family == a, H0].to_numpy() for a in ARMS]
        h, p = stats.kruskal(*groups)
        medians[key] = {a: float(np.median(g)) for a, g in zip(ARMS, groups)}
        verdict = "separates" if p < 0.05 else "DOES NOT separate"
        print(f"  [{key:5}] Kruskal-Wallis H = {h:6.2f}  p = {p:.3g}   -> {verdict}")

    print("\n  Arm medians (more negative = lines sit closer together than "
          "arbitrary verse):")
    tbl = pd.DataFrame(medians).loc[ARMS]
    tbl["rank_nomic"] = tbl.nomic.rank()
    tbl["rank_mpnet"] = tbl.mpnet.rank()
    print(tbl.round(4).to_string())

    rho, p = stats.spearmanr(tbl.nomic, tbl.mpnet)
    print(f"\n  Spearman of the arm ordering across models: rho = {rho:+.3f} "
          f"(p = {p:.3g}, n = {len(ARMS)})")
    print("  Every arm negative under both models? "
          f"{bool((tbl[KEYS] < 0).all().all())}")

    print("\n  Pairwise Mann-Whitney within each model (uncorrected):")
    for i, a in enumerate(ARMS):
        for b in ARMS[i + 1:]:
            cells = []
            for key in KEYS:
                real = ph[key][~ph[key].is_synthetic]
                pa = real.loc[real.form_family == a, H0]
                pb = real.loc[real.form_family == b, H0]
                pv = stats.mannwhitneyu(pa, pb).pvalue
                cells.append(f"{key}: p={pv:.4f} {'*' if pv < 0.05 else 'ns'}")
            print(f"    {a:14} vs {b:14}  " + "   ".join(cells))


# --------------------------------------------------------------- check 3
def compare_displacement(sens: dict[str, pd.DataFrame]) -> None:
    rule("CHECK 3 - is the H0 displacement response still monotone?")
    print("A paraphrase modelled as a nudge of size eps. Cardinality is fixed "
          "at 19\ndistinct points throughout, so nothing here is point count "
          "in disguise.\n")

    for key in KEYS:
        df = sens[key]
        by_eps = df.groupby("eps").h0_mean_life_excess.mean()
        nonzero = by_eps[by_eps.index > 0]
        mono = bool(np.all(np.diff(nonzero.to_numpy()) > 0))
        print(f"  [{key}] mean H0 excess by eps:")
        print("    " + "  ".join(f"{e:g}:{v:+.4f}" for e, v in by_eps.items()))
        print(f"    monotone increasing over eps > 0? {mono}")

        # Saturation: where does the curve stop climbing appreciably?
        span = nonzero.iloc[-1] - nonzero.iloc[0]
        reached = nonzero[(nonzero - nonzero.iloc[0]) >= 0.9 * span]
        print(f"    reaches 90% of its climb by eps = {reached.index[0]:g}")

        base = df[df.eps == 0].set_index("donor").h0_mean_life_excess
        sig = []
        for eps in sorted(df.eps.unique())[1:]:
            cur = df[df.eps == eps].set_index("donor").h0_mean_life_excess
            common = base.index.intersection(cur.index)
            pv = stats.wilcoxon(base.loc[common], cur.loc[common]).pvalue
            sig.append(f"{eps:g}:p={pv:.2g}{'*' if pv < 0.05 else 'ns'}")
        print(f"    paired vs verbatim (eps=0): " + "  ".join(sig) + "\n")

    # Same donors, same displacements -- so the curves can be correlated.
    a = sens["nomic"].groupby("eps").h0_mean_life_excess.mean()
    b = sens["mpnet"].groupby("eps").h0_mean_life_excess.mean()
    rho, p = stats.spearmanr(a, b)
    print(f"  Spearman between the two curves: rho = {rho:+.3f} (p = {p:.3g})")


# --------------------------------------------------------------- check 4
def compare_h1(ph: dict[str, pd.DataFrame], sens: dict[str, pd.DataFrame]) -> None:
    rule("CHECK 4 - the H1 null. Does mpnet find loops where nomic found none?")
    print("This is the one to watch: concluding H1 carries nothing would "
          "reshape the\nproject's framing (task-2), and it is a poor reason to "
          "do so if it is one\nmodel's quirk.\n")

    print("  (a) Across the four real form arms -- Kruskal-Wallis on each H1 "
          "statistic:")
    for key in KEYS:
        real = ph[key][~ph[key].is_synthetic]
        cells = []
        for stat in H1_STATS:
            groups = [real.loc[real.form_family == a, stat] for a in ARMS]
            p = stats.kruskal(*groups).pvalue
            cells.append(f"{stat.replace('__excess', ''):22} p={p:.3g}"
                         f"{' *' if p < 0.05 else ' ns'}")
        print(f"    [{key:5}] " + "\n            ".join(cells))

    print("\n  (b) Across refrain strength in the synthetic sweep -- Spearman "
          "vs n_repeats:")
    for key in KEYS:
        syn = ph[key][ph[key].is_synthetic]
        cells = []
        for stat in H1_STATS:
            rho, p = stats.spearmanr(syn.n_repeats, syn[stat])
            cells.append(f"{stat.replace('__excess', ''):22} rho={rho:+.3f} "
                         f"p={p:.3g}{' *' if p < 0.05 else ' ns'}")
        print(f"    [{key:5}] " + "\n            ".join(cells))

    print("\n  (c) Across displacement at fixed cardinality -- Spearman vs eps:")
    for key in KEYS:
        df = sens[key]
        cells = []
        for stat in ["n_h1_excess", "h1_max_excess"]:
            rho, p = stats.spearmanr(df.eps, df[stat])
            cells.append(f"{stat:16} rho={rho:+.3f} p={p:.3g}"
                         f"{' *' if p < 0.05 else ' ns'}")
        print(f"    [{key:5}] " + "   ".join(cells))

    print("\n  (d) Is there any H1 excess at all? Mean n_h1 excess over "
          "size-matched controls:")
    for key in KEYS:
        real = ph[key][~ph[key].is_synthetic]
        m = real["n_h1__excess"].mean()
        t, p = stats.wilcoxon(real["n_h1__excess"])
        print(f"    [{key:5}] mean = {m:+.3f}  (Wilcoxon vs 0: p = {p:.3g})"
              "   negative = fewer loops than arbitrary verse")


# ------------------------------------------------- cross-model agreement
def compare_per_poem(ph: dict[str, pd.DataFrame]) -> None:
    rule("EXTRA - do the same individual poems come out extreme under both?")
    print("The arm-level checks above could agree while every poem inside them "
          "disagreed.\nThis correlates the per-poem statistic across models, "
          "which is the strictest\nform of the question.\n")

    a = ph["nomic"].set_index("poem_id")
    b = ph["mpnet"].set_index("poem_id")
    common = a.index.intersection(b.index)
    print(f"  {len(common)} poems measured under both models\n")

    for label, mask in [("real poems", ~a.loc[common].is_synthetic),
                        ("synthetic", a.loc[common].is_synthetic)]:
        idx = common[mask.to_numpy()]
        for stat in [H0, "n_h1__excess"]:
            rho, p = stats.spearmanr(a.loc[idx, stat], b.loc[idx, stat])
            print(f"  {label:11} {stat:32} rho = {rho:+.3f}  p = {p:.3g}")


def main():
    ph, sens = load(PH), load(SENS)

    rule("CHECK 1 - both models' results exist side by side")
    for path in (PH, SENS):
        for key in KEYS:
            p = tagged(path, key)
            print(f"  {p}  ({p.stat().st_size / 1e3:.0f} kB, "
                  f"{len(pd.read_parquet(p))} rows)")
    print(f"\n  Models: " + ", ".join(f"{k} = {MODEL_KEYS[k]}" for k in KEYS))

    compare_form_arms(ph)
    compare_displacement(sens)
    compare_h1(ph, sens)
    compare_per_poem(ph)
    print()


if __name__ == "__main__":
    main()
