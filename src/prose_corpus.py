"""The same-author prose corpus for task-8: download, extract, clean.

Each poet's prose comes from a specific printed edition on Project Gutenberg,
and every edition lays out the poet's words and its editor's apparatus
differently. So each edition gets its own extractor, written after reading the
edition, and all of them write the same table:

    data/processed/prose_units.parquet
        poet, source (Gutenberg id), work, register (personal | argued),
        unit (letter number, essay title, ...), recipient, text, n_words

One row is one natural unit: a letter, an essay. Paragraphs are separated by
blank lines inside `text`. Passages for matching are cut from these later;
nothing here knows about poems.

The rule being implemented is in backlog/docs/task-8-segmentation-rule.md
("Authorship: only the poet's own prose, written alone"), and what each
extractor does and why is in backlog/docs/task-8-prose-cleaning.md.

Run from the project root:

    uv run python src/prose_corpus.py
"""

import re
import time
from pathlib import Path

import pandas as pd
import requests

RAW = Path("data/raw/prose/gutenberg")
OUT = Path("data/processed/prose_units.parquet")
URL = "https://www.gutenberg.org/cache/epub/{id}/pg{id}.txt"
DELAY_SECONDS = 2


def fetch(gid: int) -> str:
    """Gutenberg plain text, cached; Gutenberg's header and licence stripped."""
    RAW.mkdir(parents=True, exist_ok=True)
    path = RAW / f"pg{gid}.txt"
    if not path.exists():
        r = requests.get(URL.format(id=gid), timeout=120)
        r.raise_for_status()
        path.write_bytes(r.content)
        time.sleep(DELAY_SECONDS)
    lines = path.read_text(encoding="utf-8").replace("\r", "").split("\n")
    s = next(i for i, l in enumerate(lines) if l.startswith("*** START"))
    e = next(i for i, l in enumerate(lines) if l.startswith("*** END"))
    # Some files repeat Gutenberg's closing line before the end marker.
    body = [l for l in lines[s + 1:e]
            if not re.match(r"\s*End of (the )?Project Gutenberg", l, re.I)]
    return "\n".join(body)


def paragraphs(lines):
    """Blank-line-separated paragraphs, each a list of raw lines."""
    buf = []
    for l in lines:
        if l.strip():
            buf.append(l)
        elif buf:
            yield buf
            buf = []
    if buf:
        yield buf


def indent(par) -> int:
    return min(len(l) - len(l.lstrip()) for l in par)


def is_verse(par) -> bool:
    """Line-structured paragraph: several short lines, nearly all capitalised.

    Wrapped prose fills its lines to ~70 characters; verse breaks early and
    capitalises each line. Used to drop verse quoted or enclosed in a letter.
    """
    if len(par) < 2:
        return False
    stripped = [l.strip() for l in par]
    capitalised = sum(s[:1].isupper() or s[:1] in "\"'(" for s in stripped)
    return max(map(len, stripped)) < 55 and capitalised / len(par) >= 0.75


# --------------------------------------------------------------------------
# Letter editions. The extraction logic is shared; each edition supplies its
# own heading pattern, end markers and fallback indent, learned by reading it.
# --------------------------------------------------------------------------

class LetterEdition:
    """A printed edition of a poet's letters, one heading per letter.

    The shared logic: a letter runs from its heading to the next heading or an
    end marker; its body indentation is measured from the letter itself (the
    commonest indent among its prose paragraphs), and paragraphs at any other
    indent are the editor's text or quotation; verse is dropped by shape;
    footnote blocks, editor's brackets, datelines, salutations, signatures and
    closing formulas are removed.
    """

    HEAD = None            # regex; group 1 = letter number, group 2 = recipient
    SEP = re.compile(r"^\s*\*\s+\*\s+\*")
    STOP = None            # regex for lines that end the current letter
                           # (a chapter heading between letters)
    END = None             # regex for the line where the letters section
                           # ends for good (appendix, index): nothing after
                           # it is searched for headings
    START = None           # regex for the line where the letters begin, when
                           # front matter would otherwise match HEAD
    FOOT = re.compile(r"^\s*\[(Sub-)?Footnote")
    DATELINE = re.compile(
        r"\b(1[78]\d\d|Jan|Feb|Mar|Apr|May|June?|July?|Aug|Sept?|Oct|Nov|Dec)"
        r"\w*\.?,?\s*\d*", re.I)
    SIGNATURE = re.compile(r"^\s*(([A-Z]\.\s*){1,3}|[A-Z][A-Z .]{2,25}\.?)\s*$")
    CLOSING = re.compile(r"\b(yours|affectionate|believe me|ever|truly|"
                         r"sincerely|faithfully|obliged|remain)\b", re.I)
    # "MY DEAR SIR,--", "My dear Reynolds--", "MY DAINTIE DAVIE--"
    # A salutation word or title ("Mr. Ridge,--"), a phrase in capitals
    # ("DEAR WEBSTER,--"), or one or two names ("Thomas Moore,--"). Not any
    # capitalised opening: "You will receive my Juvenilia,--" and "You will
    # feel for poor Hobhouse,--" are sentences.
    SALUTATION = re.compile(
        r"^(?:(?:My|MY|Deare?|DEAR|Dearest|DEAREST|Sir|SIR|Madam|MADAM|"
        r"Mr|Mrs|Miss|Dr)\b[A-Za-z .']{0,40},?|[A-Z][A-Z .']{0,40},"
        r"|[A-Z][a-z]+(?: [A-Z][a-z]+)?,)"
        r"(?:(?<=,)\s*-{1,2}|\s*--|\s*\u2014)\s*")
    DEFAULT_INDENT = 0     # used only when a letter has nothing to measure
    RECIPIENT = None       # for editions whose headings name no recipient

    def __init__(self, gid: int, label: str):
        self.gid, self.label = gid, label

    def keep(self, head) -> bool:
        return True

    def units(self):
        lines = fetch(self.gid).split("\n")
        if self.START:
            first = next(i for i, l in enumerate(lines) if self.START.match(l))
            lines = lines[first + 1:]
        if self.END:
            # Search only after the first letter: tables of contents list the
            # appendices before any letter appears.
            h0 = next(i for i, l in enumerate(lines) if self.HEAD.match(l))
            last = next((i for i, l in enumerate(lines[h0:], h0)
                         if self.END.match(l)), len(lines))
            lines = lines[:last]
        starts = [i for i, l in enumerate(lines) if self.HEAD.match(l)]
        for a, b in zip(starts, starts[1:] + [len(lines)]):
            head = self.HEAD.match(lines[a])
            if not self.keep(head):
                continue
            span = lines[a + 1:b]
            for j, l in enumerate(span):
                if ((self.SEP and self.SEP.match(l))
                        or (self.STOP and self.STOP.match(l))):
                    span = span[:j]
                    break
            text = self.clean(list(paragraphs(span)))
            if text:
                yield {"unit": self.unit_id(head, lines, a),
                       "recipient": (head.group(2) if head.re.groups >= 2
                                     else self.RECIPIENT),
                       "text": "\n\n".join(text)}

    def unit_id(self, head, lines, at) -> str:
        return f"{self.label}-letter{head.group(1)}"

    def body_indent(self, paras) -> int:
        inds = []
        for p in paras:
            if self.FOOT.match(p[0]):
                break
            if len(" ".join(p).split()) > 12 and not is_verse(p):
                inds.append(indent(p))
        return (max(set(inds), key=inds.count) if inds
                else self.DEFAULT_INDENT)

    def clean(self, paras) -> list[str]:
        lo = self.body_indent(paras)
        body, depth = [], 0
        for p in paras:
            # Footnotes: skip until brackets balance, so a nested
            # sub-footnote cannot end the footnote early.
            if depth > 0 or self.FOOT.match(p[0]):
                joined = " ".join(p)
                depth = max(depth + joined.count("[") - joined.count("]"), 0)
                continue
            if not lo <= indent(p) <= lo + 1 or is_verse(p):
                continue                     # editor's text, quotation, verse
            text = " ".join(l.strip() for l in p)
            if self.SIGNATURE.match(text) or re.fullmatch(r"\[[^\]]*\]\.?", text):
                continue                     # signature; editor's address line
            if not re.search(r"[a-z]", text):
                continue                     # all capitals, or a row of asterisks
            if re.match(r"_(Extract|Fragment|Part) of\b|_Extract from\b", text):
                continue                     # editor's italic note
            text = re.sub(r"\{([\w.]+)\}", r"\1", text)  # superscripts: Jan{y.} -> Jany.
            text = text.replace("_", "")             # Gutenberg's italic markup
            text = re.sub(r"(\s*\*)+\s*", " ", text).strip()  # editor's asterisks: omissions, censored names
            body.append(text)

        # Dateline or bare address at the top ("Burgage Manor.").
        while body and ((len(body[0].split()) <= 12 and self.DATELINE.search(body[0]))
                        or (len(body[0].split()) <= 4 and body[0].endswith("."))):
            body = body[1:]
        # Dated entry headings inside journal-letters ("Saturday, Jany. 2nd.")
        # and time stamps ("Evening, 9 o'clock.").
        stamp = re.compile(r"o'clock|\b(Morning|Evening|Night|Noon|Midnight|Monday|"
                           r"Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\b", re.I)
        body = [t for t in body if not (len(t.split()) <= 6
                                        and (self.DATELINE.search(t) or stamp.search(t)))]
        for i in range(min(3, len(body))):
            body[i] = self.SALUTATION.sub("", body[i])
        # Editor's insertions: [1], [Thursday], [sic]; and bracket stubs left
        # where an insertion spans a paragraph break.
        # Innermost first, so a nested insertion ("[think me[23]]") cannot
        # leave a stray bracket behind.
        def unbracket(t):
            while re.search(r"\[[^\[\]]*\]", t):
                t = re.sub(r"\s*\[[^\[\]]*\]", "", t)
            return t
        body = [unbracket(t) for t in body]
        body = [re.sub(r"\s*\[[^\]]*$", "", re.sub(r"^[^\[]*\]\.?\s*", "", t))
                for t in body]
        # Closing formulas, wherever they sit (often stranded before a P.S.).
        body = [t for t in body if not (len(t.split()) <= 6 and self.CLOSING.search(t))]
        body = [t for t in body if t.strip() and not (
            len(t.split()) <= 12 and t.endswith((",", "."))
            and self.CLOSING.search(t) and not re.search(r"[.!?].+[.!?]", t[:-1]))]
        # A closing fused onto the end of a paragraph ("... Write to me at
        # Malta. I am, with all sincerity,"): cut the fragment after the last
        # sentence break when it ends in a comma and reads as a closing.
        trimmed = []
        for t in body:
            if t.endswith(","):
                cut = max(t.rfind(". "), t.rfind("! "), t.rfind("? "),
                          t.rfind("--"), t.rfind("\u2014"))
                tail = t[cut + 1:] if cut >= 0 else t
                if self.CLOSING.search(tail) or re.search(r"\b(I am|am),", tail):
                    t = t[:cut + 1].rstrip(" -") if cut >= 0 else ""
            if t.strip():
                trimmed.append(t)
        body = trimmed
        # A very short paragraph ending in a comma is a closing broken across
        # lines ("Unhappy Son,"), wherever it sits; a short last one is the
        # lead-in to a signature ("In the interim I am, Dear Madam,").
        body = [t for t in body if not (len(t.split()) <= 6 and t.endswith(","))]
        while body and len(body[-1].split()) <= 8 and body[-1].endswith(","):
            body = body[:-1]
        return body


class Prothero(LetterEdition):
    """Byron, Letters and Journals, ed. Rowland E. Prothero (1898), vols 1-2.

    - Headings: "272.--To John Murray. [1]".
    - Vol. 1's body is usually indented two spaces with the editor's narrative
      flush left; vol. 2 is the reverse, with two-space indents used for
      quotations inside the editor's notes. Five letters break their own
      volume's pattern, hence per-letter measurement.
    - Footnotes are "[Footnote N: ...]" blocks after the annotated paragraph,
      sometimes several paragraphs long, sometimes with a nested
      "[Sub-Footnote A: ...]".
    - Vol. 2 separates letters with asterisks. Before the journal, every run
      of text between two separators is front matter, a chapter heading,
      verse from a verse letter, or a letter with an irregular heading
      (checked 2026-11-06), so a separator ends a letter. Both volumes end in appendices
      (vol. 1 reprints the Edinburgh Review's attack on Byron, which is
      Brougham's, not his); vol. 2 has a journal section, not used.
    - Adult prose only (Sungyeon, 2026-11-06): Byron turned 18 on 22 January
      1806. Letter 44 is the last certainly earlier (13 Dec 1805), 45-46 are
      undated, 47 (26 Feb 1806) the first certainly later, so vol. 1 starts at 47.
    """

    # Typeset irregularly in vol. 2: "174.-To", "176.---To", "188--To",
    # "192.--TO", "281.--To----Corbet". A strict pattern silently dropped
    # these letters, because the separator before them ended the previous one.
    HEAD = re.compile(r"^(\d+)\.?-{1,3}\s*To\b[\s-]*(.+?)\.?\s*(\[\d+\])?\s*$", re.I)
    STOP = re.compile(r"^(CHAPTER\b|JOURNAL\b)")
    END = re.compile(r"^(APPENDIX\b|END OF VOL)")
    SIGNATURE = re.compile(r"^\s*(B\.|BYRON\.?|N\. ?B\.?|BN\.?|Byron\.?)\s*$")

    def __init__(self, gid, label, default_indent, first_adult_letter=0):
        super().__init__(gid, label)
        self.DEFAULT_INDENT = default_indent
        self.first_adult_letter = first_adult_letter

    def keep(self, head):
        return int(head.group(1)) >= self.first_adult_letter


class Colvin(LetterEdition):
    """Keats, Letters to His Family and Friends, ed. Sidney Colvin (1891).

    - Headings: "IV.--TO CHARLES COWDEN CLARKE."
    - Body flush left; verse Keats copied into letters (often his own new
      poems) is indented two spaces or more.
    - Datelines are bracketed or partly bracketed: "[London,] November 20, 1816."
    - Footnotes are collected after the index at the back of the book; in the
      letters only the markers ("[9]") appear.
    - Rows of asterisks mark an omission *inside* a letter, not a boundary
      (unlike Prothero's vol. 2), so they do not end a letter.
    - Italic editor's notes open some letters ("_Extract from a letter
      dated_ ..."); superscripts are printed in braces ("2{d}", "n{r}").
    - Excludes the letters to Fanny Brawne, which Colvin omitted.
    - All letters are adult: Keats was born 31 October 1795, and the first
      letter is dated 31 October 1816.
    """

    HEAD = re.compile(r"^([IVXLC]+)\.?--TO (.+?)\.\s*$")   # "XIV--TO" lacks the stop
    END = re.compile(r"^INDEX\b")
    SEP = None             # asterisks mark omissions inside a letter here


class BuxtonForman(LetterEdition):
    """Keats, Letters to Fanny Brawne, ed. H. Buxton Forman (1878).

    - Headings are bare Roman numerals on their own line ("XIV."), grouped
      under flush-left section titles ("WENTWORTH PLACE.") that the
      indentation rule drops.
    - Body indented four spaces; verse six; datelines, postmarks and
      signatures pushed far right.
    - Editor's conjectures are bracketed ("[think me]"), and footnotes follow
      "THE END" at the back. An appendix on Wentworth Place follows the last
      letter.
    - Uses Unicode em dashes, not "--".
    - The appendix after the last letter is numbered with the same bare
      numerals as the letters and quotes others' recollections of Keats, so
      the letters section ends at "APPENDIX".
    """

    HEAD = re.compile(r"^([IVXLC]+)\.\s*$")
    END = re.compile(r"^(APPENDIX\b|THE END\b)")
    RECIPIENT = "Fanny Brawne"
    # The introduction's front matter repeats the title; start at the
    # second, real one. The appendix has its own sections numbered "I.",
    # "II.", quoting others' recollections of Keats: END stops before it.
    START = re.compile(r"^LETTERS TO FANNY BRAWNE\.\s*$")
    DEFAULT_INDENT = 4


class LoganRobertson(LetterEdition):
    """Burns, The Letters of Robert Burns, selected by J. Logie Robertson.

    - Three sections, each opened by the editor's prefatory note: General
      Correspondence (split in two around the others), Letters to Clarinda,
      and the Thomson letters. Only Burns's own letters are printed;
      Clarinda's and Thomson's side appears only in footnotes.
    - General letters are headed "LVI-To DR. MOORE.", with dashes typeset
      irregularly; one, XXXI, is a mock decree headed "IN THE NAME OF THE
      NINE". Clarinda and Thomson letters are headed by a bare numeral,
      sometimes without its full stop ("IX").
    - Scanning errors in the numerals ("LVIL" for LVII, "CXVIII" printed for
      CXCVIII, which duplicates a real letter), so letters are identified by
      section and running sequence, with the printed numeral kept as a label.
    - Asterisk rows usually separate letters but sometimes mark an omission
      inside one, so they do not end a letter; headings and section titles do.
    - Body flush left; verse indented two; footnotes "[Footnote N: ...]"
      indented three, placed after the paragraph or at the letter's end.
    - All letters are adult: Burns was born 25 January 1759, and the first
      letters (to Alison Begbie) date from about 1780.
    """

    HEAD = re.compile(
        r"^([IVXLC]+)\.?(?:-{1,3}\s*(?:TO\b\s*(.+?)|(IN THE NAME OF THE NINE.*?)))?"
        r"\s*(\[\d+\])?\s*$", re.I)
    SECTION = re.compile(r"^(GENERAL CORRESPONDENCE|THE CLARINDA LETTERS|"
                         r"LETTERS TO CLARINDA|THE THOMSON LETTERS?)\b")
    STOP = re.compile(r"^(GENERAL CORRESPONDENCE|THE CLARINDA LETTERS|"
                      r"NOTE PREFATORY|LETTERS TO CLARINDA|THE THOMSON LETTERS?|"
                      r"PREFATORY NOTE)\b")
    START = re.compile(r"^GENERAL CORRESPONDENCE\.\s*$")
    SEP = None

    def __init__(self, gid, label):
        super().__init__(gid, label)
        self.seq = 0

    def unit_id(self, head, lines, at):
        self.seq += 1
        section = "general"
        for l in reversed(lines[:at]):
            m = self.SECTION.match(l)
            if m:
                section = ("clarinda" if "CLARINDA" in m.group(1) else
                           "thomson" if "THOMSON" in m.group(1) else "general")
                break
        return f"{self.label}-{self.seq:03d}-{section}-{head.group(1)}"

    def units(self):
        self.seq = 0
        for u in super().units():
            if u["recipient"] is None:
                u["recipient"] = ("Clarinda (Agnes M'Lehose)" if "clarinda" in u["unit"]
                                  else "George Thomson" if "thomson" in u["unit"]
                                  else None)
            yield u


# --------------------------------------------------------------------------
# Registry: one entry per edition, added as each is read and its extractor
# written. Never point an extractor at an edition it was not written for.
# --------------------------------------------------------------------------

SOURCES = [
    ("George Gordon, Lord Byron", 8901, "Letters and Journals, vol. 1 (ed. Prothero)",
     "personal", Prothero(8901, "vol1", 2, first_adult_letter=47)),
    ("George Gordon, Lord Byron", 9921, "Letters and Journals, vol. 2 (ed. Prothero)",
     "personal", Prothero(9921, "vol2", 0)),
    ("John Keats", 35698, "Letters to His Family and Friends (ed. Colvin)",
     "personal", Colvin(35698, "colvin")),
    ("John Keats", 60433, "Letters to Fanny Brawne (ed. Buxton Forman)",
     "personal", BuxtonForman(60433, "brawne")),
    ("Robert Burns", 9863, "The Letters of Robert Burns (ed. Logie Robertson)",
     "personal", LoganRobertson(9863, "burns")),
]


def main():
    rows = []
    for poet, gid, work, register, extractor in SOURCES:
        n0 = len(rows)
        for u in extractor.units():
            rows.append({"poet": poet, "source": gid, "work": work,
                         "register": register, **u,
                         "n_words": len(u["text"].split())})
        got = rows[n0:]
        print(f"{poet:28s} {gid:6d}  {len(got):4d} units  "
              f"{sum(r['n_words'] for r in got):7d} words  {work}")
    df = pd.DataFrame(rows)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(OUT, index=False)
    print(f"\n{len(df)} units, {df.n_words.sum()} words -> {OUT}")


if __name__ == "__main__":
    main()
