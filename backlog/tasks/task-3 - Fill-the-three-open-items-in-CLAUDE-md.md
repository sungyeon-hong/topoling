---
id: task-3
title: Fill the three open items in CLAUDE.md
status: In Progress
priority: high
created: 2026-09-14
updated: 2026-10-19
labels: [documentation, sungyeon-only]
depends_on: []
---

## What this is

Three items in `CLAUDE.md` have been marked `OPEN` since 2026-08-12 and need
Sungyeon specifically. Nobody else can supply them.

1. **The falsifiable one-sentence claim.** What, stated in one sentence, would
   this project be wrong about? Everything downstream — which comparison is the
   headline, which baseline matters, what a negative result looks like —
   depends on this being written down.
2. **The intended output.** Paper, thesis chapter, or fellowship deliverable.
   This decides scope and timeline, and it decides how much the Phase 1 arXiv
   work needs to carry.
3. **The record of approaches already ruled out.** Embedding models that were
   wrong for this text, filtrations that produced nothing, framings that drew
   pushback. Without this written down, an assistant will keep re-proposing
   things already tried and rejected, which wastes sessions.

## Why it matters now

The first Phase 0 results exist, and they point somewhere specific: the
instrument measures semantic dispersion rather than loops, and near-duplicates
rather than verbatim repetition. That is enough evidence to make the falsifiable
claim concrete rather than aspirational, which was not true in August.

Item 3 has also become more valuable: this session ruled out verbatim
repetition as ground truth and the shuffled-line control as a nuisance
calibration, both for structural reasons. Those belong in the record.

## What counts as finished

- [ ] All three `OPEN` markers in `CLAUDE.md` replaced with content.

## Update 2026-09-30 — the second item is now half answered

Sungyeon has named a concrete short-term output: **an abstract and preliminary results for a conference**, on the topological signature of explorative pathways in language, with
poetry as the validation corpus. The venue and timeline are kept outside this repository, because they carry venue and positioning material.

That raises this task's priority to high and makes the **falsifiable
one-sentence claim the critical path**. It is the abstract's first sentence,
and the figures and framing both follow from it. It cannot be deferred past
October 2026 without compressing the whole schedule.

The longer-horizon question — paper, thesis chapter or fellowship deliverable —
is still open. A conference abstract is a milestone, not the destination.

## Update 2026-10-19 — the claim is written (item 1 done)

Sungyeon clarified what they mean by novelty: a poem is written differently
from an ordinary description, with more metaphors and novel links connecting
seemingly distant notions together, which may not arise in usual or formal
writing. Their hypothesis is that poetry exhibits a wider spread of semantic
features than usual texts, especially in H0.

Made precise together, and agreed by Sungyeon:

> Compared with prose by the same authors, cut into segments of the same
> length, a poem's lines spread more widely across semantic space yet stay
> linked to one another, giving longer H0 bars than prose but shorter than an
> unordered bag of lines.

**False if** poems' H0 bars are no longer than the matched prose under both
embedding models.

Notes on the wording:

- **"Wider spread" means longer H0 bars, not larger components.** Lines further
  from their nearest neighbours break into more, smaller components at a given
  scale, which merge later.
- **The claim has two halves.** Wide spread (distant notions) and bridging
  (metaphor links them). The existing result that poems are *tighter* than
  bags of other verse lines already supports the bridging half; the prose
  comparison tests the spread half.
- **Metaphor is the explanation, not the measurement.** Sentence embeddings may
  not represent metaphor as metaphor.
- **The unit mismatch is the main confound.** Poem lines are short fragments,
  prose sentences longer and complete; short fragments may embed more
  erratically and look "wider" for a trivial reason. Match segment length.
- **Same-author prose** was chosen because it holds voice and period fixed.

Also agreed: an order-aware measure (distance between consecutive lines, with
a shuffled control) as support, since metaphor's "leaps" are a claim about
flow that plain Rips cannot see. Fuller discourse analysis, and rhetorical
move analysis of arXiv abstracts, are follow-on work.

Item 1 done. Item 2 half done (conference abstract short term; longer horizon
open). **Item 3, the record of approaches Sungyeon has already ruled out, is
still open.** Testing the claim is task-8.

- [x] Item 1, the falsifiable claim, written into `CLAUDE.md`.
