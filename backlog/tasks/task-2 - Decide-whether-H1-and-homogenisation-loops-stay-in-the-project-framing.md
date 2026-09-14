---
id: task-2
title: Decide whether H1 and the "homogenisation loops" framing stay in the project
status: To Do
priority: high
created: 2026-09-14
updated: 2026-09-14
labels: [phase-0, framing, decision]
depends_on: [task-1]
---

## What this is

A decision, not an analysis: does the project keep first-order persistent
homology — H1, the loops — in its central claim, or does it become an
H0 project about semantic dispersion?

## Why it matters

The `Aim` section of `CLAUDE.md`, and the fellowship abstract it was
reconstructed from, both lead on detecting "homogenisation loops". H1 is what
would detect a loop. In the first Phase 0 run (2026-09-07) H1 showed nothing in
any condition tested:

- no trend across synthetic refrain strength (p = 0.11 to 0.58),
- no discrimination across refrain displacement once point count was matched
  (excess H1 count sat flat at -4.5 to -5.4 for every displacement above zero),
- no separation between the four real form arms.

H0 carried the entire signal. That is one model and one construction, so it is
not yet a verdict — hence the dependency on task-1.

Independent corroboration is worth weighing. The `panic-tda` project's
TASK-77, a keep/kill pilot asking whether topological data analysis earns a
place in that paper, reaches the same conclusion from different data: Rips
persistent homology on 25-100 points is unreliable beyond H0, H0 duplicates
hierarchical clustering, and persistence entropy is confounded by bar count
from duplicate captions. Two projects hitting the same wall independently is
evidence about the method, not about either dataset.

## The options

1. **Keep H1, conditional on task-1.** Only defensible if mpnet shows H1
   structure that Nomic missed.
2. **Move to sliding-window persistence.** Plain Rips is permutation-invariant
   (see `docs/glossary.md`), so it is blind to order by construction, and a
   loop in a *trajectory* is a different object from a loop in a *set*. This is
   the route panic-tda's TASK-77 identifies as the only candidate value-add.
   It would change what topoling measures, not just how.
3. **Become an H0 project.** Reframe around semantic dispersion and
   convergence, which is what the instrument demonstrably measures, and retire
   "homogenisation loops" to the discussion as a hypothesis that did not
   survive. Honest, and still answers the original research question.

## What counts as finished

- [ ] task-1 complete, so the H1 null is known to be model-independent or not.
- [ ] One option chosen and written into `CLAUDE.md`'s Aim section.
- [ ] If H1 is dropped or deferred, the wording of any fellowship or
      publication material that promises loop detection is revisited.
