import re

def clean_abstract(text: str) -> str:
    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text)
    text = text.strip()

    # Optional: normalize LaTeX-ish spacing, but do not over-clean mathematical terms
    text = text.replace("``", '"').replace("''", '"')

    return text
