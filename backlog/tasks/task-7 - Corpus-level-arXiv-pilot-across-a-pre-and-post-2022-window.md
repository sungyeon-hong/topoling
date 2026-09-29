---
id: task-7
title: Corpus-level arXiv pilot across a pre- and post-2022 window
status: To Do
priority: medium
created: 2026-09-30
updated: 2026-09-30
labels: [phase-1, corpus]
depends_on: [task-6]
---

## What this is

The first Phase 1 measurement: collect arXiv abstracts across a window
spanning the arrival of ChatGPT, and measure between-document diversity at
corpus level in each year.

## Why it matters

This is the first time the project measures the thing it is actually about.
Everything before it is instrument validation.

It is also the deciding input for whether the conference submission is
poetry-only or attempts the link to generative AI. A weak or ambiguous result
here is a reason to leave it out of the abstract rather than to report it
thinly -- an abstract has no room to defend a contested measurement.

## Design, as already specified in CLAUDE.md

The scientific baseline is **difference-based**, not a comparison against
randomness. Establish the natural drift rate in a pre-2022 window, then test
whether the post-2022 trend departs from it. Optionally strengthen this with a
control discipline having low AI-writing adoption over the same period, giving
a difference-in-differences shape.

Nuisance calibration is separate and still needed: random-points-on-sphere
controls, to know whether an observed feature exceeds what point count and
ambient dimension alone produce. Note that the shuffled-sentence control listed
in `CLAUDE.md` is a no-op for plain Rips and should not be attempted -- a Rips
complex is built from a set of points and is permutation-invariant.

## Practical notes

- Use `scratch/collect_arxiv_pilot.py` rather than `src/1_collect_arxiv.py`.
  The scratch version is the better collector: version stripping, dedup, a
  21-column schema and a run summary. `src/1_collect_arxiv.py` is hardcoded to
  math.AT.
- **Do not lower the collector's delay_seconds or parallelise the harvest.**
  The 3-5 second delays are arXiv API courtesy.
- Corpus-level is the right unit here regardless of anything else: an abstract
  is 6-10 sentences, and document-level H1 on 8 points is sampling noise. No
  document-level H1 claim may be made for arXiv abstracts.

## What counts as finished

- [ ] A collected, cleaned, deduplicated arXiv sample spanning pre- and
      post-2022, with enough documents per year to subsample to fixed *n*.
- [ ] Corpus-level persistence statistics per year with bootstrap error bars.
- [ ] Run under both embedding models, per the task-1 rule.
- [ ] A written judgement in `backlog/docs/` on whether the result is solid
      enough to appear in the conference abstract.
