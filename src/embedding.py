"""Embed poem lines and place them on the unit sphere.

Two decisions from CLAUDE.md are enforced here rather than left to callers.

**Model.** nomic-embed-text-v1.5 is the primary: general-domain, so poems and
abstracts are handled on equal footing, and the same model panic-tda uses, so
results stay comparable across the two projects. all-mpnet-base-v2 is the
robustness check -- a different training regime. If a topological finding flips
between the two, it is a model artifact rather than a property of the text.

**L2 normalisation.** Every embedding is scaled to unit length, so points lie
on the unit sphere and Euclidean distance becomes a monotone function of cosine
similarity (||x-y||^2 = 2 - 2cos). Ripser's Euclidean metric then *is* cosine
geometry, and the filtration is bounded in [0, 2], so diagrams are comparable
across poems and corpora with no further rescaling.

Nomic is prefix-conditioned: the same text embeds differently under
"clustering: " than under "search_query: ". Phase 0 measures the geometry among
lines of one poem, which is a clustering task, so that prefix is used and is
recorded alongside the vectors. Getting this wrong silently distorts every
distance downstream.
"""

from pathlib import Path

import numpy as np

PRIMARY_MODEL = "nomic-ai/nomic-embed-text-v1.5"
ROBUSTNESS_MODEL = "sentence-transformers/all-mpnet-base-v2"

# Only Nomic takes a task prefix; mpnet must not be given one.
TASK_PREFIX = {PRIMARY_MODEL: "clustering: "}

# Short keys for the command line and for tagging output files. Every stage of
# the pipeline writes to a model-tagged path, so the primary run and the
# robustness run survive side by side and neither can silently overwrite the
# other (task-1).
MODEL_KEYS = {"nomic": PRIMARY_MODEL, "mpnet": ROBUSTNESS_MODEL}


def resolve_model(key: str) -> str:
    """Full model name for a short key such as "nomic" or "mpnet"."""
    if key not in MODEL_KEYS:
        raise ValueError(f"unknown model key {key!r}; expected one of "
                         f"{sorted(MODEL_KEYS)}")
    return MODEL_KEYS[key]


def tagged(path: Path, key: str) -> Path:
    """Insert a model key before the suffix: foo.parquet -> foo_nomic.parquet."""
    return path.with_name(f"{path.stem}_{key}{path.suffix}")


def add_model_arg(parser) -> None:
    """Give a script the standard --model flag."""
    parser.add_argument("--model", choices=sorted(MODEL_KEYS), default="nomic",
                        help="embedding model to run (default: nomic)")


_MODEL_CACHE = {}


def load_model(name: str = PRIMARY_MODEL):
    """Load a sentence-transformers model, memoised for the process."""
    from sentence_transformers import SentenceTransformer

    if name not in _MODEL_CACHE:
        # Nomic ships custom modelling code, hence trust_remote_code.
        _MODEL_CACHE[name] = SentenceTransformer(name, trust_remote_code=True)
    return _MODEL_CACHE[name]


def l2_normalise(vectors: np.ndarray) -> np.ndarray:
    """Scale each row to unit length; leave any zero row untouched."""
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    return vectors / np.where(norms == 0, 1.0, norms)


def embed_lines(
    lines: list[str],
    model_name: str = PRIMARY_MODEL,
    batch_size: int = 64,
    truncate_dim: int | None = None,
) -> np.ndarray:
    """Embed lines and return unit-length row vectors.

    `truncate_dim` uses Nomic's Matryoshka training: 768 truncates cleanly to
    256 or 128, which cuts Rips runtime. Truncation happens before
    normalisation, because a truncated vector is no longer unit length.
    """
    model = load_model(model_name)
    prefix = TASK_PREFIX.get(model_name, "")
    vectors = model.encode(
        [prefix + line for line in lines],
        batch_size=batch_size,
        show_progress_bar=False,
        convert_to_numpy=True,
        normalize_embeddings=False,
    )
    if truncate_dim is not None:
        vectors = vectors[:, :truncate_dim]
    return l2_normalise(np.asarray(vectors, dtype=np.float64))
