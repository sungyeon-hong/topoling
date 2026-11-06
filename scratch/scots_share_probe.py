"""How much Scots is in Burns's drawn poems, his eligible poems, and his letters?

Written 2026-11-06 for task-8. Burns is reported separately because a dialect
gap between poems and prose would push his poems' spread in the same direction
as the claim (an embedding model trained mostly on modern English may place
Scots words idiosyncratically). This measures the size of that gap.

Method: the share of word tokens found in a small hand-made list of common
Scots forms, after normalising curly apostrophes (PoetryDB prints "a'" as
"a’"). The list is incomplete, so the shares are lower bounds and are for
comparing texts, not for absolute claims. Byron's and Keats's letters are the
English baseline.

Result on 2026-11-06: drawn poems 3.1% on average (one ballad at 17.7%, five
at 0%), all 58 eligible poems 6.1% (26 above 5%), letters 0.2% (2 of 268
above 5%), Byron and Keats letters 0.0%.

Run from the project root, after src/draw_task8_poems.py and
src/prose_corpus.py:

    uv run python scratch/scots_share_probe.py
"""

import re
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from poetry_forms import is_wrap_fragment                    # noqa: E402

SCOTS = set("""
ae ane auld awa aye bairn bairns bonie bonnie brae braes braw cauld canna
couldna didna dinna doon e'en een fu gae gaed gang gane gat gie gied gin gowd
gude guid ha hae hame ilka ither ken kens kent kirk lang lo'e lea mair maun nae
naething nane nicht o' oot ower owre sae sair sang sic sma syne tak tauld thae
thegither thro tae twa wa wad wadna wark waur wee weel wha whare wi' wie yon
yont aften ance amang aboon afore blythe dool fause frae gaun greet jo laddie
lass lassie lo'ed mony neebor puir richt stane tint unco wean weans whyles
wyte a' an' ca' fa' wa' gi'e ha'e o'er e'e tho' ilk mysel' himsel'
""".split())


def share(text: str) -> float:
    words = re.findall(r"[a-z']+", text.lower().replace("’", "'"))
    return sum(w in SCOTS for w in words) / max(1, len(words))


def verse(lines) -> str:
    return " ".join(l for l in lines if l.strip() and not is_wrap_fragment(l))


def main():
    draw = pd.read_parquet("data/processed/task8_poem_draw.parquet")
    burns = draw[draw.author == "Robert Burns"]
    drawn = burns[burns.status.isin(["drawn", "replacement"])]
    prose = pd.read_parquet("data/processed/prose_units.parquet")

    s = [share(verse(l)) for l in drawn["lines"]]
    print("drawn poems:", [round(100 * x, 1) for x in s],
          f"mean {100 * sum(s) / len(s):.1f}%")
    s = [share(verse(l)) for l in burns["lines"]]
    print(f"all eligible poems: mean {100 * sum(s) / len(s):.1f}%, "
          f"above 5%: {sum(x > 0.05 for x in s)} of {len(s)}")
    for poet in prose.poet.unique():
        s = prose[prose.poet == poet].text.map(share)
        print(f"{poet} letters: mean {100 * s.mean():.1f}%, "
              f"above 5%: {(s > 0.05).sum()} of {len(s)}")


if __name__ == "__main__":
    main()
