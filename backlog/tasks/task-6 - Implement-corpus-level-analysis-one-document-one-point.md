---
id: task-6
title: Implement corpus-level analysis (one document = one point)
status: To Do
priority: high
created: 2026-09-30
updated: 2026-09-30
labels: [methodology, phase-1, blocking]
depends_on: [task-2]
---

## What this is

Build the second unit of analysis. Everything in the project so far is
document-level: one *line* of a poem is a point, and one poem is the cloud.
This task builds the corpus-level view, where one *document* is a point and a
corpus (or a single year of one) is the cloud.

## Why it matters

`CLAUDE.md` is explicit that these are two different measurements answering
two different questions, and that **the homogenisation claim lives at corpus
level**. Document-level work measures internal rhetorical structure and flow.
Between-document diversity — whether a body of writing is spreading out or
converging on a semantic mean — is only visible when each document is a point.

So the instrument validated by task-1 does not currently measure the quantity
the project's motivating claim is about. That is fine as far as Phase 0 goes,
because Phase 0 is instrument validation on poetry. It is blocking for anything
that touches the claim about generative AI narrowing the range of expression.

## What it involves

Most of the machinery already exists and should be reused rather than rewritten:
`embedding.py` for the model choice and L2 normalisation, `topology.py` for the
diagrams and the corpus control.

The genuinely new piece is the one `CLAUDE.md` calls the single most important
design choice for any time-series claim: **fixing the point count**. Persistence
statistics move with cardinality, so a corpus of 500 documents and one of 5,000
will differ for entirely trivial reasons. Subsample to a fixed *n* (~300) with
*B* bootstrap replicates and report the distribution, which yields error bars
for free.

Two constraints carry over and must not be relaxed:

- **No mean-centring per corpus or per year.** That removes exactly the
  between-group offset being measured.
- **No UMAP or t-SNE before ripser.** If dimension reduction is needed, use PCA
  or Matryoshka truncation, fitted once on pooled data.

## What counts as finished

- [ ] A corpus-level pipeline exists that takes a set of documents and returns
      persistence statistics with bootstrap error bars at fixed cardinality.
- [ ] It runs under both embedding models, tagged the way steps 3-5 are, so the
      task-1 robustness rule can be applied to any result it produces.
- [ ] Run on the poetry corpus as a sanity check, where poetry is expected to
      sit at the high-diversity end of the measurement scale.
- [ ] The document-level and corpus-level measurements are kept clearly
      labelled as separate quantities. `CLAUDE.md` warns that conflating them
      in a figure will mislead.
