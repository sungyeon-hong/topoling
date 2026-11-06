# Cleaning the same-author prose

How each poet's prose is extracted from its edition, what was removed and why,
and what checks the output passed. The rule being implemented is the
authorship rule in `task-8-segmentation-rule.md`: only the poet's own prose,
written alone, with editors' material and quotation removed.

Code: `src/prose_corpus.py`, one extractor per edition. Output:
`data/processed/prose_units.parquet`, gitignored. Regenerate with
`uv run python src/prose_corpus.py`; downloads are cached in
`data/raw/prose/gutenberg/`.

**Status (2026-11-06):** Byron and Keats done, 533 letters, about 216,000
words.

| poet | edition | letters | words |
|-|-|-|-|
| Byron | Prothero, vol. 1 (adult letters only) | 122 | 45,851 |
| Byron | Prothero, vol. 2 | 210 | 50,234 |
| Keats | Colvin, *Letters to His Family and Friends* | 164 | 108,178 |
| Keats | Buxton Forman, *Letters to Fanny Brawne* | 37 | 12,200 |

**Decisions (Sungyeon, 2026-11-06):**

- **Adult prose only:** writing from age 18 on. Byron's childhood letters are
  excluded. Keats's letters are all adult.
- **Period mismatch accepted.** Prose is matched by author, not by date. The
  rule asks for the same author, and PoetryDB does not date poems. Byron's
  letters stop in 1814 while about half his drawn poems are later. A
  period-matched check is a later robustness test, not part of the first pass.

**Every edition gets its own extractor, written after reading the edition.**
The layout of the poet's words and the editor's apparatus differs between
editions, and even between volumes of one edition (Byron below), so a generic
cleaner would silently keep editors' text. Never point an extractor at an
edition it was not written for.

## Byron: *Letters and Journals*, ed. Prothero (1898), vols 1–2

Gutenberg 8901 and 9921. Done 2026-11-06.

**Result:** 332 adult letters, about 96,000 words of Byron's prose (vol. 1:
122 letters; vol. 2: 210). One letter, no. 291 to Moore, is written entirely
in verse and correctly yields nothing. **Every letter heading in both volumes
is accounted for:** vol. 2 has 211 headings, giving 210 letters plus the verse
letter; vol. 1 has 168, of which 46 are childhood letters.

### How the edition is laid out

- Each letter opens with a heading: `272.--To John Murray. [1]`.
- **The editor's material is everywhere.** There are chapter introductions,
  linking narrative between letters, and `[Footnote N: ...]` blocks after
  annotated paragraphs. Some footnotes run to several paragraphs, and some
  contain a nested `[Sub-Footnote A: ...]`. Inline markers (`[1]`) and inserted
  conjectures (`[Thursday]`, `[At 63, Portland Place.]`) are the editor's too.
- **The two volumes are laid out oppositely.**
  - In vol. 1 the letter body is usually indented two spaces and Prothero's
    narrative is flush left.
  - In vol. 2 the body is flush left, two-space indents are quotations inside
    Prothero's notes (Moore's recollections, for example), and letters are
    separated by rows of asterisks.
  - Five letters break their own volume's pattern.
- **Each volume ends in appendices.** Vol. 1 reprints the *Edinburgh Review*'s
  attack on *Hours of Idleness*, which is Henry Brougham's prose, not Byron's.
  The first parser attached all of it to the volume's last letter.
- **Vol. 2 contains Byron's 1813–14 journal** as a separate section. It is not
  used: the letters are ample.

### What the extractor does

1. **Where a letter ends.** A letter runs from its heading to the next heading,
   asterisk separator, chapter, appendix, journal section or end of volume.
2. **Body indentation is measured per letter.** It is the most common indent
   among the letter's prose paragraphs before its first footnote, with
   verse-shaped paragraphs ignored. A fixed per-volume indent lost letters 35,
   111 and 116 entirely, and enclosed verse outvoted the prose in letter 295.
   Paragraphs at any other indent are the editor's text or quotation, and are
   dropped.
3. **Footnotes are skipped until brackets balance.** This means a nested
   sub-footnote cannot end the footnote early. That failure is how letter 10
   first kept Prothero's account of Byron's Harrow speeches.
4. **Verse is dropped by shape**: several lines under 55 characters, at least
   three quarters starting with a capital. Byron copies verse into letters
   flush left, so indentation alone does not catch it.
5. **Datelines, address lines, salutations, signatures and closing formulas
   are removed.** That covers "Newstead Abbey, Nov. 8th, 1798.", "Burgage
   Manor.", "MY DEAR SIR,--", "BYRON.", and "Ever yours most sincerely,"
   wherever it sits, including when it is fused onto the end of a real
   paragraph or stranded before a postscript.
6. **Postscripts are kept.** They are Byron's own words. An early version
   dropped everything after the signature, and lost his postscripts written
   without "P.S.".
7. **All bracketed text is removed.**

### Checks the output passed

- **No residue:** no `[` or `]`, no "Footnote", no "APPENDIX", and no phrase of
  Brougham's review anywhere in the output.
- **Every exception inspected:** the five letters that break their volume's
  pattern were each checked by hand.
- **Byron's own odd registers survive.** Letter 225's mock-archaic "ye boke is
  ye boke of a cock-brained man" is Byron's, not an editor's, and is kept.
- **Two letters were read in full**, chosen at random (seed 7) from letters of
  150–400 words: nos. 99 and 225. Both are clean.
- **27 paragraphs still end in a comma.** Most are Byron's sentences running
  on into a removed quotation ("the first line of Pope's couplet,"). A few are
  formal closings ("I have the honour to be,"). Left as they are: fragments of
  27 paragraphs in about 111,000 words.

### Found after the first pass

These were found while generalising the extractor for Keats.

- **Irregular headings silently lost letters.** Vol. 2 prints some headings
  as "174.-To", "176.---To", "188--To", "192.--TO" and "281.--To----Corbet".
  The strict pattern missed them. Because an asterisk separator ends the
  letter before, each missed letter was dropped, not merged, so nothing
  wrong got in but 12 letters were lost. The heading pattern now accepts
  these forms.
- **Separators are letter boundaries in vol. 2.** Checked: before the
  journal, every run of text between two separators is front matter, a
  chapter heading, verse from a verse letter, or a letter with an irregular
  heading. After the journal begins, the runs are appendices: Byron's
  Parliamentary speeches, Walter Scott's replies to him, newspaper attacks.
  The letters section ends at the first appendix, so none of that enters.
- **The table of contents lists "APPENDIX I." before any letter**, so the end
  marker is searched for only after the first letter heading.

### Resolved

- **Childhood letters excluded** (adult prose only). Byron turned 18 on 22
  January 1806. Letter 44 (13 December 1805) is the last certainly earlier,
  letters 45–46 are undated, and letter 47 (26 February 1806) is the first
  certainly later. Vol. 1 therefore starts at letter 47; letters 1–46 are
  excluded.
- **Period mismatch accepted.** Gutenberg holds only vols 1–2 of Prothero's
  six, so the letters stop in 1814. About half of the 10 drawn Byron poems are
  later (1815–23). Byron's later letters are on Gutenberg only inside Moore's
  *Life of Byron*, interleaved with Moore's narrative and bowdlerised. They are
  not used.

## Keats

Done 2026-11-06. **201 letters, about 120,000 words.** All are adult: Keats was
born 31 October 1795, and his first letter is dated 31 October 1816. The two
collections do not overlap. Colvin's "Fanny" letters are to Fanny Keats, his
sister; Colvin omitted the letters to Fanny Brawne.

### *Letters to His Family and Friends*, ed. Sidney Colvin (1891)

Gutenberg 35698. 164 letters, numbered I–CLXIV with no gaps.

- **Headings:** "IV.--TO CHARLES COWDEN CLARKE." One, "XIV--TO FANNY KEATS.",
  lacks the full stop and was at first merged into letter XIII.
- **Layout:** the body is flush left. Verse Keats copied into his letters,
  often first drafts of his own poems, is indented two spaces or more and is
  dropped. So is his transcription of Hazlitt's letter to Gifford.
- **Footnotes** are collected after the index; only markers ("[9]") appear in
  the letters. Datelines are bracketed or partly bracketed.
- **Rows of asterisks mark an omission inside a letter,** the opposite of
  Byron's vol. 2. At first they were treated as letter boundaries, which cut
  off the rest of 13 letters. Letter CVIII lost everything but the editor's
  italic note. They no longer end a letter.
- **Other details:**
  - italic editor's notes open some letters ("_Extract from a letter dated_
    ...") and are dropped;
  - superscripts printed in braces ("Jan{y.}", "2{d}") are flattened;
  - the dated entry headings inside the long journal-letters to George and
    Georgiana ("Saturday, Jany. 2nd.") are dropped.
- **Kept:** in letter XVIII Keats quotes his own earlier words to Bailey ("a
  long poem is a test of invention"). That is his own prose.

### *Letters to Fanny Brawne*, ed. H. Buxton Forman (1878)

Gutenberg 60433. 37 letters.

- **Headings and layout:** headings are bare Roman numerals ("XIV."). The body
  is indented four spaces and verse six; datelines, postmarks and signatures
  are pushed far right. The text uses em dashes rather than "--".
- **The appendix reuses the letters' numbering.** It is numbered "I.", "II."
  ... just like the letters, and quotes others' recollections of Keats
  ("I did not know Keats at the time the review appeared..."). At first these
  became a phantom letter I. The letters section now ends at "APPENDIX".
- **Nested editor's brackets** ("[think me[23]]", words supplied by the
  editor) left a stray "]" when brackets were removed in one pass, and that
  deleted the start of letter I. Brackets are now removed innermost first.

### Checks the Keats output passed

- **Every heading accounted for:** 164 and 37 headings give 164 and 37 letters.
- **No residue:** no brackets, footnotes, index or appendix text, separators,
  or editor's asterisks anywhere in the prose table.
- **One letter from each edition read in full** (seed 11; Colvin CXLIV,
  Brawne XXXI): both are Keats's prose only.
- **Byron re-checked after every shared change.** The six differences were
  all improvements (a heading, a stanza label and signatures removed).

## What this says about cost

Byron took one session of iteration: reading, six rounds of parser fixes, and
inspection. Keats took less, because the shared logic carried over, but still
found five edition-specific traps. Two of them (irregular headings, and
separators that mean opposite things in different editions) *lose* text
silently rather than admitting wrong text. The check that catches both is
counting headings against extracted letters, which every edition should get. His was expected to be the worst edition for editorial material,
and it was. Other letter editions (Keats, Burns, the Brownings, Coleridge) will
have their own conventions but probably lighter apparatus. Essay collections
(Shelley, Swinburne, Poe, Stevenson, Edward Thomas) should be simpler, except
for quotation, which essays carry far more of than letters.
