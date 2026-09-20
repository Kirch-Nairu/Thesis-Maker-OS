from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Iterable

from .models import ResearchModel, is_unresolved


@dataclass(slots=True)
class Finding:
    severity: str
    code: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass(slots=True)
class GateResult:
    name: str
    status: str
    findings: list[Finding]

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "status": self.status,
            "findings": [finding.to_dict() for finding in self.findings],
        }


def _gate_status(findings: Iterable[Finding]) -> str:
    severities = {finding.severity for finding in findings}
    if "BLOCK" in severities:
        return "BLOCK"
    if "WARN" in severities:
        return "WARN"
    return "PASS"


def _result(name: str, findings: list[Finding]) -> GateResult:
    return GateResult(name=name, status=_gate_status(findings), findings=findings)


def validate_research_model(model: ResearchModel) -> list[GateResult]:
    return [
        _identity_gate(model),
        _variable_gate(model),
        _theory_gate(model),
        _analysis_gate(model),
    ]


def _identity_gate(model: ResearchModel) -> GateResult:
    findings: list[Finding] = []
    for label, value in (
        ("title", model.title),
        ("population", model.population),
        ("research_design", model.research_design),
    ):
        if is_unresolved(value):
            findings.append(Finding("BLOCK", "MODEL_IDENTITY_UNRESOLVED", f"{label} is unresolved"))
    return _result("MODEL_IDENTITY", findings)


def _variable_gate(model: ResearchModel) -> GateResult:
    findings: list[Finding] = []
    if len(model.variables) < 2:
        findings.append(Finding("BLOCK", "VARIABLE_SET_INCOMPLETE", "At least two variables are required"))
        return _result("VARIABLE_OPERATIONALIZATION", findings)

    roles = {v.role.lower().strip() for v in model.variables}
    if not roles.intersection({"predictor", "independent", "exposure"}):
        findings.append(Finding("WARN", "PREDICTOR_ROLE_MISSING", "No predictor/exposure variable is identified"))
    if not roles.intersection({"outcome", "dependent"}):
        findings.append(Finding("BLOCK", "OUTCOME_ROLE_MISSING", "No outcome/dependent variable is identified"))

    seen: set[str] = set()
    for variable in model.variables:
        key = variable.name.casefold().strip()
        if not key:
            findings.append(Finding("BLOCK", "VARIABLE_NAME_MISSING", "A variable has no name"))
            continue
        if key in seen:
            findings.append(Finding("BLOCK", "VARIABLE_DUPLICATE", f"Duplicate variable: {variable.name}"))
        seen.add(key)

        required = {
            "construct": variable.construct,
            "operational_definition": variable.operational_definition,
            "measurement_scale": variable.measurement_scale,
            "instrument": variable.instrument,
            "scoring": variable.scoring,
        }
        for field_name, value in required.items():
            if is_unresolved(value):
                findings.append(
                    Finding(
                        "BLOCK",
                        "VARIABLE_UNRESOLVED",
                        f"{variable.name}: {field_name} is unresolved",
                    )
                )
        if variable.status.lower() != "resolved":
            findings.append(Finding("BLOCK", "VARIABLE_STATUS", f"{variable.name}: status is not resolved"))

    return _result("VARIABLE_OPERATIONALIZATION", findings)


def _theory_gate(model: ResearchModel) -> GateResult:
    findings: list[Finding] = []
    variable_names = {v.name.casefold().strip() for v in model.variables}

    if not model.theory_links:
        findings.append(Finding("WARN", "THEORY_LINKS_EMPTY", "No theory-to-variable links are declared"))
        return _result("THEORY_TRACEABILITY", findings)

    for link in model.theory_links:
        if is_unresolved(link.theory) or is_unresolved(link.construct):
            findings.append(Finding("BLOCK", "THEORY_UNRESOLVED", "A theory link has unresolved theory/construct"))
        if link.variable.casefold().strip() not in variable_names:
            findings.append(
                Finding("BLOCK", "THEORY_VARIABLE_MISSING", f"Theory link targets unknown variable: {link.variable}")
            )
        if not link.evidence_ids:
            findings.append(
                Finding("BLOCK", "THEORY_EVIDENCE_MISSING", f"{link.theory}: no evidence source IDs declared")
            )
        if link.status.lower() != "resolved":
            findings.append(Finding("BLOCK", "THEORY_STATUS", f"{link.theory}: traceability is unresolved"))

    return _result("THEORY_TRACEABILITY", findings)


def _analysis_gate(model: ResearchModel) -> GateResult:
    findings: list[Finding] = []
    variable_names = {v.name.casefold().strip(): v for v in model.variables}

    if not model.planned_tests:
        findings.append(Finding("BLOCK", "ANALYSIS_PLAN_EMPTY", "No inferential/statistical tests are declared"))
        return _result("ANALYSIS_PLAN", findings)

    for test in model.planned_tests:
        if is_unresolved(test.test) or test.status.lower() != "resolved":
            findings.append(Finding("BLOCK", "TEST_UNRESOLVED", f"Planned test is unresolved: {test.test or '<unnamed>'}"))
        if len(test.variables) < 2:
            findings.append(Finding("BLOCK", "TEST_VARIABLES_INCOMPLETE", f"{test.test}: fewer than two variables"))
        for variable in test.variables:
            if variable.casefold().strip() not in variable_names:
                findings.append(Finding("BLOCK", "TEST_UNKNOWN_VARIABLE", f"{test.test}: unknown variable {variable}"))
        if is_unresolved(test.rationale):
            findings.append(Finding("BLOCK", "TEST_RATIONALE_MISSING", f"{test.test}: rationale is unresolved"))
        if not test.assumptions:
            findings.append(Finding("WARN", "TEST_ASSUMPTIONS_EMPTY", f"{test.test}: assumptions are not declared"))

    return _result("ANALYSIS_PLAN", findings)
