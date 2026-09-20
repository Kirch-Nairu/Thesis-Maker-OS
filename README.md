# Thesis Maker OS

**The OS does not write research until it can prove what the research means.**

Thesis Maker OS is a research-engineering control layer for AI-assisted thesis work. It separates evidence, constructs, variables, measurement, analysis, manuscript generation, and review so polished prose cannot hide unresolved research decisions.

The first milestone is intentionally narrow: take a concept paper, expose unresolved research logic, validate a structured research model, and produce a reviewer-readable audit before any rewrite is accepted.

## Authority chain

```text
SOURCE EVIDENCE
      ↓
CLAIM LEDGER
      ↓
CONSTRUCTS / THEORIES
      ↓
VARIABLES / MEASUREMENT
      ↓
ANALYSIS PLAN
      ↓
MANUSCRIPT
      ↓
INDEPENDENT REVIEW
```

Evidence outranks the Writer. The research model outranks prose. Methodology outranks convenience. A reviewer may reject generated text. Missing scientific decisions are surfaced, never silently invented.

## What the bootstrap can do

- Create a governed thesis workspace with registries and review folders.
- Extract text from Markdown/text, with optional PDF and DOCX support.
- Audit unresolved methodology language such as `may include`, `appropriate instrument`, or `to be finalized`.
- Detect duplicated/skipped numbered sections.
- Compare in-text author-year citations with the reference section.
- Flag theory naming inconsistency and weak theory-to-variable traceability through the structured research model.
- Validate predictor/outcome definitions, operationalization, instruments, scoring, measurement scales, and analysis plans.
- Produce an **AI-mediation susceptibility** signal based on writing patterns without pretending it proves AI authorship.
- Emit machine-readable JSON plus a Markdown review report.

## Quick start

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -e ".[dev,pdf,docx]"

thesis-os bootstrap ./my-thesis
thesis-os audit ./paper.pdf --model ./my-thesis/03-RESEARCH-MODEL/research_model.json --out ./audit
thesis-os validate ./my-thesis/03-RESEARCH-MODEL/research_model.json
```

Plain `.md` and `.txt` auditing requires no optional runtime dependency.

## Review semantics

A gate is either `PASS`, `WARN`, or `BLOCK`.

- `PASS`: enough information exists for the next stage.
- `WARN`: the research can proceed, but a reviewer should inspect the issue.
- `BLOCK`: the Writer must not resolve the issue by inventing a research decision.

AI-mediation output is deliberately named **susceptibility**, not probability. It is a writing-pattern diagnostic, not evidence of misconduct.

## Repository map

```text
src/thesis_os/                  executable core
AGENTS.md                       operating rules for AI/code agents
docs/ARCHITECTURE.md            pipeline and gate design
docs/GOVERNANCE.md              role authority and review rules
templates/                      canonical machine-readable templates
examples/tennis-concept-paper/  anonymized bootstrap case
```

## Current milestone

`M0 — RESEARCH MODEL GATE + MANUSCRIPT AUDITOR`

The next milestone should add provider-backed source verification, DOI metadata reconciliation, structured claim extraction, and writer generation constrained by approved claim IDs.
