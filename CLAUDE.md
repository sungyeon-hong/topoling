# topoling project overview

*Drafted from the code on 2026-08-12; method decisions below reflect Sungyeon's
answers of the same date. Items still marked* **OPEN** *need Sungyeon.*

topoling (topology + linguistics) applies **persistent homology to text
corpora** to measure whether a body of writing is structurally exploratory or
converging on a semantic mean.

**Start here (added 2026-09-14):** work records live in `backlog/`.
`backlog/tasks/` holds numbered task files with a status; `backlog/docs/` holds
findings. Read `backlog/docs/glossary.md` first if any vocabulary below is
unfamiliar, then `backlog/docs/phase0-first-results.md` for what is currently
known, then `backlog/docs/task-1-embedding-model-robustness.md` for what
survived a change of embedding model, then the tasks in number order. **task-1
is Done (2026-09-18) and no longer gates anything.** The Phase 0 findings
replicated under `all-mpnet-base-v2`, with the exceptions recorded in that
document. **task-2 is Done (2026-10-19)** -- see
`backlog/docs/task-2-h1-decision.md`. task-3's claim is recorded (2026-10-19); task-8, the prose comparison corpus, now gates it.

## Aim

Generative AI is a "super-convergent" engine: it predicts the statistically
probable next token, so AI-co-produced writing may be pulled toward the semantic
mean. Individual productivity rises while collective narrative diversity narrows
(Doshi & Hauser, 2024) — a structural effect rather than a failure of individual
agency (Ferdman, 2025). There is currently no established methodology to
quantify this systemic thinning of ideas.

This project builds that diagnostic. It treats a document (or a corpus) as a
**point cloud in semantic space** and uses persistent homology (Carlsson, 2009)
to track connectivity (H0) and loops (H1) across scales, looking for signatures
that surface statistics cannot detect.

### What each phase claims

Decided 2026-10-19 in task-2; see `backlog/docs/task-2-h1-decision.md`.

- **Phase 1, arXiv, corpus level: homogenisation is the motivation here.**
  Whether "homogenisation loops" and the loss of conceptual frontiers show up as
  corpus-level H1 is an **open question**, not a finding. Write the prediction
  down before task-6 or task-7 produces numbers.
- **Phase 0, poetry, document level: no homogenisation claim.** Sungyeon's
  motivation for poetry is to see whether novel or unusual expression shows
  identifiable patterns under topological analysis. H0 is the headline
  measurement. H1 is reported as a supporting coherence measure: real poems have
  about 15% fewer loops than size-matched controls, which fits Sungyeon's
  reading that poems are short and leaner in structure than usual texts. It does
  not discriminate form.
- **Sliding-window persistence** (the only construction that sees line order) is
  future work, outside the conference timeline.

**"Structural openness" means** a shift toward different styles and different
formulations of ideas, as opposed to "following the crowd". It is *not* a claim
about randomness — a maximally random corpus is not the ideal. See Baselines.

**Testable claim (Sungyeon, 2026-10-19; task-3):** compared with prose by the
same authors, cut into segments of the same length, a poem's lines spread more
widely across semantic space yet stay linked to one another, giving longer H0
bars than prose but shorter than an unordered bag of lines. **It is false if**
poems' H0 bars are no longer than the matched prose under both embedding
models. Sungyeon's reasoning: a poem is written differently from an ordinary
description, with more metaphors and novel links connecting seemingly distant
notions, which formal writing does not produce. Metaphor is the *explanation*;
the claim is about semantic spread and bridging, because sentence embeddings
may not represent metaphor as metaphor. Testing it needs a prose comparison
corpus: task-8.

**Intended output:** a conference abstract in the short term (venue and plan
kept outside the repository). The longer-horizon output (paper, thesis chapter
or fellowship deliverable) is still OPEN.

## Relationship to other projects

- **panic-tda** — shares the "TDA over generative-AI semantic trajectories"
  frame, but studies *recursive model-to-model* trajectories. topoling studies
  *human-authored corpora over historical time*. Keep method vocabulary and
  embedding-model choices aligned so results are comparable across the two.
- **geometry-driven-hyperuniformity** — methodologically unrelated. An early
  proof-of-concept script borrowed text and dependency pins from it; neither was
  carried into this public repository.

## Phasing

**Poetry comes first, and it is instrument validation — not a comparison arm.**
*(2026-10-19: Sungyeon's stated motivation now goes further -- whether novel or
unusual expression shows identifiable topological patterns; see Aim. The current
arms test form, not novelty; closing that gap belongs to task-3.)*

- **Phase 0 (current): poetry.** Establish that persistent homology detects
  known structural signatures in human writing at all, using PoetryDB. Poetry is
  the right starting corpus because **fixed forms provide ground truth**: lines
  repeated verbatim are near-duplicate points and should produce a predictable
  H0/H1 signature; a sonnet is 14 lines with a volta near line 8–9, predicting a
  split. If PH cannot separate the forms, it will not detect the far subtler
  homogenisation signal in abstracts, and the method fails cheaply and early.
  **Revised 2026-09-07: PoetryDB contains no villanelles.** Of 3092 poems, 22
  have the villanelle's 19 lines and none carries two recurring refrains. This
  is not a detection failure. The villanelle became a common English form only
  in the twentieth century, and PoetryDB holds public-domain material predating
  that; it also omits the 1890s revival villanelles (Dowson, Henley, Wilde, E.
  A. Robinson) that *are* public domain, carrying only 1, 6 and 10 poems by the
  first three and no E. A. Robinson at all. The four Phase 0 arms are therefore
  **sonnet / refrain_song / ballad_stanza / irregular**. The `refrain_song` arm
  — songs and hymns whose chorus recurs verbatim — supplies the
  near-duplicate-line geometry the villanelle was wanted for, and being far
  longer (median 48 lines) it clears the H1 point floor a 19-line villanelle
  never could. Free verse is unavailable for the same reason: modern free verse
  is in copyright, so Whitman and Crane are all a public-domain source can
  offer.
- **Phase 1: arXiv.** Apply the validated instrument to academic abstracts over
  historical time.

Poetry is the **high-diversity anchor** — an upper reference point on the same
measurement scale for narrative, metaphor, and expressive range. It is *not*
directly compared to academic prose; the object of interest is the topological
signature of structure, style, and flow in human-created writing.

**Revised 2026-10-19 (Sungyeon, task-3):** poetry *is* now compared directly
with ordinary, non-academic prose by the same authors, because the testable
claim is that poetry spreads wider than ordinary writing (task-8). The
comparison with academic prose is still not made.

## Methodology

Pipeline, as implied by the numbered scripts in src/:

1. **Collect** — arXiv abstracts by category + date window (1_collect_arxiv.py);
   PoetryDB poems (collect_poetrydb_corpus.py, then poetry_forms.py to label
   forms and draw the Phase 0 sample).
2. **Clean** — whitespace/LaTeX-quote normalisation only. Deliberately
   *under*-cleans: mathematical terms must survive (2_clean_text.py).
3. **Embed** — see Method decisions. **Implemented (3_embed_text.py,
   embedding.py).**
4. **Build complexes** — Vietoris–Rips over the point cloud. **Implemented
   (4_build_complexes.py); the complex itself is built inside ripser at step
   5.**
5. **Compute PH** — H0 (connectivity) and H1 (loops). **Implemented
   (5_compute_ph.py, topology.py).** Vectorising via persistence images is **not
   implemented** and has not been needed yet.

## Method decisions

### Unit of analysis — both, but they answer different questions

- **Corpus-level** (one document = one point, corpus/year = the cloud) measures
  *between-document diversity*. **The homogenisation claim lives here.**
- **Document-level** (one sentence or line = one point, document = the cloud)
  measures *internal rhetorical structure and flow*. **Phase 0 poetry lives
  here.**

Do both, but keep them labelled as separate measurements — they are not two
views of one quantity, and conflating them in a figure will mislead.

**Hard constraint on document-level work:** an arXiv abstract is ~6–10
sentences. Vietoris–Rips H1 on 8 points in 768 dimensions is sampling noise, not
argument structure — any loop found is essentially guaranteed and
uninterpretable. Set a floor (~25 points) below which no document-level H1 claim
is made. Poems taken line-by-line often clear this; abstracts do not. So in
practice document-level analysis is poetry-only, unless Phase 1 moves to full
paper texts rather than abstracts.

### Embedding model — switch off SPECTER2 for sentence-level work

The original proof of concept (an early scratch script, not carried into this
public repository) used allenai/specter2_base and took the CLS token per
sentence. This is off-label: SPECTER2 is trained for *document-level* citation
similarity on title+abstract pairs, and the CLS vector of an encoder not tuned
for sentence similarity is a weak sentence representation. It is also
scientific-domain tuned, so it cannot be the cross-corpus model — it would
distort the poetry geometry.

Recommended:

- **Primary: nomic-embed-text-v1.5.** General-domain (handles poems and
  abstracts on equal footing), long context, and Matryoshka-trained so
  embeddings truncate cleanly from 768 → 256/128, which matters for PH runtime.
  panic-tda already uses Nomic, so results become comparable across projects.
- **Robustness check: all-mpnet-base-v2** — different training regime, widely
  used, 768d. If a topological finding flips between the two models, it is a
  model artifact, not a property of the text. Run this before believing
  anything.
- Keep SPECTER2 only for arXiv *document-level* embeddings, where
  citation-similarity geometry is genuinely the thing being measured.

### Normalisation — L2 to the unit sphere, then fix cardinality

1. **L2-normalise every embedding.** Points then lie on the unit sphere and
   Euclidean distance is a monotone function of cosine similarity (‖x−y‖² =
   2−2·cos). Ripser's Euclidean metric then *is* cosine geometry, and the
   filtration is bounded in [0, 2] — so diagrams are comparable across corpora
   and across years with no further rescaling. This is the whole fix for the
   scale-sensitivity problem.
2. **Do not mean-centre per corpus or per year.** That removes precisely the
   between-group offset the project is trying to measure.
3. **Fix the point count.** Persistence statistics depend on cardinality; a year
   with 500 abstracts and one with 5,000 will differ for entirely trivial
   reasons. Subsample to a fixed *n* (e.g. 300) with *B* bootstrap replicates
   and report the distribution. This is the single most important design choice
   for any time-series claim, and it yields error bars for free.
4. **Never run UMAP or t-SNE before PH.** Neither preserves distances; both
   manufacture and destroy topology. umap-learn is in the dependencies — it is
   for *pictures only*, never as input to ripser. If dimension reduction is
   needed, use PCA or Matryoshka truncation, fitted **once on pooled data**,
   never separately per corpus.

### Baselines — two different things, both needed

Sungyeon's framing is right: randomness is not the target, so a "random null" is
not the scientific baseline. But two distinct roles were being conflated:

- **Nuisance calibration (instrument check).** Shuffled-sentence and
  random-points-on-sphere controls are still needed — not as a hypothesis, but
  to know whether an observed feature exceeds what point count and ambient
  dimension alone produce. Cheap, and without it a diagram cannot be read.
- **Scientific baseline (the real comparison).** "Shift in style vs following
  the crowd" is a claim about *change relative to a prior regime*. So the design
  is difference-based: establish the natural drift rate in a pre-2022
  (pre-ChatGPT) window, then test whether the post-2022 trend departs from it.
  Optionally strengthen with a control discipline having low AI-writing adoption
  over the same period — a difference-in-differences shape.
- **Poetry is neither.** It is the high-diversity anchor on the measurement
  scale. For the Phase 0 claim, *same-author prose* is the scientific baseline
  that poetry is compared against (task-8), and a bag of lines from other poems
  remains the nuisance calibration.

## Status

**Phase 0 results are replicated across two embedding models (2026-09-18).** The
pipeline runs end to end on poetry and has produced findings -- see
`backlog/docs/phase0-first-results.md` for the reasoning and
`backlog/docs/task-1-embedding-model-robustness.md` for what is established.
Phase 1 (arXiv) is untouched. Nothing here is publication-track.

| **Component** | **State** |
|-|-|
| src/1_collect_arxiv.py | Works. Hardcoded to math.AT, max_results=5000. Simpler than the scratch version. |
| src/2_clean_text.py | Works. A single function, not wired into anything. |
| src/3_embed_text.py | **Works (2026-09-07).** Embeds Phase 0 sample lines and the synthetic sweep through one pipeline. Drops wrap fragments first; writes embedding_manifest.parquet. |
| src/4_build_complexes.py | **Works (2026-09-07).** Decides which clouds are admissible and records their geometry; writes cloud_geometry.parquet. The complexes themselves are built inside ripser at step 5. |
| src/5_compute_ph.py | **Works (2026-09-07).** H0/H1 against corpus controls matched on *distinct* point count; writes ph_results.parquet. |
| src/embedding.py | **Works (2026-09-07).** Importable. Holds the model choice and enforces L2 normalisation and Nomic's `clustering: ` prefix so callers cannot get them wrong. |
| src/topology.py | **Works (2026-09-07).** Importable. Rips persistent homology plus the two controls, and counts exact duplicates from the cloud rather than the diagram. |
| src/synthetic.py | **Works.** Importable. Builds synthetic villanelles by replanting refrains on the standard schedule, with refrain strength sweepable 1-4. Pairing bug fixed 2026-09-18: it drew a fresh `rng.choice` per strength, and since the number of lines needed shrinks as repetition rises, every strength got different lines. Now draws a permutation once per donor. |
| src/experiment_refrain_sensitivity.py | **Works.** The displacement sweep -- paraphrase modelled as a small nudge of the refrain. Produced Phase 0's most useful result. Seeding bug fixed 2026-09-18: it used Python's `hash()`, which is randomised per process, so the sweep was not reproducible between runs. See task-4. |
| src/compare_models.py | **Works (2026-09-18).** Runs task-1's cross-model comparison over the model-tagged outputs. Compares shapes, never absolute values. |
| src/collect_poetrydb_pilot.py | Superseded by collect_poetrydb_corpus.py. Kept for provenance of the 100-poem pilot. |
| src/collect_poetrydb_corpus.py | **Works (2026-09-07).** Full corpus, 3092 poems / 129 authors. Fetches per author, falls back to per-title when a bulk payload 503s (Byron 324 poems, Shelley 312), caches per author so a rerun is free. |
| src/poetry_forms.py | **Works (2026-09-07).** Mechanical form detection and stratified sampling. Importable, unlike the digit-prefixed scripts, so steps 3-5 can use it. |
| scratch/collect_arxiv_pilot.py | Works, and is the *better* collector — version stripping, dedup, 21-column schema, run summary. |
| main.py | uv init boilerplate. Not an entry point. |
| notebooks/poetry_db.md | Notes on three poetry corpus options (PoetryDB / Gutendex / Gutenberg Poetry Corpus). No notebooks yet. |

## Data on disk

Both pilots, data/raw/, 100 rows each, saved as parquet **and** CSV:

- arxiv_math_CO_2000_pilot.parquet — math.CO, submitted during 2000, 21 cols
  (arxiv_id, title, abstract, text_title_abstract, year, month, categories,
  is_withdrawn, retrieved_at, …)
- poetrydb_pilot.parquet — 7 cols (title, author, linecount, lines, text, …)

**Full PoetryDB corpus and Phase 0 sample (2026-09-07), ~71 MB in total.** data/
is now gitignored: everything in it is reproducible from the two scripts above
and the corpus is ~71 MB. Regenerate with `uv run python
src/collect_poetrydb_corpus.py` then `uv run python src/poetry_forms.py`.

- data/raw/poetrydb_full.parquet - 3092 poems, 129 authors. 640 duplicate ids
  were dropped on collection: PoetryDB's author endpoint matches substrings, so
  some poems arrive under two queries.
- data/processed/poetrydb_labelled.parquet - every poem with structural features
  (stanza profile, refrain counts, repeat_fraction, wrap_fraction,
  meets_h1_floor) and a form label.
- data/processed/poetry_phase0_sample.parquet - the Phase 0 sample: 240 poems,
  60 per arm, 76 authors, largest author share 7%.

Note the mismatch: the scratch collector wrote math.CO/2000, while
src/1_collect_arxiv.py targets math.AT — the committed pilot data comes from the
scratch script, not from src/.

**The poetry pilot is superseded (2026-09-07).** It took the first 100 titles in
PoetryDB's default order and was 71% Robert Burns, so any topological difference
in it confounds form with authorial voice. It is kept only as a record. The
Phase 0 sample is now data/processed/poetry_phase0_sample.parquet: 240 poems,
four arms of 60, 76 authors, no author above 7%.

Form is recovered mechanically, with no hand-labelling, because PoetryDB's
linecount counts only non-blank lines — so the blank lines left in the lines
array are stanza separators and give stanza structure for free. Sonnets are
typed by stanza profile ((4,4,4,2) Shakespearean, (8,6) Petrarchan) and refrains
by exact repeated lines. Note that a 14-line poem printed as one unbroken block
is usually a genuine sonnet, not a false positive: that is the normal printing
convention for sequences (Shakespeare 152, Drayton's *Idea* 29, Donne's Holy
Sonnets 18, Barrett Browning 18).

## Workflow

- **Env:** uv, Python 3.12, in-project .venv/. Run things as uv run python
  src/1_collect_arxiv.py.
- **Authoritative deps:** pyproject.toml + uv.lock. Add with uv add.
- Scripts are run from the **project root** — output paths like data/raw are
  relative to CWD, not to the script.
- Filenames beginning with a digit (1_collect_arxiv.py) are not importable as
  modules; they are scripts only. Shared logic must move to a normal module name
  if steps 3–5 need to import it.
- **Every pipeline stage takes --model {nomic,mpnet}** and writes to a
  model-tagged path (`ph_results_nomic.parquet`, `ph_results_mpnet.parquet`,
  ...), so the primary and robustness runs cannot overwrite each other. Both
  models see byte-identical text: every draw upstream of the embedding is
  seeded. Compare them with `uv run python src/compare_models.py`.
- **arXiv API courtesy:** the collectors already use delay_seconds 3–5 and
  retries. Do not lower these or parallelise the harvest.

## Gotchas

- **There is no requirements.txt, deliberately.** The one that existed pinned
  another project's dependencies and was removed on 2026-10-19.
  pyproject.toml and uv.lock are authoritative.
- **Declared but unused so far:** gudhi, duckdb, umap-learn, persim,
  scikit-learn. Their presence signals intent, not existing code — don't assume
  a UMAP step or a DuckDB store exists.
- **This repository is public (2026-10-19)**, at
  github.com/sungyeon-hong/topoling, so the research trajectory can be traced.
  It was created from an earlier private repository, kept unedited as an
  archive, with its history cleaned: a scratch script carrying an unpublished
  application abstract and a foreign requirements.txt were removed from every
  commit, venue-specific wording was neutralised, and authorship was normalised
  to `sungyeon-hong`. Commit dates and messages are otherwise unchanged.
  CLAUDE.md, CONTRIBUTIONS.md and backlog/ are tracked as the least
  reproducible files here; data/ stays ignored on size grounds.
- **Venue names, submission dates and publication plans never go in this
  repository.** They are kept outside it. Here, write "the
  target venue" or "the conference abstract". `.githooks/pre-commit` refuses a
  commit whose staged changes match a blocklist kept outside the repository; enable it once per clone
  with `git config core.hooksPath .githooks`.
- **PoetryDB wraps long lines.** A long line of Whitman is stored broken across
  entries, leaving indented continuation fragments like " the" and " of". These
  are not lines of verse and they bite twice: they register as repeated refrains
  ("the" appeared as a 6x refrain before this was caught), and since Phase 0
  embeds one line per point, each fragment would become a meaningless point in
  the cloud. poetry_forms.py carries a wrap_fraction column and holds out the
  193 poems wrapped worse than 10%. Fixing this cut the refrain_song class from
  171 to 135, so 36 were pure artefact. Whitman is worst affected at 14.7% -
  relevant if he is ever used as a free-verse arm.
- **Resolved 2026-09-14:** data/ is gitignored in full, because the corpus is
  ~71 MB and fully reproducible from the collectors.

## Don't do this

- Do not feed UMAP/t-SNE output into ripser (see Normalisation).
- Do not report document-level H1 for arXiv abstracts (~8 sentences — noise).
- Do not report document-level H1 for sonnets either. A sonnet is 14 lines and
  the floor is ~25 points, so **no sonnet can clear it** - 0 of 442 do. The
  sonnet arm supports H0 and volta structure only. Decide this per arm rather
  than globally: refrain_song clears the floor in 106 of 135 poems.
- Do not embed PoetryDB lines without filtering wrap fragments (see Gotchas).
- Do not use verbatim repetition as ground truth (learned 2026-09-07). Identical
  lines embed to the same point, ripser drops zero-persistence bars, and the
  refrain contributes nothing but a smaller cloud. Use *near*-duplicates:
  displacing a refrain by 0.02-0.20 in embedding space gives a clean monotone H0
  dose-response at fixed cardinality, saturating by 0.20 (median distance
  between unrelated verse lines is ~0.80). This is good news for Phase 1:
  homogenisation produces near-duplicates, not copies. Replicated under mpnet
  (2026-09-18): same shape, same saturation point, but the effect is five times
  smaller. **Never quote an effect size from one model as the instrument's
  sensitivity** - shape replicates, magnitude does not.
- Do not assume H1 discriminates (confirmed across two models, 2026-09-18). H1
  moves with nothing: not refrain strength, not displacement at matched
  cardinality, not form arm. The two H1 arm results that looked significant flip
  in *opposite* directions between Nomic and mpnet, and a third is just point
  count (rho = +0.92 with distinct-point count). H0 carries the discriminating
  signal. The "homogenisation loops" framing is not supported at document level;
  it stays open for corpus-level arXiv work (task-2).
- **But H1 is not empty.** Real poems have *fewer* loops than a size-matched bag
  of arbitrary verse: median ratio 0.85 (nomic) and 0.86 (mpnet), 75% of poems
  below their controls, both p < 10^-15. **Quote the ratio, not the mean
  excess** -- the -25.2 / -18.5 mean excess in task-1 is dragged by a few long
  poems. H1 carries a **coherence** signal, partly overlapping H0 (rho ~0.6),
  but no form information beyond H0. Settled in task-2.
- Do not use a shuffled-line control with plain Rips. A Rips complex is built
  from a *set* of points and is permutation-invariant, so shuffling changes no
  diagram at all. A sonnet's volta is visible only as clustering, not position.
- OPEN — dead ends Sungyeon has already ruled out: embedding models that were
  wrong for this text, filtrations that produced nothing, framings that got
  pushback. Without these I will re-propose them.
