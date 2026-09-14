---
id: task-1
title: Robustness-check the Phase 0 result against a second embedding model
status: To Do
priority: high
created: 2026-09-07
updated: 2026-09-14
labels: [phase-0, validation, blocking]
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

- [ ] Both models' results exist as separate files under `data/processed/`,
      and neither has overwritten the other.
- [ ] The four real form arms are compared across models: does the
      Kruskal-Wallis separation (p = 6.8e-05 under Nomic) survive?
- [ ] The refrain displacement sweep is compared across models: is the H0
      dose-response still monotone, and does it still saturate near a
      displacement of 0.20?
- [ ] The H1 null is checked specifically. If mpnet shows H1 structure where
      Nomic showed none, the H1 question is reopened and task-2 is blocked.
- [ ] Result written up in `backlog/docs/`, and `CLAUDE.md` updated if any
      finding flips.

## Watch out for

Absolute distances are not comparable between models. Nomic puts unrelated
verse lines around cosine 0.6, so all pairwise distances landed in [0, 1.03] of
a possible [0, 2]. mpnet spreads differently. Compare *shapes* — monotonicity,
ordering of the arms, significance — not raw values.
