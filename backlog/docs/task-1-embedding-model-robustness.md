# Does Phase 0 survive a change of embedding model?

Run 2026-09-18, closing task-1. Both models were put through the whole pipeline
from scratch on byte-identical text: `nomic-embed-text-v1.5` (primary) and
`all-mpnet-base-v2` (robustness check). Reproduce with

    uv run python src/3_embed_text.py --model {nomic,mpnet}
    uv run python src/4_build_complexes.py --model {nomic,mpnet}
    uv run python src/5_compute_ph.py --model {nomic,mpnet}
    uv run python src/experiment_refrain_sensitivity.py --model {nomic,mpnet}
    uv run python src/compare_models.py

## The short version

The instrument is measuring the text, not the model. The form arms still
separate, the displacement calibration curve still rises and still saturates
near 0.20, and H1 still fails to discriminate. Three things changed and are
recorded below: the *size* of the displacement effect is model-dependent, some
individual pairwise arm contrasts flip, and Result 1 of
`phase0-first-results.md` was overstated because of a bug in how the synthetic
sweep was paired.

## Why the two models cannot be compared on absolute values

The models place text at quite different scales. The median distance between
two verse lines is 0.80 under Nomic and 1.24 under mpnet — cosine 0.68 against
cosine 0.23. The largest distance observed anywhere is 1.033 under Nomic and
1.553 under mpnet, of a possible 2. mpnet spreads text across much more of the
sphere.

So only *shape* is comparable: the ordering of the arms, the sign and
monotonicity of the displacement response, the presence or absence of an H1
signal, and whether the same individual poems come out extreme under both.

One thing that is *not* a confound: only 10 of 360 poems differ at all in
distinct-point count between the models, and the largest difference is 7 points
out of 2799. The two models see effectively identical clouds.

## Result 1 — the form arms separate under both models

Kruskal–Wallis across the four arms on excess H0 mean bar life:

| model | H | p |
|---|---|---|
| nomic | 21.92 | 6.8 × 10⁻⁵ |
| mpnet | 17.31 | 6.1 × 10⁻⁴ |

Weaker under mpnet, still decisive. Every arm is negative under both models,
meaning a real poem's lines sit closer together than a size-matched bag of
arbitrary verse. That is the instrument detecting coherence, and it replicates.

The headline contrast survives. `refrain_song` against `irregular` — the two
arms closest in size, which is what makes it hard to dismiss as cardinality —
is p < 10⁻⁴ under Nomic and p = 3 × 10⁻⁴ under mpnet. `ballad_stanza` against
`irregular` also holds under both (p = 0.0029, p = 0.0025).

**Individual pairwise contrasts flip, and the arm ordering changes.**

| contrast | nomic | mpnet |
|---|---|---|
| refrain_song vs irregular | p < 10⁻⁴ | p = 0.0003 |
| ballad_stanza vs irregular | p = 0.0029 | p = 0.0025 |
| sonnet vs refrain_song | p = 0.0015 | p = 0.21 |
| sonnet vs irregular | p = 0.17 | p = 0.0026 |

Sonnet and ballad swap ranks between the models. Spearman of the arm ordering
across models is +0.800, which on four arms cannot reach significance (p = 0.2)
and should not be quoted as if it could.

**The practical rule: only the strongest contrast is safe to lean on.** A claim
resting on `sonnet vs refrain_song` would have been a claim about Nomic.

## Result 2 — the displacement curve replicates, at one fifth the size

Mean excess H0 mean bar life by displacement. All rows at ε > 0 have 19
distinct points, so cardinality is fixed and cannot explain the trend. (ε = 0
is verbatim repetition and has only 13 distinct points, so it is not on the
same footing as the rest — see Result 3.)

| ε | 0.02 | 0.05 | 0.10 | 0.20 | 0.40 |
|---|---|---|---|---|---|
| nomic | −0.052 | +0.103 | +0.177 | +0.219 | +0.240 |
| mpnet | −0.219 | −0.055 | +0.013 | +0.038 | +0.047 |

Monotone increasing over ε > 0 under both. Both reach 90% of their climb by
ε = 0.20. The two curves correlate at Spearman ρ = +0.943 (p = 0.005). Every
paired comparison against verbatim is significant at p < 10⁻²² under both.

**This is the finding Phase 0 leant on hardest and it replicates cleanly.**

The caveat is magnitude, and it is not small. At ε = 0.40 the excess is +0.240
under Nomic and +0.047 under mpnet, roughly a fifth; under mpnet the curve does
not cross zero until ε = 0.10. The *shape* of the calibration curve is a
property of the text. The *effect size* is a property of the model.

Phase 1 must not quote a sensitivity figure from one model as though it were
the instrument's sensitivity. If a power calculation is ever done for the
arXiv work, it has to be done per model, and the smaller of the two is the
honest one to plan against.

## Result 3 — refrain strength does nothing, under either model, and the earlier weak trend was a bug

`phase0-first-results.md` Result 1 reported a weak but nominally significant H0
trend across refrain strength: Spearman ρ = +0.22, p = 0.038. **That result does
not survive, and the reason is a defect in the experiment rather than the
model.**

`synthetic.py`'s `build_sweep` documented itself as holding the refrains and
filler fixed across the sweep so that only the amount of repetition changed.
It did not. It drew `rng.choice(donor_lines, size=n_needed, replace=False)`,
and `n_needed` falls from 19 to 13 as refrain strength rises, so every strength
received a *different* random selection of lines from the donor. The sweep was
paired only at the donor-poem level, not at the line level, and the reported
trend was partly a comparison between different sets of lines.

Fixed on 2026-09-18 by drawing a permutation once per donor and taking a prefix,
so the two refrains and the filler are now genuinely identical across all four
strengths. Restated:

| statistic | nomic ρ (p) | mpnet ρ (p) | endpoint r1 vs r4 |
|---|---|---|---|
| excess H0 mean bar life | +0.040 (0.66) | +0.048 (0.60) | ns under both |
| excess H1 count | −0.009 (0.92) | +0.108 (0.24) | ns under both |
| excess H1 total persistence | −0.086 (0.35) | +0.106 (0.25) | ns under both |

Nothing, anywhere, under either model. This *strengthens* rather than
undermines the September conclusion: verbatim repetition is invisible to
persistent homology, full stop, and the apparent residual trend was an artifact.

## Result 4 — the H1 null holds, and the exceptions are textbook model artifacts

Two H1 statistics came out nominally significant across the form arms, and they
flip in *opposite directions* between the models:

| statistic | nomic | mpnet |
|---|---|---|
| h1_total_persistence | p = 0.010 | p = 0.90 |
| h1_max_persistence | p = 0.10 | p = 0.041 |

Neither survives the other model. This is precisely the situation `CLAUDE.md`
wrote the robustness rule for.

A third, `n_h1`, is significant under both (p = 7 × 10⁻¹⁰, p = 1 × 10⁻⁷) — and
it is point count. Raw loop count correlates with distinct-point count at
ρ = +0.923 (nomic) and +0.941 (mpnet). Restricted to a narrow 35–60 point band,
the `refrain_song`/`irregular` difference is p = 0.029 under Nomic and p = 0.34
under mpnet, on 15 poems. There is nothing there.

Refrain strength moves no H1 statistic under either model (Result 3). Across
displacement at fixed cardinality, H1 count moves *down* under both
(ρ = −0.375, ρ = −0.105) — consistent in direction, an order of magnitude apart
in size, and in the opposite direction to anything a "homogenisation loop"
would predict.

**So the September conclusion stands and is not a Nomic quirk: H1 does not
discriminate.**

## Result 5 — the one robust H1 finding, previously understated

> **Correction, 2026-10-19 (task-2):** the mean excess figures below are
> dragged by a few long poems. The typical effect is about 15% fewer loops
> (median ratio to controls 0.85 nomic, 0.86 mpnet). Quote the ratio. See
> `task-2-h1-decision.md`.

Real poems have dramatically *fewer* loops than a size-matched bag of arbitrary
verse: mean excess H1 count −25.2 under Nomic and −18.5 under mpnet, both
p < 10⁻¹⁶.

This is large, consistent, and robust across models, and it is a different
claim from "H1 shows nothing". H1 carries a **coherence** signal — a real poem's
lines are constrained enough that they do not enclose the empty space an
arbitrary collection of verse does — but not a **form-discriminating** one.

task-2 should decide on H1 with this on the table, because "H1 is empty" and
"H1 measures coherence but not form" support different framings.

## Result 6 — the strictest test: per-poem agreement

The arm-level checks above could all agree while every poem inside them
disagreed. Correlating each individual poem's statistic across the two models:

| | statistic | Spearman ρ |
|---|---|---|
| real poems | excess H0 mean bar life | +0.875 |
| synthetic | excess H0 mean bar life | +0.902 |
| real poems | excess H1 count | +0.677 |
| synthetic | excess H1 count | +0.469 |

All on 360 poems measured under both models, all p < 10⁻⁷.

The H0 measurement is substantially a property of the text. H1 is markedly more
model-dependent, which independently supports not building the project's
framing on it.

## A reproducibility bug fixed along the way

`experiment_refrain_sensitivity.py` seeded its displacement noise from Python's
built-in `hash()` of the donor's identifier. Python randomises string hashing
per process, so the sweep drew different displacements on every run.

Within a single session that is untidy. For this task it would have been fatal:
the primary and robustness runs would have used different random draws, and a
difference between the two models could not have been distinguished from a
difference between two draws. Now seeded from `blake2b`, which is stable across
processes and machines.

Reassuringly, re-running Nomic with the corrected seeding reproduced the
September displacement curve to three decimal places, so that result was never
dependent on one lucky draw.

## What this does and does not license

**Established, in the sense task-1 meant.** The form arms separate. The
displacement calibration curve is monotone and saturates near 0.20. H1 does not
discriminate. Real text is more coherent than size-matched arbitrary verse on
both H0 and H1.

**Still single-model, and not established.** Any specific effect size. Any
pairwise arm contrast other than `refrain_song`/`irregular` and
`ballad_stanza`/`irregular`.

**Unblocked by this.** task-2 (whether H1 and the "homogenisation loops"
framing stay), task-4 (real paraphrases in place of the geometric model), and
task-5 (whether to collect real villanelles) all depended on task-1.
