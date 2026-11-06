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
for the sample that will actually be measured. The per-poem rows from this
alphabetical-slice run were not kept; the probe now writes to
`scratch/output/sentence_probe.csv` (gitignored), which holds the Phase 0
sample rerun below.

### Sentence-splitting verse is reliable

An objection raised and then refuted by the probe. Only 0.4% of poems (4 of
943) contain no `.!?` at all, and no author has a suspect median — including
Dickinson, with 446 poems in the slice. Her dash-heavy punctuation does not
make splitting *fail*; it makes it yield few units, which is a precision
problem and is handled by the ≥8-sentence floor below, not a validity problem.

*Qualified by the rerun below: within the Phase 0 sample, this holds for every
author except Dickinson.*

### Rerun on the Phase 0 sample (2026-11-06)

The probe was rerun the same day against the sample that will actually be
measured (`data/processed/poetry_phase0_sample.parquet`: 240 poems, 60 per arm,
76 authors, at most five poems per author per arm), with
`uv run python scratch/sentence_probe.py --phase0-sample`. No rule changed. The
numbers below replace the indicative ones above wherever they differ.

**The premise holds almost exactly.** Over 28,461 lines: 67.5% sit wholly
inside a sentence, 21.2% end at a boundary, 11.3% straddle one (against 68.0 /
21.6 / 10.4 on the alphabetical slice).

**Sentence counts, the full sample.** Dickinson is in it, but only 11 poems,
so no exclusion is needed:

| arm | med. lines | med. sentences | poems with ≥8 sentences |
|-|-|-|-|
| refrain_song | 42 | 15.5 | 44 of 60 |
| irregular | 48.5 | 13 | 38 of 60 |
| ballad_stanza | 20 | 6 | **20 of 60** |
| sonnet | 14 | **3** | 5 of 60 |

What moved materially:

- **Primary B is thinner than estimated.** It keeps 102 of the 180
  non-sonnet poems (57%), not roughly two-thirds. The ballad_stanza arm is the
  weak point: 20 poems, down from an estimated 49% retention.
- **Sonnets now sit at a median of 3 sentences**, below the 4-point minimum
  rather than at it. But **5 of 60 sonnets do reach 8 sentences**, so
  "excluded by construction" is no longer literally true of the floor alone.
  **OPEN for Sungyeon:** either drop the sonnet arm from B by rule, or admit
  those 5. A 5-poem arm cannot carry a comparison, so dropping it is the
  natural reading. Either way it has to be settled before B is run.
- **Dickinson's punctuation does defeat splitting in the measured sample.** 4
  of her 11 poems contain no `.!?` at all (these are the 4 of 240, 1.7%,
  replacing the 0.4% above), and her median is 2 sentences. Splitting on
  dashes as well would give 5–29 units per poem. Her maximum under the real
  splitter is 6, so **the ≥8 floor removes all of her poems from Primary B**.
  This does no harm, because the floor is doing the job it was set for. The
  consequence for the corpus is that Dickinson prose (her letters) can only
  serve Primary A.
- **Michael Drayton is also flagged** (8 poems, median 2 sentences), but
  correctly: his sonnets are long, fully punctuated periodic sentences, and a
  14-line sonnet in two sentences is what the text actually contains. Five of
  his eight are sonnets, which B excludes anyway.

Mean line length per arm is 6.4–8.1 words, consistent with the 5.8–7.9 range
quoted above. Sentence length within poems is 23–34 words.

## Which poems and which prose: the selection rule

Fixed by Sungyeon on 2026-11-06, before any prose was downloaded and before any
poem was drawn. The inventory behind it is in `task-8-prose-sources.md`.

**This replaces the Phase 0 sample as the source of poems.** In this
comparison the four poetry forms (sonnet, refrain_song, ballad_stanza,
irregular) are not a control parameter. The control is the pairing of each poem
with its own author's prose. So poems are drawn **per poet from the whole
PoetryDB corpus**. Form is recorded with every poem and reported as a covariate
(described, never used to include or exclude). The probe figures above describe
the Phase 0 sample. They show the scale of the segmentation problem, but they
are not the retention figures for this comparison. Those come from the draw.

1. **Poets.** The 12 first-pass poets: Shelley, Byron, Edward Thomas, Burns,
   Robert Browning, Stevenson, Swinburne, Elizabeth Barrett Browning, Poe,
   Whitman, Coleridge, Keats. Each has non-fiction prose of their own on
   Project Gutenberg. Later additions are reported separately and never merged
   silently into the first pass: Donne, Milton, Cowper, Brooke, Moore, Mary
   Robinson, and Dickinson from a non-Gutenberg source. Edward Thomas is in, and
   is also reported on his own, because his lyrical nature prose makes him the
   most stringent pairing.
   **Burns** is also reported on his own (added 2026-11-06, at the draw). His
   poems are largely in Scots and his letters in standard English. Dialect
   words may be placed idiosyncratically by the embedding model, which would
   push his poems' spread in the same direction as the claim.
2. **Eligible poems.**
   - Wrap fraction at most 0.10, the existing rule (`MAX_WRAP_FRACTION` in
     `src/poetry_forms.py`).
   - **4 to 200 distinct lines.**
   - The ceiling keeps a whole epic out of the draw. PoetryDB stores Byron's
     *Don Juan* as one poem of 16,088 lines, and its matched prose would span
     whole volumes. The ceiling also keeps a poem a single text rather than a
     book.
   - The eligible pool runs from 17 poems (Keats) to 247 (Shelley), 896 in
     all.
3. **The draw.**
   - **10 poems per poet**, drawn uniformly at random from that poet's
     eligible pool, with **seed 20261106**, the date the rule was fixed.
   - **No redraws.** A drawn poem that later turns out to be unusable (for
     example a duplicate, or a mislabelled translation) is replaced by the next
     poem in the same seeded order, and the replacement is recorded.
   - About 120 poems in all.
4. **Prose: letters and essays only.** No fiction, no drama, no "prose poems"
   (Poe's *Eureka*). Prose is tagged *personal* (letters, journals, travel,
   memoir) or *argued* (essays, criticism, prefaces, treatises), and the two are
   reported separately as already set out under "Prose register" below.
5. **Authorship: only the poet's own prose, written alone.** Before any segment
   is cut, remove:
   - **text by other hands:** editors' footnotes, introductions and linking
     narrative, and letters *to* the poet;
   - **co-written works:** Shelley's *Six Weeks' Tour* is excluded;
   - **speech transcribed by others:** Coleridge's *Table Talk* is excluded;
   - **all quotation, verse quotation above all:** Swinburne quoting
     Shakespeare, Poe quoting *The Raven*. Verse inside the prose arm would blur
     the very contrast under test.

   In a two-writer collection (the Browning–Barrett letters), each poet's poems
   are matched only with that poet's own letters.
6. **Matching passages.**
   - Each poem gets its own passage of its poet's prose, **never overlapping**
     another poem's passage.
   - The passage starts at a random offset under the same seed, never at a
     work's opening, and never inside front matter or editors' material.
   - Record the work, the offset and the register with every match.
7. **Analysis carried with the draw.**
   - Comparison B admits **every** drawn poem with at least 8 sentences,
     whatever its form, sonnets included.
   - Comparison A runs twice: on all drawn poems, and on **exactly B's poems**,
     so that A against B is like for like.
   - Results are reported per poet, with a leave-one-poet-out check: rerun
     dropping each poet in turn.

### Descriptive layer: per-poet persistence diagrams

Sungyeon's picture of the analysis (2026-11-06): for each poet, set the
distribution of topological features of their poems against that of their
prose.

- **Each poem, and each prose match, stays its own cloud** with its own
  diagram. Never pool a poet's poems into one cloud: that would mix distances
  within a poem with distances between poems, which is the
  document-level/corpus-level conflation `CLAUDE.md` warns against.
- Per poet, **compare the distribution of H0 bar lengths** across the 10 poem
  diagrams with the same for the 10 prose diagrams: one panel per poet, poems
  against prose. This is likely the figure that shows the result.
- **This layer describes; it does not decide.** The verdict is reached only by
  the rule fixed earlier: the paired mean H0 lifetime, across three models. A
  difference in distribution shape with no difference in the mean is reported
  as what it is.

## The cutting rule

### Primary A — line level, word-matched prose

For each selected poem:

1. Take its **distinct** lines after wrap-fragment filtering (`verse_lines` in
   `src/3_embed_text.py`), **and after dropping lines that are only a section
   numeral** ("XIII", "4."). Those are headings, not verse; added 2026-11-06,
   see `task-8-poem-draw.md`. Call that count *n*, and their total word count
   *W*.
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
restricted to poems with **at least 8 sentences**, whatever their form. Most
sonnets fall below the floor (median 3 sentences in the Phase 0 sample), but
a long one that clears it is admitted. Amended 2026-11-06: this originally
read "sonnets are excluded by construction", which treated form as a criterion
when only point count is.

A and B are **co-primary, not test-and-robustness-check**. Neither dominates:
A keeps every selected poem but compares a crafted unit against a mechanical
one; B compares two natural units but loses the poems with fewer than 8
sentences (43% of the non-sonnets in the Phase 0 sample; the real figure comes
from the draw). Because they then cover different poems, **A is also run on
exactly B's poems**, and it is that run that is set against B. Agreement
between them is strong evidence. **Disagreement is
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

- The first probe used the **first 40 authors alphabetically**. It was rerun on
  the Phase 0 sample the same day. See "Rerun on the Phase 0 sample" above,
  whose figures take precedence.
- The **≥8-sentence floor is a judgement call**. It sits above the pipeline's
  4-point minimum and well below the 25-point H1 floor, which does not apply to
  an H0 claim. H0 on 8 points is 7 finite bars: thin, but measurable.
- Prose sentence lengths for these authors are **not yet measured**. Nothing in
  the rule depends on them — *k* comes from each poem — but Primary B's residual
  length gap cannot be quantified until the prose corpus exists.

## Status

**Fully specified as of 2026-11-06.** The cutting rule, the selection rule and
the descriptive layer are all fixed. No poem has been drawn, no prose
downloaded and no H0 measured. The sonnet question is settled: form is not a
criterion.

Next in task-8:

1. ~~Run the seeded draw.~~ Done 2026-11-06: `task-8-poem-draw.md`.
2. Download and clean the 12 poets' prose under the authorship rule.
3. Wire EmbeddingGemma 2 into `src/embedding.py` as a third `--model` key.
