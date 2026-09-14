# The PoetryDB corpus: what is in it, and what is not

Collected 2026-09-07 by `src/collect_poetrydb_corpus.py`. 3,092 poems by 129
authors. The data itself is gitignored and reproducible; this file records what
was learned about it, which is not.

## How it was collected

PoetryDB exposes ~3,010 titles. Fetching per author costs 129 requests rather
than one per title, so that is what the collector does. Two wrinkles:

- **Prolific authors break the bulk endpoint.** Byron (324 poems) and Shelley
  (312) return HTTP 503 on the whole-author payload. The collector falls back to
  one request per title for those, which is slow but works.
- **The author endpoint matches substrings**, so some poems arrive under more
  than one query. 640 duplicates were dropped on a stable id built from author
  and title.

Responses are cached per author under `data/interim/`, so a rerun after a
failure re-fetches only what is missing.

## Form is recoverable without hand-labelling

PoetryDB has no form labels, but it does not need them. Its `linecount` field
counts only *non-blank* lines, which means the blank lines left in the `lines`
array are stanza separators — 87% of poems have them. Stanza structure is
therefore free, and form follows from line count, stanza profile, and exactly
repeated lines. This is what `src/poetry_forms.py` does.

Sonnets type cleanly by stanza profile: (4,4,4,2) is Shakespearean, (8,6) is
Petrarchan.

**A 14-line poem printed as one unbroken block is usually a real sonnet, not a
false positive.** That is the normal printing convention for sonnet sequences,
and the 386 such poems are dominated by Shakespeare (152, the complete
sequence), Drayton's *Idea* (29), Donne's Holy Sonnets (18) and Barrett
Browning's *Sonnets from the Portuguese* (18). The line-count proxy does
misfire occasionally — Dickinson's "'Twould ease -- a Butterfly --" is 14 lines
in a (4,4,3,3) layout and is not a sonnet — but the bulk are genuine.

## There are no villanelles

Of 3,092 poems, 22 have the villanelle's 19 lines and **none** carries two
recurring refrains. This is not a detection failure. The villanelle became a
common English form only in the twentieth century, and PoetryDB holds
public-domain material predating that. Dylan Thomas returns HTTP 404.

It also omits the 1890s revival villanelles that *are* public domain: it holds
1 Dowson poem, 6 Henley, 10 Wilde, and its "Robinson" is Mary Robinson
(1757–1800), not E. A. Robinson. See task-5.

Free verse is thin for the same reason — modern free verse is in copyright, so
Whitman and Crane are the ceiling for any public-domain source.

The four Phase 0 arms are therefore **sonnet / refrain_song / ballad_stanza /
irregular**. `refrain_song` — songs and hymns whose chorus recurs verbatim —
replaces the villanelle arm, and being far longer it clears the point floor a
19-line villanelle never could.

## Long lines are stored wrapped, and this is a trap

PoetryDB breaks long lines across multiple entries, leaving indented
continuation fragments. A line of Whitman trails off into entries like `"  the"`
and `"    of"`. These are not lines of verse, and they bite twice:

1. They register as repeated refrains. `"the"` was detected as a 6× refrain
   before this was caught.
2. Because Phase 0 embeds one line per point, each fragment becomes a
   meaningless point in the cloud.

383 of 3,092 poems are affected, 193 worse than 10%, 68 worse than 25%. Whitman
is worst at 14.7% — which matters, since he is the closest thing this corpus has
to a free-verse arm.

`poetry_forms.py` now carries a `wrap_fraction` column, requires a refrain to
have at least three words, and holds out poems wrapped worse than 10%. Applying
this cut the `refrain_song` class from 171 to 135, meaning 36 had been pure
artefact.

## The original pilot was unusable

The first 100-poem pilot took PoetryDB's default title order and came out **71%
Robert Burns**. Any topological difference measured in it would confound form
with authorial voice. It is kept only for provenance.

The replacement sample (`data/processed/poetry_phase0_sample.parquet`) is 240
poems, 60 per arm, 76 authors, with no author above 7%.

## Author counts worth knowing

Byron 303, Edward Thomas 132, Burns 99, Shakespeare 152 sonnets, Whitman 67.
A per-author cap is not optional when sampling from this source.
