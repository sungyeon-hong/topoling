"""Step 3 - embed poem lines onto the unit sphere.

Embeds the Phase 0 sample together with the synthetic villanelle sweep, so
both pass through an identical pipeline. Wrap fragments are dropped first:
PoetryDB breaks long lines, and an indented remnant like "  the" is not a line
of verse and must not become a point (see poetry_forms.py).

Outputs are tagged with the model key, so the primary run and the robustness
run (task-1) survive side by side.

Run from the project root:
    uv run python src/3_embed_text.py --model nomic
    uv run python src/3_embed_text.py --model mpnet
"""

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from tqdm import tqdm

sys.path.insert(0, str(Path(__file__).parent))
from embedding import add_model_arg, embed_lines, resolve_model, tagged  # noqa: E402
from poetry_forms import is_wrap_fragment                  # noqa: E402
from synthetic import build_sweep                          # noqa: E402

PROCESSED = Path("data/processed")
SAMPLE = PROCESSED / "poetry_phase0_sample.parquet"
LABELLED = PROCESSED / "poetrydb_labelled.parquet"
OUT = PROCESSED / "embeddings.npz"
MANIFEST = PROCESSED / "embedding_manifest.parquet"

# The donor draw, the synthetic sweep and the sample are all seeded, so the two
# models see byte-identical text. Only the embedding differs.
SEED = 0

# Donors for the synthetic sweep: poems with no refrains of their own, long
# enough to supply 19 distinct lines, so any repetition is the one we planted.
N_DONORS = 30
MIN_DONOR_LINES = 25


def verse_lines(lines) -> list[str]:
    """Real lines of verse: non-blank, and not a wrap continuation."""
    return [l.strip() for l in lines if l.strip() and not is_wrap_fragment(l)]


def main(model_key: str):
    model_name = resolve_model(model_key)
    out, manifest_path = tagged(OUT, model_key), tagged(MANIFEST, model_key)

    sample = pd.read_parquet(SAMPLE)
    labelled = pd.read_parquet(LABELLED)

    donors_df = labelled[
        (labelled.n_refrains == 0)
        & (labelled.linecount >= MIN_DONOR_LINES)
        & (labelled.wrap_fraction == 0)
    ].sample(n=N_DONORS, random_state=SEED)
    donors = []
    for lines in donors_df.lines:
        uniq = list(dict.fromkeys(verse_lines(lines)))
        if len(uniq) >= 19:
            donors.append(uniq)
    print(f"{len(donors)} donor poems for the synthetic sweep")

    records, clouds = [], {}
    real = [{"poem_id": r.poem_id, "title": r.title, "author": r.author,
             "form": r.form, "form_family": r.form_family, "n_repeats": 0,
             "lines": list(r.lines)} for r in sample.itertuples()]
    synthetic = build_sweep(donors, seed=SEED)
    print(f"{len(real)} real poems + {len(synthetic)} synthetic poems")

    for rec in tqdm(real + synthetic, desc="embedding"):
        lines = verse_lines(rec["lines"])
        if len(lines) < 4:            # too small for any complex worth building
            continue
        clouds[rec["poem_id"]] = embed_lines(lines, model_name=model_name)
        records.append({k: v for k, v in rec.items() if k != "lines"}
                       | {"n_lines_embedded": len(lines),
                          "is_synthetic": rec["author"] == "SYNTHETIC",
                          "model_key": model_key, "model_name": model_name})

    np.savez_compressed(out, **clouds)
    manifest = pd.DataFrame(records)
    manifest.to_parquet(manifest_path, index=False)

    print(f"\nEmbedded {len(clouds)} poems with {model_name}")
    print(f"  {out}  ({out.stat().st_size / 1e6:.0f} MB)")
    print(f"  {manifest_path}")
    print(manifest.groupby("form_family").n_lines_embedded.agg(
        ["size", "median"]).to_string())


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    add_model_arg(ap)
    main(ap.parse_args().model)
