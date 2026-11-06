# Where the same-author prose comes from

Inspected 2026-11-06, before any prose was downloaded. This document records
which PoetryDB poets have non-fiction prose on Project Gutenberg, and the
selection decisions Sungyeon made from that inventory. The selection rule
itself (eligibility, cap, sampling) is in `task-8-segmentation-rule.md`,
alongside the cutting rule.

## What the comparison is for

A reminder, so this inventory can be read on its own. task-3's claim
(Sungyeon, 2026-10-19) is that, compared with prose by the same author cut into
segments of the same length, a poem's lines **spread more widely** across
semantic space yet **stay linked**. The poem should have longer H0 bars than
the matched prose, but shorter than an unordered bag of lines from other poems.

- The first half needs this prose corpus.
- The second half uses the existing control, the bag of lines from other poems.
- The claim is judged across three embedding models by a rule fixed in advance
  (`CLAUDE.md`).

**Same-author** prose holds voice, vocabulary and period constant, so the only
thing that changes is the mode of writing. That is why prose is collected poet
by poet, and why which poets have prose decides who is in the comparison.

## Decisions taken from this inventory

Sungyeon, 2026-11-06:

1. **Poets, not arms.** The poetry forms used in Phase 0 (sonnet, refrain_song,
   ballad_stanza, irregular) are not a control parameter here; the pairing of
   each poem with its own author's prose is the control. Poems are therefore
   drawn per poet from the **whole PoetryDB corpus**, not from the 240-poem
   Phase 0 sample. Form is kept as a reported covariate (recorded and described,
   not used to include or exclude poems).
2. **No fiction, no drama.** Prose is letters and essays only, in two groups:
   *personal* (letters, journals, travel, memoir) and *argued* (essays,
   criticism, prefaces, treatises).
3. **Cap of 10 poems per poet**, drawn at random from a fixed seed. Results are
   reported per poet, with a leave-one-poet-out check (rerun dropping each poet
   in turn) so that no single voice carries the outcome.
4. **First pass on the 12 strong poets below.** The poets on the catch list are
   left out for now.
5. **Dickinson left out for now.** Her letters are not on Gutenberg; add her
   later from another source as a robustness check.
6. **Edward Thomas in, and also reported separately.** His prose is lyrical
   nature writing, closer to poetry than any letter, so he is a stringent test
   rather than ordinary prose.

Carried over from the same session's discussion of the cutting rule, to be
written into `task-8-segmentation-rule.md`:

- Poems with at least 8 sentences enter comparison B **whatever their form**,
  sonnets included.
- Comparison A is run **twice**: on all poems, and on exactly B's poems. That
  makes A against B a like-for-like comparison, in which only the cutting rule
  differs.

## How the inventory was made

- **Source:** Gutenberg's own catalogue file,
  `https://www.gutenberg.org/cache/epub/feeds/pg_catalog.csv`, downloaded
  2026-11-06. It is the file Gutendex is built from, and the Gutendex API itself
  took about 77 seconds per request.
- **Candidates:** every PoetryDB poet with **at least 20 poems** (32 poets).
- **Matching:** each poet was matched by name. English-language texts only.
- **Re-derive with** `scratch/gutenberg_catalogue_probe.py`. Its tags are only
  keyword hints; every title below was judged by hand.
- **"Usable poems"** are poems in PoetryDB that pass the existing filter for
  broken lines (`wrap_fraction ≤ 0.10`) and have at least 4 distinct lines.

## Strong candidates: the first pass

Gutenberg ebook numbers are in brackets.

| poet | usable poems | personal | argued |
|-|-|-|-|
| Shelley | 275 | *History of a Six Weeks' Tour* [52790] ⚠ | *A Defence of Poetry and Other Essays* [5428]; *Prose Works* 1–2 [67925, 67926]; *A Vindication of Natural Diet* [38727] |
| Byron | 268 | *Letters and Journals* 1–2 [8901, 9921] | — |
| Edward Thomas | 113 | — | *The South Country* [60760]; *In Pursuit of Spring* [58395]; *The Icknield Way* [57097]; *Beautiful Wales* [52539]; *Oxford* [55918]; *Windsor Castle* [41345]; *George Borrow* [18588] |
| Burns | 61 | *The Letters of Robert Burns* [9863] | — |
| Robert Browning | 51 | Browning–Barrett letters 1–2 [16182, 73891] | — |
| Stevenson | 43 | *Letters* 1–2 [622, 637]; *Vailima Letters* [387]; *An Inland Voyage* [534]; *Travels with a Donkey* [535]; *The Silverado Squatters* [516]; *In the South Seas* [464] | *Virginibus Puerisque* [386]; *Memories and Portraits* [381]; *Familiar Studies of Men and Books* [425]; *Essays in the Art of Writing* [492]; *Across the Plains* [614]; *Lay Morals* [373] |
| Swinburne | 41 | — | *A Study of Shakespeare* [16412]; *The Age of Shakespeare* [14252]; *William Blake* [35995]; *Victor Hugo* [60466] |
| E. B. Browning | 33 | *Letters* 1–2 [13018, 16646]; Browning–Barrett letters [16182, 73891] | — |
| Poe | 33 | — | *The Raven, and The Philosophy of Composition* [55749]; criticism in *Works* vol. 5 [2151] |
| Whitman | 27 | *Specimen Days*, in *Complete Prose Works* [8813]; *The Wound Dresser* [35725] | *Democratic Vistas*, in [8813] |
| Coleridge | 23 | *Letters* 1–2 [44553, 44554] | *Biographia Literaria* [6081]; *Literary Remains* 1–4 [8488, 8533, 8956, 10801]; *Aids to Reflection* [44795] |
| Keats | 22 | *Letters to His Family and Friends* [35698]; *Letters to Fanny Brawne* [60433] | — |

Notes on individual entries:

- ⚠ **Shelley's *Six Weeks' Tour*** was written jointly with Mary Shelley. The
  rule should admit only prose that is clearly the poet's own, so exclude it or
  use only passages attributable to him.
- **Shelley's *Prose Works*** may include fiction (his early Gothic romances);
  take only the essays.
- **Poe's *Eureka*** [32037] is subtitled "a prose poem". Exclude it as neither
  ordinary prose nor verse. His tales are fiction, so they are excluded too.
- **Whitman's** usable count is low (67 poems, 27 usable) because PoetryDB
  breaks his long lines across entries.
- **Burns** loses 38 of 99 poems to the same filter.
- **Coleridge's *Table Talk*** [8489] was recorded by his nephew. It is speech
  transcribed by another hand, so exclude it.
- **Byron's letters** are the heavily annotated standard edition. In every
  letter collection, editors' footnotes, linking commentary and introductions
  are not the poet's words and must be stripped. This is the main cleaning job.

## Possible, each with a catch: not in the first pass

- **John Donne** (28 usable): *Devotions* [23772], *Letters to Severall Persons
  of Honour* [37387], *Paradoxes and Problemes* [61783]. The texts are 17th
  century, so first check whether PoetryDB has modernised his poems' spelling
  while the prose keeps the original. Same-author pairing holds era constant,
  but not edition.
- **John Milton** (26): *Areopagitica* [608], *A Treatise of Civil Power*
  [79107]. Same spelling check as Donne.
- **William Cowper** (23): his letters are inside a single combined *Works*
  volume [47790] and would need extracting.
- **Rupert Brooke** (26): *Letters from America* [6445] is travel journalism.
- **Thomas Moore** (31): his *Life of Lord Byron* interleaves Byron's own
  letters, so the authorship is mixed.
- **Mary Robinson** (54; PoetryDB lists her only as "Robinson"): her *Memoirs*
  were completed by another hand after her death.

## Out

- **Emily Dickinson:** her letters are not on Gutenberg, which holds only her
  poems. The 1894 edition of her letters is public domain and held elsewhere,
  for example the Internet Archive. Reserved for a later robustness check
  (decision 5).
- **Alexander Pope:** his "essays" are verse; no prose found.
- **John Clare:** only a biography with fragments of his prose [9156].
- **Robert Herrick:** Gutenberg's "Robert Herrick" is the American novelist
  (1868–1938), not the poet. This is a name collision, not a holding.
- **No usable prose:** Shakespeare (drama only), Tennyson, Drayton, Hopkins,
  Chaucer (Middle English), Blake, McGonagall.
- **Only fiction available:** Longfellow, Eugene Field, Stephen Crane.

## What this implies for the design

- **Size.** Twelve poets with a cap of 10 gives **about 120 poems**, before
  comparison B's floor of 8 sentences thins it. Every first-pass poet has at
  least 22 usable poems, so the cap can be met everywhere.
- **The personal/argued split is confounded with poet.** Byron, Burns, Keats
  and both Brownings have only letters. Swinburne, Poe and Edward Thomas have
  only essays. A plain "letters versus essays" contrast therefore partly
  compares different poets. The clean contrast is **within** the poets who have
  both kinds: Shelley, Stevenson, Whitman and Coleridge.
- **Prose volume is not a constraint.** Each poem needs only a few hundred words
  of matched prose. Draw each poem's prose from a separate passage that doesn't
  overlap any other poem's, at a random offset that avoids openings and
  editorial matter.

## Next

1. ~~Write the selection rule into `task-8-segmentation-rule.md`.~~ Done
   2026-11-06. The rule adds a ceiling of 200 distinct lines per poem and the
   seed 20261106.
2. Download and clean the first-pass texts.
3. Wire in EmbeddingGemma 2 as the third model.
