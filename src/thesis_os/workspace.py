from __future__ import annotations

from pathlib import Path
import json


DIRECTORIES = [
    "00-SOURCE",
    "01-AUDIT",
    "02-EVIDENCE",
    "03-RESEARCH-MODEL",
    "04-METHODOLOGY",
    "05-MANUSCRIPT",
    "06-REVIEWS",
]


DEFAULT_MODEL = {
    "title": "TBD",
    "population": "TBD",
    "research_design": "TBD",
    "variables": [
        {
            "name": "Predictor / exposure",
            "role": "predictor",
            "construct": "TBD",
            "operational_definition": "TBD",
            "measurement_scale": "TBD",
            "instrument": "TBD",
            "scoring": "TBD",
            "status": "unresolved",
        },
        {
            "name": "Outcome",
            "role": "outcome",
            "construct": "TBD",
            "operational_definition": "TBD",
            "measurement_scale": "TBD",
            "instrument": "TBD",
            "scoring": "TBD",
            "status": "unresolved",
        },
    ],
    "theory_links": [],
    "planned_tests": [],
    "confounders": [],
    "authority_notes": [],
}


def bootstrap_workspace(root: str | Path) -> list[Path]:
    root = Path(root)
    created: list[Path] = []
    root.mkdir(parents=True, exist_ok=True)
    for directory in DIRECTORIES:
        path = root / directory
        path.mkdir(exist_ok=True)
        created.append(path)

    model_path = root / "03-RESEARCH-MODEL" / "research_model.json"
    if not model_path.exists():
        model_path.write_text(json.dumps(DEFAULT_MODEL, indent=2) + "\n", encoding="utf-8")
        created.append(model_path)

    ledger_path = root / "02-EVIDENCE" / "claim_evidence_ledger.json"
    if not ledger_path.exists():
        ledger_path.write_text("[]\n", encoding="utf-8")
        created.append(ledger_path)

    readme_path = root / "README.md"
    if not readme_path.exists():
        readme_path.write_text(
            "# Governed Thesis Workspace\n\n"
            "Do not write around BLOCK gates. Resolve research decisions in the model first.\n",
            encoding="utf-8",
        )
        created.append(readme_path)

    return created
