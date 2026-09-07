"""Vietoris-Rips persistent homology over poem line clouds, and its controls.

Points are L2-normalised (see embedding.py), so they lie on the unit sphere,
Euclidean distance is monotone in cosine similarity, and every filtration value
is bounded in [0, 2]. Diagrams are therefore directly comparable across poems
without rescaling.

**Verbatim refrains are invisible in the diagram, and this matters.** Two lines
repeated word for word embed to the same point, and ripser silently discards
zero-persistence bars: 13 points containing 3 exact copies yield a 10-bar H0
diagram, not 13. So a repeated refrain contributes *nothing* to the topology
except to reduce the number of distinct points. A 19-line villanelle whose two
refrains recur four times each is, to Rips, a cloud of 13 points.

The consequence is that a synthetic villanelle differs from its 19-distinct-line
control mainly in **cardinality**, which CLAUDE.md already identifies as a
confound: persistence statistics depend on point count for entirely trivial
reasons. `n_exact_duplicates` is therefore computed from the cloud rather than
read off the diagram, and `n_distinct_points` is reported alongside it so the
confound stays visible. Any claim that PH "detects refrains" must survive
matching on distinct point count, not raw line count.

**Controls.** Two, answering different questions.

`corpus_control` replaces a poem's lines with the same number of lines drawn at
random from other poems. This is the right nuisance calibration, because it
holds the embedding manifold fixed -- these are real lines of real verse, with
whatever geometry the model imposes -- and destroys only the within-poem
coherence. It answers "is this poem's structure different from an arbitrary
bag of verse the same size?"

`sphere_control` draws points uniformly on the unit sphere in the same ambient
dimension. It answers the weaker question "is this different from noise?", and
it is deliberately a poor match: unrelated Nomic embeddings sit around cosine
0.6 rather than 0, so real text occupies a narrow cone, not the whole sphere.
Reported for completeness, but the corpus control is the one that bites.
"""

import numpy as np
from ripser import ripser


def compute_diagrams(cloud: np.ndarray, maxdim: int = 1):
    """H0 and H1 persistence diagrams for a point cloud."""
    return ripser(cloud, maxdim=maxdim)["dgms"]


def _finite(bars: np.ndarray) -> np.ndarray:
    """Drop the essential (infinite-death) bar; H0 always has exactly one."""
    if bars.size == 0:
        return bars.reshape(0, 2)
    return bars[np.isfinite(bars[:, 1])]


def count_duplicates(cloud: np.ndarray, tol: float = 1e-9) -> int:
    """How many points coincide with an earlier point.

    Read from the cloud, not the diagram: ripser drops the zero-persistence
    bars that duplicates would otherwise produce.
    """
    rounded = np.round(cloud / tol).astype(np.int64)
    _, counts = np.unique(rounded, axis=0, return_counts=True)
    return int(len(cloud) - len(counts))


def summarise(dgms, cloud: np.ndarray) -> dict:
    """Scalar summary of one poem's diagrams."""
    h0, h1 = _finite(dgms[0]), _finite(dgms[1])
    h0_life = h0[:, 1] - h0[:, 0] if h0.size else np.array([])
    h1_life = h1[:, 1] - h1[:, 0] if h1.size else np.array([])
    n_dup = count_duplicates(cloud)

    return {
        "n_points": len(cloud),
        "n_distinct_points": len(cloud) - n_dup,
        "n_exact_duplicates": n_dup,
        "h0_total_persistence": float(h0_life.sum()) if h0_life.size else 0.0,
        "h0_max_death": float(h0[:, 1].max()) if h0.size else 0.0,
        # Mean over non-duplicate bars: how spread the distinct lines are.
        "h0_mean_life_nondup": (float(h0_life[h0_life > 1e-9].mean())
                                if (h0_life > 1e-9).any() else 0.0),
        "n_h1": int(h1.shape[0]),
        "h1_total_persistence": float(h1_life.sum()) if h1_life.size else 0.0,
        "h1_max_persistence": float(h1_life.max()) if h1_life.size else 0.0,
    }


def analyse(cloud: np.ndarray) -> dict:
    """Diagrams and summary for one cloud."""
    return summarise(compute_diagrams(cloud), cloud)


def corpus_control(pool: np.ndarray, n_points: int, rng) -> np.ndarray:
    """`n_points` real verse lines drawn at random from elsewhere in the corpus."""
    idx = rng.choice(len(pool), size=n_points, replace=False)
    return pool[idx]


def sphere_control(n_points: int, dim: int, rng) -> np.ndarray:
    """`n_points` drawn uniformly on the unit sphere in `dim` dimensions."""
    x = rng.standard_normal((n_points, dim))
    return x / np.linalg.norm(x, axis=1, keepdims=True)
