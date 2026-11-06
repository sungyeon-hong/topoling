---
id: task-9
title: Audit the Phase 0 sample for drama, translations and numeral-only lines
status: To Do
priority: medium
created: 2026-11-06
updated: 2026-11-06
labels: [phase-0, data, data-quality]
depends_on: []
---

## What this is

Found in passing while running the task-8 draw (see
`backlog/docs/task-8-poem-draw.md`). The Phase 0 sample
(`data/processed/poetry_phase0_sample.parquet`, 240 poems) was built by
mechanical form detection. Nobody has read through it for content that is not a
poem by the named poet.

Known so far:

- **Verse drama:** Shelley's *Oedipus Tyrannus or Swellfoot the Tyrant* (927
  distinct lines), labelled refrain_song; Shelley's *Scenes from the Magico
  Prodigioso*, labelled irregular.
- **Translation:** the *Magico Prodigioso* scenes are translated from Calderón.
- **Numeral-only lines** (section numbers such as "XIII") in 8 of 240 poems,
  embedded as points. Small: 4.5% of those poems' points on average, 9% at most.

Not yet checked: misattribution (the task-8 draw found a Felicia Hemans poem
under Elizabeth Barrett Browning's name) and duplicates under different titles.

## Why it matters

Phase 0's published findings (form separation, the calibration curve, H1 as
coherence) rest on this sample, and its release is archived with a DOI. Two
very long dramas in a 60-poem arm could move arm-level H0 summaries, though
the matched-cardinality controls limit how far.

## What counts as finished

- [ ] Read through the 240 poems' titles and openings and list every drama,
      translation, misattribution and duplicate, using the flags in
      `src/draw_task8_poems.py` as a first pass.
- [ ] Decide with Sungyeon whether to rerun Phase 0 without them, or record the
      list and check the arm-level results are robust to dropping them.
- [ ] Decide whether numeral-only lines should be dropped in `verse_lines`
      for every stage, not just task-8. This changes Phase 0 point counts, so
      it is a rerun decision too.
- [ ] Findings written to `backlog/docs/`.
