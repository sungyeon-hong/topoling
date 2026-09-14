# Glossary

Terms used across topoling's code and notes, written out so they do not have to
be inferred. Topological terms first, then this project's own vocabulary.

## Topological data analysis

**Point cloud** — a set of points in some space. Here, each point is one line of
a poem, represented by its embedding vector. A poem becomes a cloud of as many
points as it has lines.

**Embedding** — a text turned into a list of numbers (768 of them, for the
models used here) such that texts with similar meaning land near each other.

**L2 normalisation** — scaling every vector to length 1, so all points sit on
the surface of a sphere. The reason this project does it: once points are on the
unit sphere, ordinary straight-line distance becomes a direct function of cosine
similarity, so distances mean the same thing across different poems and corpora
with no further rescaling. All distances then fall in [0, 2].

**Filtration** — the process of growing a ball of radius *r* around every point,
starting at *r* = 0 and expanding. Features appear and disappear as *r* grows,
and persistent homology is the record of when.

**Vietoris–Rips complex** (usually just "Rips") — the shape built at each radius
by connecting every pair of points closer than *r*. It is built from a *set* of
points, which is why it is **permutation-invariant**: reordering the points
changes nothing at all. This is why shuffling a poem's lines is not a usable
control, and why a sonnet's volta cannot be located by position.

**H0** — connected components. An H0 feature is a cluster; the H0 diagram
records when separate clusters merge into one as *r* grows. Informally, H0
measures how spread out or clumped the cloud is.

**H1** — loops. An H1 feature is a hole, a ring of points enclosing empty space
that exists over some range of radii before filling in. This is what would
detect a "homogenisation loop". In the first Phase 0 run, H1 showed nothing.

**Persistence** — how long a feature survives as *r* grows: its death radius
minus its birth radius. Long-lived features are usually called real structure,
short-lived ones noise.

**Persistence diagram** — the list of (birth, death) pairs for all features.
**Bar life** is one feature's persistence; **total persistence** is the sum over
all of them.

**Zero-persistence bar** — a feature born and killed at the same radius. Exactly
coincident points produce these, and **ripser discards them silently**. This is
why verbatim repeated lines are invisible to this pipeline.

**ripser** — the library that computes persistence diagrams. **gudhi** and
**persim** are declared dependencies that nothing currently uses.

**Persistence image** — a way of turning a diagram into a fixed-size grid of
numbers so diagrams can be compared statistically. Planned, not yet implemented.

## This project's vocabulary

**Phase 0** — the poetry stage. Instrument validation: establish that the method
detects known structure in human writing at all, before trusting it on anything
subtle. Poetry is used because fixed forms supply ground truth.

**Phase 1** — the arXiv stage. Apply the validated instrument to academic
abstracts over historical time.

**Corpus-level vs document-level** — two different measurements that must not be
conflated. *Corpus-level* treats one whole document as one point and a year's
worth of documents as the cloud; it measures diversity *between* documents, and
the homogenisation claim lives there. *Document-level* treats one line or
sentence as a point and a single document as the cloud; it measures internal
structure, and Phase 0 poetry lives there.

**H1 point floor** — the rule that no document-level H1 claim is made on a cloud
smaller than about 25 points, because loops found among a handful of points in
768 dimensions are sampling noise. Note it applies to *distinct* points: repeated
lines collapse, so raw line count overstates what the method sees. No sonnet can
clear it, since a sonnet is 14 lines.

**The four arms** — the Phase 0 comparison groups. `sonnet` (fixed 14 lines,
volta), `refrain_song` (a chorus recurring verbatim), `ballad_stanza` (regular
four-line stanzas, no refrain), `irregular` (no regular structure). A fifth,
villanelle, was intended but does not exist in PoetryDB.

**Corpus control** — the nuisance calibration actually used: the same number of
real verse lines drawn at random from *other* poems. It holds the embedding
model's geometry fixed and destroys only the poem's own coherence, answering
"is this poem different from an arbitrary bag of verse the same size?"

**Excess** — a poem's statistic minus the mean of its matched corpus controls.
Negative excess bar life means the poem's lines sit closer together than
arbitrary verse, i.e. the poem is coherent.

**Wrap fragment** — an indented remnant left by PoetryDB breaking a long line
across entries, such as `"  the"`. Not a line of verse; filtered out before
embedding.

**Displacement** — in the refrain sensitivity experiment, how far a repeated
refrain is moved in embedding space to simulate paraphrase. For scale, unrelated
verse lines sit about 0.80 apart.

## Abbreviations seen in sibling projects

**TDA** — topological data analysis, the field this project draws on.
**PH** — persistent homology. **T2I / I2T** — text-to-image and image-to-text,
`panic-tda` vocabulary, not used here. **AC** — acceptance criteria, the
checklist at the end of a backlog task.
