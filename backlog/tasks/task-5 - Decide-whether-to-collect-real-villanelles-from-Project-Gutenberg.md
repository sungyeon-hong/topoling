---
id: task-5
title: Decide whether to collect real villanelles from Project Gutenberg
status: To Do
priority: low
created: 2026-09-14
updated: 2026-09-14
labels: [corpus, phase-0, decision]
depends_on: [task-1]
---

## What this is

Decide whether it is worth building a villanelle corpus from Project Gutenberg,
now that the reason for wanting one has changed.

## Why the case has weakened

The original motive was ground truth: a villanelle repeats two refrains
verbatim, so it should produce a predictable signature. The 2026-09-07 session
established that verbatim repetition is precisely what this instrument cannot
see. Identical lines give identical embeddings, the points coincide, and ripser
discards the zero-persistence bars they would produce, so a four-fold-refrain
villanelle is just a smaller cloud. Collecting real villanelles would buy more
examples of the one construction already known to be invisible.

## Why it has not vanished entirely

Real villanelles are not perfectly verbatim. Poets vary refrains — a word
changed, punctuation shifted, a line inverted — and those near-repetitions are
exactly the regime where the instrument *does* respond. A corpus of real
villanelles would supply naturally occurring near-duplicates at whatever
displacement poets actually use, which overlaps heavily with task-4 and might
be a better way to do it than generating paraphrases.

## What is actually available

Villanelles are obtainable in the public domain: the form had an English
revival in the 1890s (Ernest Dowson, W. E. Henley, Oscar Wilde, Edmund Gosse,
Andrew Lang, and E. A. Robinson's "The House on the Hill", 1894). PoetryDB
simply does not carry them — it holds 1 Dowson poem, 6 Henley, 10 Wilde, and
its "Robinson" is Mary Robinson (1757-1800), not E. A. Robinson. Project
Gutenberg has the source volumes.

The cost is that Gutenberg supplies plain-text *books*, not poem records, so
this needs a poem-boundary parser, for a yield of perhaps 20-50 villanelles.

Modern free verse remains unavailable from any public-domain source, because it
is in copyright. No corpus choice fixes that.

## What counts as finished

- [ ] A decision recorded here: collect, fold into task-4, or drop.
- [ ] If dropped, `CLAUDE.md`'s Phase 0 section updated to stop implying a
      villanelle arm is still wanted.
