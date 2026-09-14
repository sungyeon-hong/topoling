# Contributions log — topoling

Private working record kept by Sungyeon Hong. Intended to be adaptable into a
CRediT contributor statement, a journal or thesis AI-use disclosure, or an
institutional record.

## Human contributions

**Sungyeon Hong** — sole researcher. Conceptualisation; the research question
on whether AI-mediated writing narrows the structural diversity of knowledge
systems; the decision to use persistent homology as the diagnostic; the
poetry-first design, in which poetry serves as instrument validation and a
high-diversity anchor rather than as a comparison arm; all methodology
decisions.

## AI assistance

Tool: Claude Opus 5 (`claude-opus-5[1m]`) via Claude Code, Anthropic.

### 2026-08-12

Directed by SH, who set the research question and made every methodological
decision.

**Documentation.** Read the existing scripts and pilot data and drafted
`CLAUDE.md`: aims, phasing, status, workflow and known problems. The aims were
reconstructed from a fellowship abstract SH had written and embedded in
`scratch/toy_model.py`, then confirmed by SH.

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

**Repository hygiene** (identified by Claude, decisions taken by SH). The
`CLAUDE.md` note that the project was untracked with zero commits was wrong:
`topoling/` is its own repository with a public remote. Claude further found
that `scratch/toy_model.py` had been committed and pushed with SH's full
fellowship abstract inline, and that this material has therefore been publicly
readable since that commit.

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

### Open items requiring SH

The falsifiable one-sentence claim, the intended output, and the record of
approaches already ruled out remain unfilled in `CLAUDE.md`.

## Draft disclosure statement

To be adapted to the venue's template:

> During the preparation of this work the author used Claude (Anthropic) to
> assist with project documentation and with discussion of methodological
> options. The author made all research and methodological decisions, reviewed
> and edited all content, and takes full responsibility for the content of the
> publication.
