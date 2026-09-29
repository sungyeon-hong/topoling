# Phase 0, first results

Run 2026-09-07. Single embedding model (`nomic-embed-text-v1.5`).

> **Superseded in part, 2026-09-18.** task-1 has been done: see
> `task-1-embedding-model-robustness.md`, which is now the authoritative
> account. Most of what follows replicated under `all-mpnet-base-v2`, but
> **Result 1 below did not and has been struck through** — it rested on a bug
> in how the synthetic sweep was paired. Result 3's numbers reproduced exactly.
> Read this document for the reasoning and the other for what is established.

## The short version

The instrument works, but the ground truth Phase 0 was designed around does not.
Verbatim repetition — the villanelle's defining feature — is invisible to
persistent homology for a mechanical reason. Near-duplicate lines, which is what
homogenisation actually produces, are visible, and produce a clean calibration
curve. H1 showed nothing anywhere; H0 carried the entire signal.

## Why verbatim repetition is invisible

Two lines repeated word for word embed to the same point: measured cosine
similarity between identical strings is exactly 1.0000. Coincident points
produce zero-length H0 bars, and ripser silently discards them — a cloud of 13
points containing 3 exact copies yields a 10-bar H0 diagram, not 13.

So a repeated refrain contributes nothing to the topology except to make the
cloud smaller. A 19-line villanelle whose two refrains each recur four times is,
to Vietoris–Rips, a cloud of 13 points. The synthetic sweep confirms this
directly: refrain strength 1, 2, 3, 4 gives 19, 17, 15, 13 distinct points.

This matters beyond villanelles, because **cardinality is a known confound** —
`CLAUDE.md` already warns that persistence statistics move with point count for
trivial reasons. An analysis that compared a villanelle against a 19-distinct-line
control would be measuring point count and calling it form.

Every comparison below is therefore made against corpus controls matched on
*distinct* point count: real verse lines drawn from other poems, carrying the
embedding model's geometry but none of the poem's coherence. The reported
quantity is the poem's statistic minus the mean of 20 such controls.

## Result 1 — WITHDRAWN 2026-09-18: refrain strength does nothing at all

**The table below is wrong and is kept only as a record.** It claimed the
sweep was "paired by donor so only the amount of repetition changes". It was
not. `synthetic.py` drew `rng.choice(donor_lines, size=n_needed)`, and
`n_needed` falls from 19 to 13 as refrain strength rises, so each strength
received a different random selection of the donor's lines. The sweep was
paired at the donor-poem level only, and the weak H0 trend was partly a
comparison between different sets of lines.

~~Synthetic villanelles, 30 donor poems, refrains planted on the standard~~
~~schedule (lines 1/6/12/18 and 3/9/15/19), paired by donor so only the amount~~
~~of repetition changes:~~

| ~~statistic~~ | ~~Spearman rho across strengths~~ | ~~endpoint test~~ |
|---|---|---|
| ~~excess H0 mean bar life~~ | ~~+0.22 (p = 0.038)~~ | ~~p = 0.14, ns~~ |
| ~~excess H1 count~~ | ~~+0.13 (p = 0.219)~~ | ~~p = 0.11, ns~~ |
| ~~excess H1 total persistence~~ | ~~+0.06 (p = 0.580)~~ | ~~p = 0.48, ns~~ |

Corrected, with the sweep genuinely paired (same refrains, same filler, only
the repetition count differing), under both embedding models:

| statistic | nomic rho (p) | mpnet rho (p) |
|---|---|---|
| excess H0 mean bar life | +0.040 (0.66) | +0.048 (0.60) |
| excess H1 count | −0.009 (0.92) | +0.108 (0.24) |
| excess H1 total persistence | −0.086 (0.35) | +0.106 (0.25) |

Nothing anywhere, under either model. This **strengthens** the section above
rather than weakening it: verbatim repetition is invisible to persistent
homology, full stop, and the residual trend was an artifact.

## Result 2 — displaced refrains give a clean dose-response

Modelling a paraphrase as a small displacement of the refrain in embedding
space, renormalised to the sphere. All rows below have 19 distinct points, so
cardinality is held fixed and cannot explain the trend:

| displacement | 0.02 | 0.05 | 0.10 | 0.20 | 0.40 |
|---|---|---|---|---|---|
| excess H0 mean bar life | −0.052 | +0.102 | +0.176 | +0.219 | +0.239 |
| excess H1 count | −4.54 | −5.40 | −5.44 | −5.35 | −4.52 |

H0 is monotone, every paired comparison against verbatim significant at
p < 10⁻⁴, saturating around 0.20. For scale, the median distance between two
unrelated verse lines is about 0.80, and all observed pairwise distances fell in
[0, 1.03] of a possible [0, 2] — real text occupies a narrow cone, not the
whole sphere.

H1 is flat across the entire range. It does not discriminate.

**This is the useful finding, and it replicated under mpnet (task-1):**
monotone, saturating by 0.20, curves correlating at rho = +0.943 — though the
effect is five times smaller under mpnet, so the *size* is model-dependent even
though the shape is not. It is a calibration curve: it says how close two
lines must be before the instrument resolves them as related. And it points the
right way for Phase 1, because a corpus converging on the semantic mean produces
near-duplicates rather than copies — so the effect of interest should be *more*
visible than a villanelle, not less.

The caveat is in task-4: a random displacement is a geometric model of
paraphrase, not a linguistic one.

## Result 3 — the real form arms do separate, on H0

240 poems, 60 per arm, on excess H0 mean bar life:

| arm | n | median distinct points | mean excess |
|---|---|---|---|
| refrain_song | 60 | 43.5 | −0.0900 |
| ballad_stanza | 60 | 20.0 | −0.0766 |
| sonnet | 60 | 14.0 | −0.0595 |
| irregular | 60 | 48.5 | −0.0579 |

Kruskal–Wallis across the four arms: H = 21.92, p = 6.8 × 10⁻⁵. Re-running
this on 2026-09-18 reproduced every figure in the table exactly, and mpnet gives
H = 17.31, p = 6.1 × 10⁻⁴ (task-1).

Pairwise (uncorrected): refrain_song vs irregular p < 10⁻⁴; refrain_song vs
sonnet p = 0.0015; ballad vs irregular p = 0.0029. The rest are not significant.

**task-1 caveat:** of these, only refrain_song vs irregular and ballad vs
irregular survive under mpnet. refrain_song vs sonnet does not (p = 0.21), and
sonnet vs irregular becomes significant under mpnet having been null here. Do
not lean on any contrast but the first two.

Every arm's excess is negative, meaning a real poem's lines sit closer together
than a size-matched bag of arbitrary verse. That is the instrument detecting
coherence, and it is a sanity check that the pipeline is wired correctly.

The strongest contrast — refrain_song against irregular — holds between the two
arms *closest in size* (43.5 vs 48.5 distinct points). That argues the
separation is not cardinality in disguise, which is the obvious objection.

## Result 4 — plain Rips cannot see order

A Vietoris–Rips complex is built from a *set* of points, so it is
permutation-invariant: shuffling a poem's lines leaves every diagram identical.

Two consequences, both of which contradict assumptions in `CLAUDE.md`:

- The shuffled-sentence control listed there as nuisance calibration is a no-op.
  It cannot detect anything, and it was not implemented.
- A sonnet's volta is a claim about *position* (near line 8–9). Plain Rips can
  only see whether the octave and sestet form two clusters, never where the
  break falls. Positional structure needs sliding-window persistence, which is a
  different construction — see task-2.

## Cross-project corroboration

`panic-tda`'s TASK-77, a keep/kill pilot on whether topological data analysis
earns a place in that paper, reaches the same conclusion from unrelated data:
Rips persistent homology on 25–100 points is unreliable beyond H0, H0 duplicates
hierarchical clustering, and persistence entropy is confounded by bar count from
duplicate captions. Two projects hitting the same wall independently is evidence
about the method rather than about either dataset.

## What to do next

**Done 2026-09-18:** task-1, the robustness check. See
`task-1-embedding-model-robustness.md`. It also surfaced one H1 finding this
document missed: real poems have far *fewer* loops than size-matched arbitrary
verse, robustly under both models. H1 carries a coherence signal even though it
carries no form-discriminating one, which is a different claim from "H1 shows
nothing" and task-2 should weigh it.

Next is task-2: whether H1 and the "homogenisation loops" framing survive.
