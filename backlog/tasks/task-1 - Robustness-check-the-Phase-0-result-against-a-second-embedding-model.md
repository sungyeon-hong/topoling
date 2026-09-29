---
id: task-1
title: Robustness-check the Phase 0 result against a second embedding model
status: Done
priority: high
created: 2026-09-07
updated: 2026-09-18
labels: [phase-0, validation, blocking]
completed: 2026-09-18
depends_on: []
---

## What this is

Re-run the whole Phase 0 measurement with `all-mpnet-base-v2` in place of
`nomic-embed-text-v1.5`, and compare the two sets of results.

## Why it matters

Everything currently known about Phase 0 rests on a single embedding model.
`CLAUDE.md` states the rule plainly: `all-mpnet-base-v2` uses a different
training regime, and "if a topological finding flips between the two models, it
is a model artifact, not a property of the text. Run this before believing
anything."

Nothing from the 2026-09-07 session should be treated as established until this
is done. That includes the two findings the session leant on most:

- the monotone H0 dose-response to refrain displacement, and
- the absence of any H1 signal in any condition.

The second is the one to watch. Concluding that H1 carries nothing is a claim
that would reshape the project's framing (see task-2), and it would be a poor
reason to drop "homogenisation loops" if it turned out to be a quirk of how one
model spaces its embeddings.

## How to run it

The pipeline already supports this; no new code should be needed.
`src/embedding.py` exposes `ROBUSTNESS_MODEL`, and `embed_lines()` takes a
`model_name`. Note that `TASK_PREFIX` deliberately maps only the Nomic model:
mpnet must *not* be given a task prefix, and passing one would silently change
every distance.

Run from the project root, writing to separate output paths so the two sets
survive side by side:

    uv run python src/3_embed_text.py      # after pointing it at ROBUSTNESS_MODEL
    uv run python src/4_build_complexes.py
    uv run python src/5_compute_ph.py
    uv run python src/experiment_refrain_sensitivity.py

Step 3 currently hardcodes the primary model, so it needs a model argument
before this can run cleanly. That is part of this task.

## What counts as finished

- [x] Both models' results exist as separate files under `data/processed/`,
      and neither has overwritten the other.
- [x] The four real form arms are compared across models: does the
      Kruskal-Wallis separation (p = 6.8e-05 under Nomic) survive?
      **Yes** -- p = 6.1e-04 under mpnet. But individual pairwise contrasts
      flip, so only `refrain_song`/`irregular` and `ballad_stanza`/`irregular`
      are safe to lean on.
- [x] The refrain displacement sweep is compared across models: is the H0
      dose-response still monotone, and does it still saturate near a
      displacement of 0.20?
      **Yes to both**, curves correlate at rho = +0.943. The effect *size* is
      five times smaller under mpnet, so no sensitivity figure from one model
      may be quoted as the instrument's.
- [x] The H1 null is checked specifically. If mpnet shows H1 structure where
      Nomic showed none, the H1 question is reopened and task-2 is blocked.
      **The null holds; task-2 is not blocked.** The two nominally significant
      H1 arm results flip in opposite directions between the models, and the
      third is point count (rho = +0.92 with distinct-point count). One robust
      H1 finding did emerge and task-2 should weigh it: real poems have far
      *fewer* loops than size-matched arbitrary verse under both models.
- [x] Result written up in `backlog/docs/`, and `CLAUDE.md` updated if any
      finding flips.
      See `backlog/docs/task-1-embedding-model-robustness.md`.

## What was found along the way

Two defects in the experiment code, both fixed on 2026-09-18 and both recorded
in the findings document:

- `experiment_refrain_sensitivity.py` seeded its displacement noise from
  Python's `hash()`, which is randomised per process, so the sweep was not
  reproducible between runs. This would have confounded the whole comparison.
- `synthetic.py` did not pair the refrain-strength sweep the way its docstring
  claimed. Correcting it removes the weak H0 trend reported as Result 1 of
  `phase0-first-results.md` (rho +0.22, p = 0.038 becomes rho +0.040,
  p = 0.66).

## Watch out for

Absolute distances are not comparable between models. Nomic puts unrelated
verse lines around cosine 0.6, so all pairwise distances landed in [0, 1.03] of
a possible [0, 2]. mpnet spreads differently. Compare *shapes* — monotonicity,
ordering of the arms, significance — not raw values.
