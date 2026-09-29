"""Step 4 - assemble the point clouds and record their geometry.

The complexes themselves are built inside ripser at step 5; what this step
does is decide *which* clouds are admissible and measure the scale each one
occupies, so that step 5's diagrams can be read against something.

Because every point is L2-normalised, all pairwise distances fall in [0, 2]
and are monotone in cosine similarity. The geometry columns below therefore
mean the same thing across every poem, with no rescaling.

Run from the project root:
    uv run python src/4_build_complexes.py --model nomic
"""

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.spatial.distance import pdist

sys.path.insert(0, str(Path(__file__).parent))
from embedding import add_model_arg, tagged                 # noqa: E402
from poetry_forms import H1_POINT_FLOOR                    # noqa: E402
from topology import count_duplicates                      # noqa: E402

PROCESSED = Path("data/processed")
EMB = PROCESSED / "embeddings.npz"
MANIFEST = PROCESSED / "embedding_manifest.parquet"
OUT = PROCESSED / "cloud_geometry.parquet"


def main(model_key: str):
    emb, manifest_path = tagged(EMB, model_key), tagged(MANIFEST, model_key)
    out = tagged(OUT, model_key)

    clouds = np.load(emb)
    manifest = pd.read_parquet(manifest_path)

    rows = []
    for rec in manifest.itertuples():
        cloud = clouds[rec.poem_id]
        d = pdist(cloud)
        n_dup = count_duplicates(cloud)
        rows.append({
            "poem_id": rec.poem_id,
            "n_points": len(cloud),
            "n_distinct_points": len(cloud) - n_dup,
            "n_exact_duplicates": n_dup,
            # Distinct points, not raw lines, is what Rips actually sees.
            "meets_h1_floor": (len(cloud) - n_dup) >= H1_POINT_FLOOR,
            "d_min": float(d.min()),
            "d_median": float(np.median(d)),
            "d_max": float(d.max()),
        })

    geom = manifest.merge(pd.DataFrame(rows), on="poem_id")
    geom.to_parquet(out, index=False)

    print(f"[{model_key}] assembled {len(geom)} clouds; every distance in "
          f"[{geom.d_min.min():.3f}, {geom.d_max.max():.3f}] of the possible [0, 2]\n")
    print(geom.groupby("form_family").agg(
        n=("poem_id", "size"),
        med_points=("n_points", "median"),
        med_distinct=("n_distinct_points", "median"),
        med_dups=("n_exact_duplicates", "median"),
        med_d=("d_median", "median"),
        clears_h1=("meets_h1_floor", "sum"),
    ).to_string())
    print(f"\nH1 floor applied to *distinct* points (>= {H1_POINT_FLOOR}): "
          "repeated lines collapse to one point, so raw line count overstates "
          "what Rips sees.")
    print(f"\nWritten to {out}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    add_model_arg(ap)
    main(ap.parse_args().model)
