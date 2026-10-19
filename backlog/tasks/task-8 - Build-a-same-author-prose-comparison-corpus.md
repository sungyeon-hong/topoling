---
id: task-8
title: Build a same-author prose comparison corpus and test the poetry-spread claim
status: To Do
priority: high
created: 2026-10-19
updated: 2026-10-19
labels: [phase-0, data, critical-path]
depends_on: [task-3]
---

## What this is

task-3's claim compares poetry with ordinary prose: a poem's lines spread more
widely across semantic space than prose by the same authors, yet stay linked,
giving longer H0 bars than prose but shorter than an unordered bag of lines.
Every control so far is drawn from poetry, so the comparison corpus does not
exist. This task builds it and runs the test.

## Why same-author prose

It holds authorial voice and period constant, so only the mode of writing
changes. Public-domain candidates among the Phase 0 poets: Shelley's
*A Defence of Poetry* and essays, Byron's letters and journals, Dickinson's
letters, Burns's correspondence, Coleridge's *Biographia Literaria*,
Wordsworth's prefaces, Keats's letters. Project Gutenberg holds most of these.
A topic-matched corpus (encyclopaedia text on the poems' subjects) is the
fallback if same-author coverage is too thin.

## The confound to settle before any numbers

**Unit mismatch.** A poem line is a short fragment; a prose sentence is longer
and complete. Short fragments may embed more erratically and look "wider" for a
trivial reason. Options, to be decided before running:

- cut prose into segments of the same word length as the paired poems' lines;
- or compare sentence against sentence, splitting poems into sentences (which
  loses the poems below the H1 floor quickly).

Report how segment length alone moves H0, so the effect of segmentation is
known separately from the effect of genre.

## What counts as finished

- [ ] A prose corpus by Phase 0 poets is collected, with provenance and
      cleaning recorded (the same wrap-fragment care as PoetryDB).
- [ ] The unit-matching rule is chosen and written down before results.
- [ ] Poems and matched prose clouds are compared at matched point count on
      H0, under both embedding models.
- [ ] Order-aware support: distance between consecutive lines vs consecutive
      prose segments, each against a shuffled-order control.
- [ ] Findings written to `backlog/docs/`, stating plainly whether the claim
      survived.
