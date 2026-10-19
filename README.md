# topoling

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23466441.svg)](https://doi.org/10.5281/zenodo.23466441)

**topology + linguistics.** Persistent homology applied to text, asking
whether a body of writing is structurally exploratory or converging on a
semantic mean.

Each line of a poem (or each document in a corpus) is embedded as a point in
semantic space, and persistent homology measures the shape of the resulting
point cloud across scales: how tightly the points link together (H0) and the
loops they enclose (H1).

- **Phase 0, poetry (current).** Tests whether poetry, through metaphor and
  novel links between distant notions, spreads more widely across semantic
  space than ordinary prose by the same authors, while staying linked.
- **Phase 1, arXiv (planned).** Asks whether academic writing has narrowed
  since generative AI entered common use.

This repository is a public research log as well as code. `backlog/tasks/`
holds the work items and `backlog/docs/` the findings, each dated, so the
trajectory of the project, including results that were later withdrawn, can be
traced. `CLAUDE.md` is the full project overview, and `CONTRIBUTIONS.md`
records who contributed what, including the use of AI assistance.

## Running it

Python 3.12 with [uv](https://docs.astral.sh/uv/):

    uv sync
    uv run python src/collect_poetrydb_corpus.py
    uv run python src/poetry_forms.py
    uv run python src/3_embed_text.py --model nomic

See the Workflow section of `CLAUDE.md` for the full pipeline. Data is not
committed; it is regenerated from the collectors.

## Licence

- **Code** (everything under `src/`, `scratch/` and `.githooks/`, and
  `main.py`): MIT, see `LICENSE`.
- **Writing** (`README.md`, `CLAUDE.md`, `CONTRIBUTIONS.md`, `backlog/`,
  `notebooks/`): Creative Commons Attribution 4.0 International, see
  `LICENSE-CC-BY-4.0.txt`. You may reuse and adapt it with credit to the
  author.

## Citing

Please cite this work as:

> Hong, S. *topoling: persistent homology of semantic structure in text.*
> Zenodo. https://doi.org/10.5281/zenodo.23466441

That DOI always points to the latest version. Each release also has its own:
v0.1.0 (Phase 0 instrument and claim, before testing) is
[10.5281/zenodo.23466442](https://doi.org/10.5281/zenodo.23466442). The same
details are in `CITATION.cff`, which GitHub shows under "Cite this
repository".

Sungyeon Hong, Australian National University.
ORCID: [0000-0002-9897-1205](https://orcid.org/0000-0002-9897-1205)
