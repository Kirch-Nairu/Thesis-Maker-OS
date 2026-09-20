# Architecture — Research Before Prose

## Design target

Thesis Maker OS is not a text generator with a reviewer prompt attached. It is a sequence of typed research artifacts with admission gates between them.

```text
                     ┌────────────────────┐
                     │  HUMAN AUTHORITY   │
                     └─────────┬──────────┘
                               │ decisions
                               ▼
┌────────┐   ┌──────────┐   ┌───────────┐   ┌───────────┐
│ SOURCE │──▶│ CLAIMS   │──▶│ CONSTRUCT │──▶│ VARIABLES │
└────────┘   │ + SUPPORT│   │ + THEORY  │   │ + MEASURE │
             └──────────┘   └───────────┘   └─────┬─────┘
                                                   │
                                                   ▼
                                            ┌────────────┐
                                            │ ANALYSIS   │
                                            │ PLAN       │
                                            └─────┬──────┘
                                                  │ PASS
                                                  ▼
                                            ┌────────────┐
                                            │ WRITER     │
                                            └─────┬──────┘
                                                  ▼
                 ┌────────────────────────────────────────────┐
                 │ RESEARCH / PEER / CITATION REVIEWERS      │
                 └────────────────────────────────────────────┘
```

## M0 modules

### `ingest.py`
Converts a manuscript to text. Markdown and text are dependency-free; PDF and DOCX are optional adapters.

### `audit.py`
Finds manuscript-level symptoms: unresolved-decision language, section numbering defects, author/year reference drift, theory-name inconsistency, and detector-susceptible style patterns.

### `models.py`
Defines the minimum executable research model. A variable is not considered ready merely because it has a name; construct, operational definition, measurement scale, instrument, and scoring must exist.

### `gates.py`
Turns missing research information into `BLOCK`, `WARN`, or `PASS`. These gates are the main anti-vibe-writing mechanism.

### `report.py`
Produces a human-readable audit surface while preserving JSON for future orchestration.

### `workspace.py`
Creates the canonical seven-layer thesis workspace.

## Why the AI signal is not a detector

Authorship classification is not a reliable foundation for research governance. M0 measures style susceptibility only: repeated synthesis transitions, hedging density, unusually uniform sentence length, and repeated phrase structure. It explicitly does not claim that a score is the probability of AI authorship.

## Planned architecture

M1 should add:

1. DOI/Crossref/OpenAlex or equivalent metadata verification.
2. Source snapshots with immutable IDs and hashes.
3. Claim extraction where every sentence-level literature claim carries source IDs and support level (`DIRECT`, `INDIRECT`, `CONTESTED`, `UNSUPPORTED`).
4. Theory registry with canonical theory identity, seminal sources, constructs, and measured-variable mappings.
5. Instrument registry with validity/reliability evidence and versioned scoring rules.
6. Statistical-plan compiler driven by scale, design, assumptions, multiplicity, and confounding structure.
7. Writer generation restricted to accepted claim IDs.
8. Reviewer diff that traces every challenged sentence back to model/evidence authority.
