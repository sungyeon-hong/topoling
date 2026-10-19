# Does H1 stay? The task-2 decision

Decided 2026-10-19 by Sungyeon, closing task-2. The evidence is in
`task-1-embedding-model-robustness.md` plus one further check run the same day,
recorded below.

## The decision

**Poetry (Phase 0, document level) makes no homogenisation claim.** The
question poetry is brought in to answer is whether novel or unusual expression
shows identifiable patterns under topological analysis. H0 (connectivity: how
clustered or spread a poem's lines are) is the headline measurement. H1 (loops)
is reported as a supporting coherence measure, not a form-discriminating one.

**"Homogenisation loops" stays as an open question for Phase 1 (arXiv, corpus
level).** It is not retired. Every H1 result so far is document-level, on clouds
of 14-50 points; corpus-level clouds (one abstract = one point, ~300 points per
subsample) are a different object and have not been measured. A prediction for
corpus-level H1 should be written down before task-6 or task-7 produces
numbers, so the test is not fitted after the fact.

**Sliding-window persistence is future work.** It is the only construction
that sees line order (a sonnet's volta is a positional claim, and plain Rips is
permutation-invariant), but it is a new instrument needing its own validation,
which does not fit the conference timeline.

## Sungyeon's rationale, in their words

> It is deemed fair enough for poems not to exhibit loop structures (H1) - too
> short and so may have lean structures than usual texts. More importantly, it
> is not even necessary to consider homogenisation in the context of the shape
> of poetry. So I'd drop the homogenisation claim when dealing with poetry
> data. The main motivation of bringing in poetry is to see if novel/unusual
> expressions can show identifiable patterns via topological analysis.

How the two halves of "short and lean" map onto the evidence:

- **Lean structure** is what the data shows directly. Compared against bags of
  unrelated verse lines with the *same* number of distinct points — so length
  is controlled — real poems still have about 15% fewer loops (table below).
  Coherent verse encloses less empty space than chance.
- **Too short** applies to sonnets specifically: at 14 lines, none clears the
  ~25-point floor below which H1 is not read at all (0 of 442).

## The check run on 2026-10-19

Question: is H1's coherence signal real information, or H0 seen twice? Run over
the 240 real Phase 0 poems in `data/processed/ph_results_{nomic,mpnet}.parquet`.

| | nomic | mpnet |
|---|---|---|
| median loop count / size-matched control mean | 0.85 | 0.86 |
| share of poems with fewer loops than their controls | 75% | 75% |
| Wilcoxon on log ratio | p = 5 × 10⁻¹⁷ | p = 1 × 10⁻¹⁵ |
| Spearman, standardised excess H1 count vs excess H0 mean bar life | +0.62 | +0.56 |
| loop ratio vs distinct-point count | +0.02 (ns) | +0.13 (p = 0.04) |
| Kruskal-Wallis across arms, H1 residual after H0 | p = 0.25 | p = 0.30 |

Read as:

- **The coherence signal is real and replicates, but it is modest.** About 15%
  fewer loops, not "25 fewer". The mean excess of −25.2 (nomic) / −18.5 (mpnet)
  quoted in task-1's Result 5 is dragged by a few long poems; per-arm medians
  run from −0.5 to −9.6. **Quote the ratio, not the mean excess.**
- **It overlaps H0 without duplicating it** — correlated, but sharing well
  under half its variance.
- **It carries no form information beyond H0** under either model.

## A framing risk to carry into task-3

H0 persistence of a Rips complex is single-linkage clustering: its bars are the
edge lengths of the minimum spanning tree. A reviewer can fairly ask why an
H0-led result is topology rather than nearest-neighbour spacing. The answer
available now is the calibrated multiscale instrument (the displacement curve)
plus H1 as a second, partly independent coherence measure. The one-sentence
claim should be worded with this objection in mind.

## Earlier project material

The project abstract that `CLAUDE.md`'s Aim was reconstructed from addressed arXiv corpus analysis, not poetry, so its
reference to homogenisation loops remains consistent with this decision: loops
are still an open question at exactly that level. No rewording needed.
