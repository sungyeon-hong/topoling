# The segmentation rule for the poetry–prose comparison

Decided 2026-11-06, **before any prose was collected and before any H0 number
was produced**. That ordering is the whole point: the confound described below
runs in the same direction as the claim, so a rule chosen after seeing results
would be worthless.

This closes task-8's second acceptance criterion. It fixes how poems and prose
are cut into points, which comparisons are primary, and what must be reported
alongside every H0 number for that number to be readable.

## The problem: the artifact predicts the result

The claim (`CLAUDE.md`, task-3, 2026-10-19) is that a poem's lines spread more
widely across semantic space than prose by the same authors — longer H0 bars
for poems than for matched prose.

Short segments embed further apart than long ones, for two reasons that have
nothing to do with genre:

- **Averaging.** A segment's vector is roughly an average over its content. The
  more content, the more it regresses toward the centroid of the document's
  topic and register, so segments of a long-form document cluster tightly.
- **Underdetermination.** A short fragment does not pin down a meaning, so the
  model places it more idiosyncratically, and idiosyncratic placement reads as
  distance.

Both shrink pairwise distances as segment length grows, so both produce
**longer H0 bars for shorter segments**.

A poem line measured here runs 5.8–7.9 words by arm. Romantic-era prose
sentences run far longer. The mismatch is severalfold and it points the same
way the hypothesis does, so an uncontrolled poem-versus-prose comparison cannot
come out any way *but* "supported", whatever is true about poetry. That would
not be a weak test; it would not be a test.

## What the probe established

`scratch/sentence_probe.py`, run 2026-11-06 against PoetryDB: 1316 poems by the
first 40 authors alphabetically, 943 of them in the four Phase 0 arms. It was
written to answer one question — does a sentence-level cloud have enough points
to measure H0 on — and it answered a second that mattered more.

### A poem's line is a sub-sentential fragment

Across 121,544 verse lines:

| where the line sits | share |
|-|-|
| wholly inside a sentence | **68.0%** |
| ends at a sentence boundary | 21.6% |
| straddles a boundary | 10.4% |

Barely a fifth of lines coincide with a sentence. A poem's *sentence* runs about
22 words; its *line* about 6.4. **Lineation is a partition imposed on continuous
syntax**, which is the premise Sungyeon raised, and it is now measured rather
than assumed.

This cuts the opposite way from how it first looks. If a line is a
sub-sentential cut through running syntax, then cutting prose sub-sententially
is the *faithful analogue* of what a poem does to itself, not a mutilation of
prose. It also fixes a detail: at a 10.4% straddle rate, prose chunks should be
cut continuously rather than forced to respect sentence boundaries.

### Sentence counts: viable in two arms, marginal in one, dead in one

Median sentences per poem, against the line counts currently used as points:

| arm | med. lines | med. sentences | ≥8 sent | ≥12 sent |
|-|-|-|-|-|
| refrain_song | 39 | 15 | 77% | 59% |
| irregular | 48 | 12 | 65% | 53% |
| ballad_stanza | 24 | 7 | 49% | 25% |
| sonnet | 14 | 4 | 10% | 2% |

Dickinson is excluded from this table. In the raw probe she is 50% of the
ballad arm and 35% of irregular, and she halves both medians; the Phase 0
sampler caps any author at five poems (`max_per_author=5` in
`poetry_forms.stratified_sample`), so the excluded column is the better proxy
for the sample that will actually be measured. The uncapped figures are in
`scratch/sentence_probe.csv`.

### Sentence-splitting verse is reliable

An objection raised and then refuted by the probe. Only 0.4% of poems (4 of
943) contain no `.!?` at all, and no author has a suspect median — including
Dickinson, with 446 poems in the slice. Her dash-heavy punctuation does not
make splitting *fail*; it makes it yield few units, which is a precision
problem and is handled by the ≥8-sentence floor below, not a validity problem.

## The rule

### Primary A — line level, word-matched prose

For each poem in the Phase 0 sample:

1. Take its **distinct** lines after wrap-fragment filtering (`verse_lines` in
   `src/3_embed_text.py`). Call that count *n*, and their total word count *W*.
   Distinct rather than raw, because `dedup()` in `src/5_compute_ph.py` is what
   the diagram actually sees — the same rule the project already applies to
   cardinality everywhere else.
2. Set **k = round(W / n)**, the poem's own mean words per distinct line.
3. Take a contiguous stretch of *n* × *k* words of prose by the same author and
   cut it into *n* segments of *k* words, **cutting straight through sentence
   boundaries** as lineation does.

Poem and prose match then agree on word budget, granularity and point count;
only whose words they are differs. *k* is per poem rather than global, so a
ballad's six-word lines meet six-word prose chunks and a blank-verse poem's ten
meet ten.

The mean is used rather than the median because *W*/*n* is what makes the word
budget match exactly; *k* is recorded per poem so a freak long line is
checkable after the fact. Rounding lets *n* × *k* differ from *W* by a few
words — take *n* × *k*, record both.

Because *n* matches exactly, the existing matched-cardinality control machinery
applies unchanged and raw `h0_mean_life_nondup` is directly comparable between a
poem and its match. **The headline statistic is the paired raw value**, with
excess-over-corpus-control reported alongside for continuity with Phase 0
rather than as the test.

### Primary B — sentence level, sentence against sentence

Poem sentences against prose sentences by the same author, *n* matched,
restricted to poems with **at least 8 sentences**. Sonnets are excluded by
construction and this is stated up front, not discovered afterwards.

A and B are **co-primary, not test-and-robustness-check**. Neither dominates:
A keeps all four arms and all 240 poems but compares a crafted unit against a
mechanical one; B compares two natural units but loses an arm and roughly a
third of the rest. Agreement between them is strong evidence. **Disagreement is
itself a finding and gets reported as one** — it must not be resolved by
keeping whichever number is friendlier.

Sentence length is *not* assumed matched under B, only closer. Report mean
words per segment for both arms of every pair. If prose sentences prove much
longer than poem sentences, the fallback is length-stratified sampling: draw
real prose sentences whose word lengths match the poem's sentence-length
distribution one-to-one, from within a single contiguous window so topical
coherence is not destroyed. Real units, matched length, no chopping.

### The lineation control

Same poem, same *k*, same *n*, same words — cut at the poet's line breaks
versus cut blindly, ignoring lineation. Nothing differs but the cut points.

This separates two claims that the project's own wording runs together:

- **(A) poetry's *language* is wider** — metaphor and distant links, which live
  in the words and survive re-cutting;
- **(B) poetry *as presented* is wider** — including lineation, which is a
  deliberate, genre-defining choice.

If the effect holds under blind re-cutting it is (A). If it appears only at the
poet's line breaks it is (B), which is a finding about composition rather than
about novelty, and the claim would need rewording to match.

### Length calibration

A prose-only sweep of global *k* ∈ {5, 8, 12, 20, 35} at fixed *n*, run once, to
characterise the length–H0 relationship in absolute terms rather than only as a
poem–prose difference. Any residual length gap under B is read against this
curve.

## Reported alongside, always

**Content words per segment.** Cutting prose sub-sententially can produce
near-contentless fragments — *"of the imagination, which is the"*. Those may
pile up in a low-content region, biasing the prose arm **narrower** and
spuriously favouring the claim. Report mean non-stopword tokens per segment for
both arms of every comparison. A poem:prose ratio within 0.9–1.1 is treated as
acceptable; outside it the comparison is reported as void whatever H0 says. The
band is provisional — no data exists yet to set it properly. Revisit once the
corpus is collected, and say so if it is revised.

**Prose register, stratified.** A sustained treatise (Shelley's *Defence*,
Coleridge's *Biographia*) is argued around one thesis and will be tight for
reasons of discourse rather than of formality. Letters and journals (Byron,
Keats, Dickinson) wander and sit closer to the poems' register. Report
essay-prose and letter-prose **separately**. If the gap holds against letters it
is a much stronger result; if it holds only against treatises, something has
been learned, but it is not what the claim asserts.

**Passage position.** Sample prose at random offsets within a work, never from
its opening; exclude front matter, prefaces by other hands and editorial
apparatus. Record the offset.

## Rejected, and why

**Sentence level as the sole primary.** Rejected on point counts. Sonnets give a
median of 4 sentences, below the 4-point minimum in `src/3_embed_text.py`, and
ballad_stanza gives 7. It would empty one arm and thin another badly. It
survives as Primary B on the arms that can carry it.

**A single global *k* for all poems.** Rejected because it breaks exact pairing:
any poem whose lines are longer or shorter than the global value gets a prose
match at the wrong granularity, reintroducing the confound poem by poem. The
global sweep survives as a calibration curve, not as a comparison.

**Leaving the length confound uncontrolled and arguing it away in prose.**
Recorded here only so it is on the file as considered and refused. The artifact
and the hypothesis are collinear; no amount of discussion separates them after
the fact.

**The 25-point H1 floor as an objection to sentence level.** Raised in session
and withdrawn: the claim under test is H0-only, so that floor does not bind. The
binding constraint is the 4-point minimum. Noted because the floor is easy to
over-apply.

## Caveats on these numbers

- The probe uses the **first 40 authors alphabetically**, not the Phase 0
  stratified sample. It is indicative. Rerun `scratch/sentence_probe.py` against
  `data/processed/poetry_phase0_sample.parquet` once `data/` is regenerated, and
  amend this document if the arm medians move materially.
- The **≥8-sentence floor is a judgement call**. It sits above the pipeline's
  4-point minimum and well below the 25-point H1 floor, which does not apply to
  an H0 claim. H0 on 8 points is 7 finite bars: thin, but measurable.
- Prose sentence lengths for these authors are **not yet measured**. Nothing in
  the rule depends on them — *k* comes from each poem — but Primary B's residual
  length gap cannot be quantified until the prose corpus exists.

## Status

Decided and written down. Nothing has been measured. Next in task-8: collect the
prose corpus, and wire EmbeddingGemma 2 into `src/embedding.py` as a third
`--model` key.
