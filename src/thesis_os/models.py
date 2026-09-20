from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
import json


UNRESOLVED_MARKERS = (
    "tbd",
    "todo",
    "to be determined",
    "to be finalized",
    "to be confirmed",
    "depending on adviser",
    "depending on the adviser",
    "appropriate instrument",
    "appropriate measure",
    "may include",
    "may be used",
    "may be considered",
)


def is_unresolved(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        normalized = " ".join(value.lower().split())
        return not normalized or any(marker in normalized for marker in UNRESOLVED_MARKERS)
    if isinstance(value, (list, tuple, dict)):
        return len(value) == 0
    return False


@dataclass(slots=True)
class Variable:
    name: str
    role: str
    construct: str = ""
    operational_definition: str = ""
    measurement_scale: str = ""
    instrument: str = ""
    scoring: str = ""
    status: str = "unresolved"

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Variable":
        allowed = {field_name for field_name in cls.__dataclass_fields__}
        return cls(**{k: data.get(k, "") for k in allowed})


@dataclass(slots=True)
class TheoryLink:
    theory: str
    construct: str
    variable: str
    evidence_ids: list[str] = field(default_factory=list)
    status: str = "unresolved"

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TheoryLink":
        return cls(
            theory=str(data.get("theory", "")),
            construct=str(data.get("construct", "")),
            variable=str(data.get("variable", "")),
            evidence_ids=list(data.get("evidence_ids", [])),
            status=str(data.get("status", "unresolved")),
        )


@dataclass(slots=True)
class PlannedTest:
    test: str
    variables: list[str] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)
    rationale: str = ""
    status: str = "unresolved"

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PlannedTest":
        return cls(
            test=str(data.get("test", "")),
            variables=list(data.get("variables", [])),
            assumptions=list(data.get("assumptions", [])),
            rationale=str(data.get("rationale", "")),
            status=str(data.get("status", "unresolved")),
        )


@dataclass(slots=True)
class ResearchModel:
    title: str
    population: str
    research_design: str
    variables: list[Variable] = field(default_factory=list)
    theory_links: list[TheoryLink] = field(default_factory=list)
    planned_tests: list[PlannedTest] = field(default_factory=list)
    confounders: list[str] = field(default_factory=list)
    authority_notes: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ResearchModel":
        return cls(
            title=str(data.get("title", "")),
            population=str(data.get("population", "")),
            research_design=str(data.get("research_design", "")),
            variables=[Variable.from_dict(x) for x in data.get("variables", [])],
            theory_links=[TheoryLink.from_dict(x) for x in data.get("theory_links", [])],
            planned_tests=[PlannedTest.from_dict(x) for x in data.get("planned_tests", [])],
            confounders=list(data.get("confounders", [])),
            authority_notes=list(data.get("authority_notes", [])),
        )


def load_research_model(path: str | Path) -> ResearchModel:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Research model must be a JSON object")
    return ResearchModel.from_dict(payload)
