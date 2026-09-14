---
id: task-4
title: Replace the geometric paraphrase model with real paraphrases
status: To Do
priority: medium
created: 2026-09-14
updated: 2026-09-14
labels: [phase-0, validation]
depends_on: [task-1]
---

## What this is

`src/experiment_refrain_sensitivity.py` models a paraphrase as a small random
displacement of the refrain's embedding, renormalised back onto the unit
sphere. Replace that with actual reworded lines and check the curve survives.

## Why it matters

The displacement sweep produced the session's most useful result: a monotone
H0 dose-response at fixed cardinality, mean excess bar life running -0.052,
+0.102, +0.176, +0.219, +0.239 across displacements of 0.02 to 0.40, saturating
near 0.20. That is a calibration curve, and Phase 1 would use it to say how
strong a homogenisation signal has to be before this instrument sees it.

But a random displacement is a *geometric* model of paraphrase, not a
linguistic one. Real paraphrases do not scatter isotropically around the
original: they move along directions the embedding model treats as meaningful,
and they may move much further in some directions than others. If real
paraphrases sit at displacements the sweep never probed, or cluster
anisotropically, the calibration is wrong in a way that matters for Phase 1.

## How to approach it

Take refrain lines from the corpus, generate several genuine rewordings of
each, embed them, and measure where they actually fall relative to the original
— the empirical displacement distribution. Then check whether the H0 response at
those real displacements matches what the synthetic sweep predicted for the same
magnitude.

The interesting failure mode is that real paraphrases turn out to sit beyond the
saturation point, in which case the instrument cannot distinguish a paraphrase
from an unrelated line and the Phase 1 target is out of reach.

## What counts as finished

- [ ] Empirical displacement distribution for real paraphrases measured and
      recorded, with the magnitudes stated.
- [ ] H0 response at real paraphrase displacements compared against the
      synthetic curve at matched magnitude.
- [ ] `backlog/docs/phase0-first-results.md` updated to say whether the
      calibration curve holds for real language.
