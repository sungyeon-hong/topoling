# Contributions log — topoling

A dated record of who contributed what to this project, kept as the work
happened. Sungyeon Hong is the sole researcher. AI assistance is logged per
session, keeping what Claude proposed or did separate from what Sungyeon
decided. Intended to be adaptable into a CRediT contributor statement, a
journal or AI-use disclosure, or an institutional record.

## Human contributions

**Sungyeon Hong** — sole researcher. Conceptualisation; the research question
on whether AI-mediated writing narrows the structural diversity of knowledge
systems; the decision to use persistent homology as the diagnostic; the
poetry-first design; the hypothesis that poetry, through metaphor and novel
links between distant notions, spreads more widely in semantic space than
ordinary writing, and the falsifiable claim that tests it; the decision to
drop the homogenisation claim for poetry while keeping it open for arXiv; all
methodology decisions.

## AI assistance

Tool: Claude via Claude Code, Anthropic. Model per session: Claude Opus 5
(`claude-opus-5[1m]`) from 2026-08-12 to 2026-10-09; Claude Opus 5.5
(`claude-opus-5-5`) from 2026-10-19.

### 2026-08-12

Directed by SH, who set the research question and made every methodological
decision.

**Documentation.** Read the existing scripts and pilot data and drafted
`CLAUDE.md`: aims, phasing, status, workflow and known problems. The aims were
reconstructed from an earlier project abstract SH had written, then confirmed
by SH.

**Methodology input** (proposed by Claude, decided by SH):

- Recommended against SPECTER2 for sentence-level embedding as off-label use,
  proposing `nomic-embed-text-v1.5` with `all-mpnet-base-v2` as a robustness
  check, partly for consistency with the `panic-tda` project.
- Recommended L2 normalisation onto the unit sphere so Euclidean distance
  becomes monotone in cosine similarity and persistence diagrams are comparable
  across corpora, together with fixed-cardinality subsampling and bootstrap
  replicates.
- Advised against dimensionality reduction by UMAP or t-SNE before persistent
  homology, as neither preserves distances.
- Identified a constraint on document-level analysis: an arXiv abstract of
  roughly eight sentences cannot support interpretable H1 features, so
  document-level work is effectively poetry-only unless full texts are used.
- Distinguished nuisance calibration from the scientific baseline after SH
  clarified that structural openness concerns a shift in style rather than
  randomness.
- Observed that fixed poetic forms provide ground truth for instrument
  validation, since a villanelle's repeated refrains predict a specific
  topological signature.

**Not done.** No analysis has been run, no code written, and no results
produced. The pipeline remains unimplemented at steps 3 to 5.

### 2026-09-07

Directed by SH, who chose the session's objective (build the Phase 0 poetry
corpus) from options presented, and who retains every methodological decision.

**Code.** Wrote `src/collect_poetrydb_corpus.py`, which collects the full
PoetryDB corpus (3092 poems, 129 authors) one request per author rather than
one per title, falling back to per-title retrieval for authors whose bulk
payload the server refuses, and caching per author so a rerun is free. Wrote
`src/poetry_forms.py`, which recovers poetic form mechanically — from line
count, stanza profile and exactly repeated lines — and draws a form-stratified
sample capped at five poems per author.

**Findings** (established by Claude from the collected data, reported to SH):

- PoetryDB contains no villanelles. Of 3092 poems, 22 have the villanelle's 19
  lines and none carries two recurring refrains. The form became common in
  English only in the twentieth century, and PoetryDB also omits the
  public-domain 1890s revival villanelles. The Phase 0 design in `CLAUDE.md`
  named a villanelle arm; that arm cannot be built from this source.
- Proposed `refrain_song` — songs and hymns whose chorus recurs verbatim — as
  the substitute, on the grounds that what makes a villanelle useful as ground
  truth is verbatim line repetition rather than the form's name, and that these
  poems are long enough to clear the H1 point floor that a 19-line villanelle
  cannot.
- Modern free verse is unavailable from any public-domain source, so that arm
  is constrained by copyright rather than by corpus choice.
- No sonnet can support document-level H1: a sonnet is 14 lines against a
  ~25-point floor, and 0 of 442 clear it. The H1 decision must be made per arm.
- PoetryDB stores long lines wrapped, leaving indented continuation fragments
  that are not lines of verse. These registered as repeated refrains and would
  have entered the line-level point cloud as meaningless points. Adding a
  content floor for refrains and a wrap-fraction hold-out cut the refrain_song
  class from 171 to 135, so 36 had been artefact.
- The earlier 100-poem pilot was 71% Robert Burns, confounding form with
  authorial voice. The replacement sample is 240 poems across 76 authors with
  no author above 7%.

**Repository hygiene** (identified by Claude, decisions taken by SH). Corrected
a `CLAUDE.md` note claiming the project was untracked with zero commits; it was
already its own git repository.

**Pipeline implemented and first Phase 0 test run.** Wrote `src/embedding.py`
(nomic-embed-text-v1.5, task-prefixed, L2-normalised to the unit sphere),
`src/synthetic.py` (synthetic villanelles with refrains planted on the
1/6/12/18 and 3/9/15/19 schedule, with refrain strength as a swept parameter),
`src/topology.py` (Rips persistent homology with controls matched on point
count), the three numbered pipeline steps 3 to 5, and
`src/experiment_refrain_sensitivity.py`.

**Results** (obtained by Claude, interpretation to be reviewed by SH). These
are first results and have not been checked against the second embedding model,
so nothing here is settled:

- Verbatim repetition is invisible to this instrument, for a mechanical reason.
  Identical lines give identical embeddings, the points coincide, and ripser
  discards the zero-persistence bars they would produce. A four-fold-refrain
  villanelle is, to Vietoris-Rips, simply a cloud of 13 points rather than 19.
  Matched on distinct point count, refrain strength moved almost nothing.
- The ground truth was therefore wrong, not the instrument. Displacing each
  refrain slightly in embedding space -- a geometric model of paraphrase --
  produces a clean monotone dose-response at fixed cardinality: mean excess H0
  bar life runs -0.052, +0.102, +0.176, +0.219, +0.239 across displacements of
  0.02 to 0.40, saturating around 0.20. This is the calibration curve Phase 1
  needs, and it suggests homogenisation, which yields near-duplicates rather
  than copies, should be *more* visible than a villanelle, not less.
- H1 showed no signal in any condition: not across refrain strength, not across
  displacement at matched cardinality, and not between the real form arms. On
  present evidence the "homogenisation loops" framing is not supported, and H0
  is carrying everything.
- The four real form arms do separate on excess H0 bar life (Kruskal-Wallis
  p = 6.8e-05). The strongest contrast, refrain_song against irregular
  (p < 1e-4), holds between the two arms closest in size, which argues the
  separation is not merely cardinality.
- A Vietoris-Rips complex is built from a set of points and is therefore
  permutation-invariant. The shuffled-line control named in `CLAUDE.md` cannot
  detect anything for this construction, and a sonnet's volta is visible only
  as clustering, never as position.

**Not done.** The robustness check against all-mpnet-base-v2 has not been run,
so no finding above should be believed yet. No persistence images, no
corpus-level analysis, and nothing on arXiv.

### 2026-09-14 to 2026-10-09 (reconstructed afterwards from the record)

These entries were written on 2026-10-19 from the commit messages and backlog
documents, not at the time. They record what was done; who proposed what is
stated only where the record shows it.

- **2026-09-14.** Claude set up `backlog/` (numbered tasks with a status,
  findings documents, a glossary of the topological vocabulary) so a session's
  findings survive it, and logged task-1, the robustness check.
- **2026-09-18.** Claude corrected stale status notes in `CLAUDE.md`, then ran
  task-1: the whole pipeline under a second embedding model
  (`all-mpnet-base-v2`) on byte-identical text. Found and fixed two defects
  that would have invalidated the comparison: a seed taken from Python's
  per-process `hash()`, and a refrain-strength sweep that was not paired the
  way its documentation claimed. The latter withdrew one earlier result. Wrote
  `src/compare_models.py` and the findings document.
- **2026-09-30.** Committed the above. SH named the short-term output (a
  conference abstract); Claude added task-6 (corpus-level analysis) and task-7
  (an arXiv pilot) to build the unit of analysis that output would need.
- **2026-10-09.** Housekeeping only: planning notes moved outside the
  repository.

### 2026-10-19

Directed by SH. Session on two decisions, task-2 and task-3, plus moving the
project to a public repository.

**Decided by SH:**

- **task-2.** Poetry makes no homogenisation claim; "homogenisation loops"
  stays an open question for corpus-level arXiv analysis. SH's rationale:
  poems need not exhibit loop structure, being short and leaner in structure
  than usual texts, and homogenisation is not needed to study the shape of
  poetry.
- **The novelty hypothesis (SH's).** A poem is written differently from an
  ordinary description, with more metaphors and novel links connecting
  seemingly distant notions, so poetry should show a wider spread of semantic
  features than usual texts, especially in H0.
- **task-3, the falsifiable claim.** Wording developed together from SH's
  hypothesis and agreed by SH: compared with prose by the same authors at
  matched segment length, a poem's lines spread more widely yet stay linked,
  giving longer H0 bars than prose but shorter than an unordered bag of lines.
- **Raised by SH:** whether discourse analysis, focused on narrative flow,
  suits the study for both poetry and arXiv. Agreed as one order-aware
  supporting measure now, fuller analysis later.
- To make the repository public under `sungyeon-hong`, with venue and
  publication plans kept private, and the licences below.

**Proposed or done by Claude, accepted by SH:**

- Checked whether H1's coherence signal is independent of H0 (partly: they
  correlate at about 0.6) and found the quoted effect size overstated: the
  typical effect is about 15% fewer loops, not a mean of 25.
- Made the H0 reading precise: wider spread means longer H0 bars, not larger
  components.
- Read the claim as two halves, spread and bridging, and identified the
  existing coherence result as support for the bridging half.
- Identified the unit mismatch between poem lines and prose sentences as the
  main confound, and proposed same-author prose as the comparison corpus
  (task-8) and consecutive-line distance as the order-aware measure.
- Reformatted `CLAUDE.md`; cleaned the repository history for public release;
  added the venue-check hooks, licences and citation file.

### Open items requiring SH

The record of approaches already ruled out is still unfilled in `CLAUDE.md`
(task-3, item 3). The longer-horizon output is open.

## Draft disclosure statement

To be adapted to the venue's template:

> During the preparation of this work the author used Claude (Anthropic) to
> assist with project documentation, with discussion of methodological options,
> and with writing and running analysis code. The author made all research and
> methodological decisions, reviewed and edited all content, and takes full
> responsibility for the content of the publication.
