"""Synthetic villanelles: positive controls with ground truth by construction.

PoetryDB contains no villanelles (see CLAUDE.md), so Phase 0 cannot validate
the instrument against real ones. It does not need to. What makes a villanelle
useful as ground truth is not the label but *verbatim line repetition at known
positions*, and that can be built: take the lines of a real poem that has no
refrains of its own, and replant two of them on the villanelle's schedule.

    A1 at lines 1, 6, 12, 18        A2 at lines 3, 9, 15, 19

The advantage over a handful of real villanelles is that the signal can be
swept. `n_repeats` controls how many times each refrain recurs, from 1 (a
19-line poem with every line distinct -- the matched negative control) to 4
(a full villanelle). Running the sweep measures not just whether persistent
homology detects refrain structure but *at what strength it stops*, which is
the number Phase 1 actually needs: the homogenisation signal in abstracts will
be far weaker than a villanelle's.

A note on what this can and cannot test. A Vietoris-Rips complex is built from
a *set* of points, so it is permutation-invariant: shuffling a poem's lines
leaves every diagram identical. Refrain structure is visible because it is a
fact about the point set (duplicate points), but position is not. The
shuffled-line control named in CLAUDE.md is therefore a no-op for plain Rips
and is not implemented here; see topology.py for the controls that do bite.
"""

import numpy as np

# 1-indexed in the literature, 0-indexed here.
VILLANELLE_LENGTH = 19
A1_POSITIONS = [0, 5, 11, 17]
A2_POSITIONS = [2, 8, 14, 18]
MAX_REPEATS = 4


def make_villanelle(donor_lines: list[str], n_repeats: int, rng) -> list[str]:
    """Build a 19-line poem whose two refrains each recur `n_repeats` times.

    `n_repeats=1` places each refrain once, giving 19 distinct lines: the
    matched negative control, identical in length and provenance and differing
    only in the absence of repetition.
    """
    if not 1 <= n_repeats <= MAX_REPEATS:
        raise ValueError(f"n_repeats must be 1..{MAX_REPEATS}, got {n_repeats}")

    a1_slots = A1_POSITIONS[:n_repeats]
    a2_slots = A2_POSITIONS[:n_repeats]
    filler_slots = [i for i in range(VILLANELLE_LENGTH)
                    if i not in a1_slots and i not in a2_slots]

    # 2 refrains + one distinct line per remaining slot.
    n_needed = 2 + len(filler_slots)
    if len(donor_lines) < n_needed:
        raise ValueError(f"donor has {len(donor_lines)} lines, needs {n_needed}")

    chosen = list(rng.choice(donor_lines, size=n_needed, replace=False))
    a1, a2, *filler = chosen

    poem = [None] * VILLANELLE_LENGTH
    for i in a1_slots:
        poem[i] = a1
    for i in a2_slots:
        poem[i] = a2
    for slot, line in zip(filler_slots, filler):
        poem[slot] = line
    return poem


def build_sweep(donor_poems: list[list[str]], seed: int = 0) -> list[dict]:
    """One synthetic poem per (donor, refrain strength) pair.

    Holding the donor fixed across the sweep means the only thing that changes
    between n_repeats=1 and n_repeats=4 is the amount of verbatim repetition,
    so any change in the diagrams is attributable to that alone.
    """
    rng = np.random.default_rng(seed)
    records = []
    for donor_idx, donor in enumerate(donor_poems):
        # Same draw for every strength: the refrains and filler are identical,
        # only the number of repetitions differs.
        donor_rng = np.random.default_rng(seed + donor_idx)
        for n_repeats in range(1, MAX_REPEATS + 1):
            lines = make_villanelle(donor, n_repeats,
                                    np.random.default_rng(donor_rng.integers(1 << 30)))
            records.append({
                "poem_id": f"synth_{donor_idx:03d}_r{n_repeats}",
                "title": f"synthetic villanelle (donor {donor_idx}, {n_repeats} repeats)",
                "author": "SYNTHETIC",
                "form": f"synthetic_r{n_repeats}",
                "form_family": f"synthetic_r{n_repeats}",
                "n_repeats": n_repeats,
                "donor_idx": donor_idx,
                "linecount": VILLANELLE_LENGTH,
                "n_distinct_lines": len(set(lines)),
                "lines": lines,
            })
    return records
