# Cleaning the same-author prose

How each poet's prose is extracted from its edition, what was removed and why,
and what checks the output passed. The rule being implemented is the
authorship rule in `task-8-segmentation-rule.md`: only the poet's own prose,
written alone, with editors' material and quotation removed.

Code: `src/prose_corpus.py`, one extractor per edition. Output:
`data/processed/prose_units.parquet`, gitignored. Regenerate with
`uv run python src/prose_corpus.py`; downloads are cached in
`data/raw/prose/gutenberg/`.

**Status (2026-11-06):** Byron, Keats, Burns, both Brownings and Coleridge
done. 2,052 units (letters, essay chapters), about 1,293,000 words. Coleridge
is the first poet with both registers: letters (*personal*) and the
*Biographia Literaria* (*argued*).

| poet | edition | register | units | words |
|-|-|-|-|-|
| Byron | Prothero, vol. 1 (adult letters only) | personal | 122 | 45,854 |
| Byron | Prothero, vol. 2 | personal | 210 | 50,227 |
| Keats | Colvin, *Letters to His Family and Friends* | personal | 164 | 108,139 |
| Keats | Buxton Forman, *Letters to Fanny Brawne* | personal | 37 | 12,200 |
| Burns | Logie Robertson, *The Letters of Robert Burns* | personal | 268 | 104,656 |
| Robert Browning | *Letters of RB and EBB*, vols 1–2 (his letters only) | personal | 286 | 160,630 |
| E. B. Browning | *Letters of RB and EBB*, vols 1–2 (her letters only) | personal | 287 | 222,780 |
| E. B. Browning | Kenyon, *Letters of EBB*, vols 1–2 | personal | 394 | 278,835 |
| Coleridge | E. H. Coleridge, *Letters*, vols 1–2 (adult only) | personal | 257 | 198,731 |
| Coleridge | *Biographia Literaria*, chapters | argued | 24 | 94,938 |
| Coleridge | *Biographia Literaria*, Satyrane's Letters | personal | 3 | 16,099 |

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

## Burns: *The Letters of Robert Burns*, ed. J. Logie Robertson

Gutenberg 9863. Done 2026-11-06. **268 letters, about 105,000 words.** All are
adult: Burns was born 25 January 1759, and the earliest letters (to Alison
Begbie) date from about 1780.

### How the edition is laid out

- **A selection, in three sections, each opened by the editor's prefatory
  note.** The sections are General Correspondence (206 letters, split in two
  around the others), Letters to Clarinda (34) and the Thomson letters (28).
  Only Burns's side is printed; Clarinda's and Thomson's appear only in
  footnotes, which are removed.
- **Headings.** General letters are headed "LVI-To DR. MOORE.", with dashes
  typeset irregularly. Clarinda and Thomson letters are headed by a bare
  numeral, sometimes without its full stop ("IX"). One general item, XXXI,
  is not a letter but a mock decree headed "IN THE NAME OF THE NINE"; it is
  Burns's own prose and is kept.
- **Scanning errors in the numerals:** "LVIL" for LVII, "CXLL" for CXLI, "CII"
  twice, "CXVIII" printed for CXCVIII (duplicating a real letter). Letters are
  therefore identified by section and running sequence
  (`burns-239-general-CCV`), with the printed numeral kept only as a label.
- **Asterisk rows** usually separate letters but three times mark an omission
  inside one, with Burns's own text after them. So they do not end a letter;
  headings and section titles do. Section titles also cut off the editor's
  prefatory notes.
- **Footnotes** are indented `[Footnote N: ...]` blocks. Verse is indented two
  spaces.

### Checks the Burns output passed

- **Every section complete and in order:** General I–CCVI, Clarinda I–XXXIV,
  Thomson I–XXVIII. Every apparent step backwards in the general numbering is
  one of the scanning errors above.
- **No residue:** no brackets, footnotes, prefatory notes, separators or
  italic markup.
- **Read in full:** two letters (seed 5; General CCV, Thomson XII), plus a
  sample of 12 short paragraphs. That sample found two leaks, now fixed:
  Gutenberg's closing line, which this file repeats before its end marker, and
  time stamps inside letters ("Evening, 9 o'clock.").

### Scots: the reason Burns is reported separately

`scratch/scots_share_probe.py` counts the share of words found in a list of
common Scots forms (a lower bound, for comparison only):

| text | Scots words |
|-|-|
| the 10 drawn poems | 3.1% (one ballad 17.7%, five 0%) |
| all 58 eligible poems | 6.1% (26 above 5%) |
| his letters | 0.2% (2 of 268 above 5%) |
| Byron's and Keats's letters | 0.0% |

The letters are standard English. The poems carry some Scots, but **less than
first assumed**: the draw happened to pick mostly English poems, and only one
drawn poem is heavily Scots. The gap is real and points the same way as the
claim, so separate reporting stays.

## The Brownings

Done 2026-11-06.

### *The Letters of Robert Browning and Elizabeth Barrett Barrett, 1845–1846* (2 vols, 1899)

Gutenberg 16182 and 73891, published by their son.

- **Splitting by writer.** Every letter is headed by its direction:
  "_R.B. to E.B.B._" or "_E.B.B. to R.B._". Authorship is therefore printed,
  not inferred, and each poet gets only the letters headed with their own
  initials. This is the two-writer rule in `task-8-segmentation-rule.md`.
  Every letter has a heading, so one writer's text cannot run into the
  other's. **Counts match exactly:** vol. 1 has 140 R.B. and 141 E.B.B.
  headings; vol. 2 has 146 of each.
- **Layout and apparatus:**
  - the body is flush left; datelines, addresses and signatures are pushed
    right;
  - there are few footnotes, all in vol. 1;
  - asterisk rows in vol. 2 mark breaks inside a letter, with the same writer
    continuing, so they do not end one;
  - vol. 1 ends at "END OF THE FIRST VOLUME", vol. 2 at its index, after which
    come the publisher's advertisements.
- **Kept:** short quotations of the other's last letter at the opening of a
  paragraph ("'Vex me,' or 'teaze me,' my own Ba, you cannot..."). These are
  brief inline quotation, kept as for every poet; only set-off quotation is
  removed.

### *The Letters of Elizabeth Barrett Browning*, ed. Frederic G. Kenyon (2 vols, 1897)

Gutenberg 13018 and 16646. **The hardest edition so far.**

- **Kenyon's narrative shares the letters' indentation.** It opens each
  chapter and also runs between letters, flush left like her letters. It
  appears sometimes straight after her signature, sometimes after footnotes
  or an asterisk row. Her own postscripts also follow her signature. Neither
  indentation nor position separates the two voices.
- **The fix is a voice filter** (`KenyonEBB.editorial`). With quotations set
  aside, a paragraph is Kenyon's if it either:
  - uses his narrative phrasing: "Miss Barrett's", "Mrs. Browning's", "the
    Brownings", "the following letter", or a sentence opening with her name;
    or
  - has no I, you or we of its own *and* refers to her, her letters or her
    books.

  Once his voice appears, **the rest of the span up to the next heading is
  dropped.** His narrative runs on to introduce the next letter, and the
  documents he quotes in full sit inside it.
- **Two refinements came from auditing the filter:**
  - *Too broad at first.* The first version also dropped her own impersonal
    lines ("The weather is wonderfully warm."). Counting "we/us/our" as her
    voice, and requiring a reference to her, fixed that.
  - *Too narrow at first.* Without the truncation, documents Kenyon quotes in
    full passed as hers, because they are written in the first person:
    **Thackeray's letter to her** ("My dear, kind Mrs. Browning,--Has Browning
    ever had an aching tooth...") and Mary Russell Mitford's recollection of
    her.
- **Final audit:**
  - a sample of 18 dropped paragraphs: all Kenyon;
  - every kept paragraph naming her in the third person outside quotation
    marks: both are hers ("never to call me Miss Barrett again", and her
    protest about the *Athenaeum*);
  - 14 randomly chosen last paragraphs, plus the final letter of 1861: all
    hers, with no editor's coda.
- **One known loss:** her formal note to Mr. Westwood, written entirely in
  the third person ("Miss Barrett, inferring Mr. Westwood from the
  handwriting, begs..."). The filter takes it for Kenyon, so vol. 1 yields 220
  letters from 221 headings. Vol. 2 yields 174 from 174.
- **Other details:**
  - vol. 1 footnotes follow the annotated paragraph, with her text
    continuing after them; vol. 2 collects a "FOOTNOTES:" section at each
    chapter's end, which ends a letter;
  - one heading carries a footnote marker ("_To Mr. Westwood_[59]") and was
    at first missed, merging two letters;
  - Kenyon's transcriptions of endorsements ("(Endorsed in another hand)
    ...") are dropped.

### Why E. B. Browning has so much prose

Her prose comes from two sources, 681 letters and about 500,000 words. She is
still one poet with a cap of 10 poems, so the amount of prose changes nothing
in the comparison. It only gives more room to place each poem's matched
passage.

## Coleridge

Done 2026-11-06.

### *Letters of Samuel Taylor Coleridge*, ed. Ernest Hartley Coleridge (2 vols, 1895)

Gutenberg 44553 and 44554.

- **Headings:** "XII. TO ANNE EVANS.". "TO THE SAME." is resolved to the
  previous named recipient.
- **Layout:** the body is flush left; closings, signatures and quoted verse
  are indented. Footnotes are collected after each volume's index, and the
  letters end at "INDEX".
- **Adult prose only:** Coleridge turned 18 on 21 October 1790. Letters VI
  (February 1785, from Christ's Hospital, aged 12) and VII (undated, "before
  1790") are excluded. Letter VIII (October 1791) is the first kept.
- **The editor writes between letters, at the body's indentation, as Kenyon
  did,** but rarely. Examples: "In the diary of his voyage on the Speedwell
  Coleridge records..." and "The origin of Coleridge's friendship with
  Thomas Allsop...". The voice filter is now a shared base class,
  `EditorNarrated`, with each edition supplying its own narrative and
  subject patterns. Kenyon's output was byte-identical after the refactor.
- **Three tunings came from auditing it on Coleridge:**
  - *His own name.* In "S. T. Coleridge" and "Mr. Coleridge", the full stop
    of an initial made the name look like a sentence opening with "Coleridge",
    which is narration. Five of his own letters (to Southey, his wife, Davy)
    were lost. Now "Coleridge" after "S. T." or "Mr." does not count, and a
    full stop after a capital initial ends no sentence.
  - *Editor's notes before a letter.* The note introducing the Allsop letter
    sits after the heading, before the letter. Truncating there lost the
    letter. Editor's paragraphs before any of the writer's own text are now
    skipped instead; this changed nothing in Kenyon.
  - *"He" is not narration here.* Coleridge writes "he" about other people
    constantly ("On this ruinous plan poor Southey has been toiling..."), so
    "he/his" made ten of his own paragraphs look like the editor's, and each
    misfire cut the rest of its letter. The editor's subject is now only
    "Coleridge" in the third person, or the documents themselves
    ("transcript", "MS.", "original").
- **Final audit:**
  - **every heading accounted for:** vol. 1 has 143 headings, giving 141
    letters (the 2 juvenile letters excluded); vol. 2 has 116, giving 116;
  - the filter flags exactly three paragraphs, all the editor's, and removes
    973 words in all;
  - every kept mention of "Coleridge" is his own (his family, his son's name,
    his address);
  - Coleridge's own playful third-person note ("Mr. S. T. Coleridge, F. R. S.
    L. ... has the honour") is kept: unlike Elizabeth Barrett Browning's
    Westwood note, it is now recognised as his.

### *Biographia Literaria* (1817)

Gutenberg 6081. The first essay source: **no editor stands between Coleridge
and the reader, and the risk shifts to quotation.**

- **Units:** chapters I–XXIV (*argued*), plus the three Satyrane's Letters
  between XXII and XXIII. Those are travel letters from Germany, so they are
  tagged *personal*. Registers are now set per unit, not only per edition.
- **Dropped:**
  - each chapter's opening topic summary ("Motives to the present
    work--Reception of the Author's first publication--...");
  - Coleridge's own footnotes, collected after Chapter XXIV; notes are a
    different kind of writing from the running argument;
  - the German epigraph and its translation, which come before Chapter I.
- **Quotation:** set-off quotation is indented and dropped by the indent rule.
  Some sits flush left, so three rules are added for this edition:
  - **Non-English paragraphs** are dropped by a share-of-English-function-words
    test, `mostly_english`, available to every edition. English prose scores
    about 0.4; the Latin and German passages score 0.01–0.08.
  - **A quotation opening a paragraph** is cut, and his continuation kept
    ("“Esemplastic. The word is not in Johnson...” Neither have, I...").
    A paragraph whose opening quotation never closes is one paragraph of a
    longer quotation, and is dropped. One deliberate casualty: the "letter
    from a friend" in Chapter XIII, which Coleridge wrote himself but
    presents as a quotation.
  - **"TRANSLATION." paragraphs**, his renderings of others' words, are
    dropped.
- **Checks:**
  - all 27 units present;
  - no paragraph opens with a quotation mark, and none is non-English;
  - the paragraphs dense with quotation marks are his own analysis of short
    quoted phrases;
  - three random long paragraphs were read, all clean.

### Not used

His *Literary Remains*, *Aids to Reflection* and *Table Talk* are on Gutenberg.
*Table Talk* is excluded as speech transcribed by another hand. The other two
are not needed: the *Biographia* alone gives about 95,000 words of argued
prose.

## Changes that affected every edition

Made while adding Burns, and checked against the earlier output letter by
letter:

- **Italic markup removed.** Gutenberg marks italics with underscores
  ("_jeu-d'esprit_"); those are typesetting, not words.
- **Salutation rule narrowed.** It now accepts a salutation word or title
  ("Mr. Ridge,--"), a phrase in capitals ("DEAR WEBSTER,--"), or one or two
  names ("Thomas Moore,--"), and no longer any capitalised opening before a
  dash. The broad version had wrongly cut two real sentences: Byron's "You
  will feel for poor Hobhouse,--" and Keats's "Your Letter to me at Bedhampton
  hurt me very much,--". Both are now kept.
- **Gutenberg's closing line and short time stamps** are dropped, in every
  edition.
- **Dates and stamps inside a letter are now dropped only when they really
  are dates and stamps.** A date must contain a number ("50 Walpole Street:
  Feb. 3, 1845."), and a time stamp must be four words or fewer ("Evening, 9
  o'clock."). A looser version, briefly in use while adding the Brownings,
  dropped real sentences such as "Good night and sound rest, my dearest
  Clarinda!", and matched "Mar" in "Margaret" as a month. The filter also runs
  after bracket removal, because an editor's bracket can span a blank line.
- **Signatures and address stubs:** a short line with two words in capitals
  ("JOHN KEATS alias JUNKETS.") is a signature. One or two words ending in
  punctuation ("Maybole,.") is an address stub. Salutations are stripped after
  both, so a date stub at the top cannot hide one.
- **Compounds broken at a line end are rejoined** ("anti-" / "ministerial"
  became "anti- ministerial"). A line ending in a single hyphen joins the next
  without a space; "--" keeps its space. Two units changed, and in both the
  joined hyphen was the only difference.
- **Every shared change is diffed against the previous output, letter by
  letter.** The last round changed 10 earlier letters, all improvements or
  trivial losses ("Adieu.", "Amen.").

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
