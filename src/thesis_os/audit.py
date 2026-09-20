from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, asdict
import re
import statistics


ROMAN_VALUES = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100}

UNRESOLVED_PATTERNS = {
    "UNRESOLVED_MAY_INCLUDE": r"\bmay include\b",
    "UNRESOLVED_MAY_BE_USED": r"\bmay be used\b",
    "UNRESOLVED_MAY_BE_CONSIDERED": r"\bmay be considered\b",
    "UNRESOLVED_APPROPRIATE": r"\bappropriate (?:instrument|measure|test|assessment|method)s?\b",
    "UNRESOLVED_FINALIZE": r"\b(?:final|exact) .{0,40}\b(?:finalized|approved|confirmed)\b",
    "UNRESOLVED_ADVISER": r"\b(?:research )?adviser\b",
    "UNRESOLVED_TBD": r"\b(?:TBD|TODO|to be determined|to be finalized|to be confirmed)\b",
}

SYNTHESIS_STEMS = (
    "these findings",
    "these studies",
    "this supports",
    "this shows",
    "together, these",
    "furthermore",
    "therefore",
    "existing literature",
    "the findings may",
    "the study may",
)


@dataclass(slots=True)
class AuditIssue:
    severity: str
    code: str
    message: str
    line: int | None = None
    excerpt: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)


def _roman_to_int(token: str) -> int:
    total = 0
    previous = 0
    for char in reversed(token):
        value = ROMAN_VALUES.get(char, 0)
        if value < previous:
            total -= value
        else:
            total += value
            previous = value
    return total


def audit_manuscript(text: str) -> dict:
    issues: list[AuditIssue] = []
    lines = text.splitlines()
    issues.extend(_audit_unresolved(lines))
    issues.extend(_audit_sections(lines))
    citation_report, citation_issues = _audit_citations(text)
    issues.extend(citation_issues)
    issues.extend(_audit_theory_language(text))
    mediation = _ai_mediation_susceptibility(text)

    counts = Counter(issue.severity for issue in issues)
    return {
        "summary": {
            "blocking": counts.get("BLOCK", 0),
            "warnings": counts.get("WARN", 0),
            "notes": counts.get("NOTE", 0),
        },
        "issues": [issue.to_dict() for issue in issues],
        "citation_audit": citation_report,
        "ai_mediation": mediation,
    }


def _audit_unresolved(lines: list[str]) -> list[AuditIssue]:
    issues: list[AuditIssue] = []
    for lineno, line in enumerate(lines, start=1):
        for code, pattern in UNRESOLVED_PATTERNS.items():
            if re.search(pattern, line, flags=re.IGNORECASE):
                severity = "BLOCK" if code in {
                    "UNRESOLVED_APPROPRIATE", "UNRESOLVED_FINALIZE", "UNRESOLVED_TBD"
                } else "WARN"
                issues.append(
                    AuditIssue(
                        severity,
                        code,
                        "Potential unresolved research decision is expressed as manuscript prose",
                        lineno,
                        line.strip()[:240],
                    )
                )
    return issues


def _audit_sections(lines: list[str]) -> list[AuditIssue]:
    headings: list[tuple[int, int, str]] = []
    pattern = re.compile(r"^\s*([IVXLCDM]+)\.\s+(.+)$")
    for lineno, line in enumerate(lines, start=1):
        match = pattern.match(line)
        if match:
            headings.append((lineno, _roman_to_int(match.group(1)), match.group(2).strip()))

    issues: list[AuditIssue] = []
    if len(headings) < 2:
        return issues

    seen: dict[int, int] = {}
    previous: int | None = None
    for lineno, number, title in headings:
        if number in seen:
            issues.append(
                AuditIssue(
                    "WARN",
                    "SECTION_NUMBER_DUPLICATE",
                    f"Section {number} is duplicated; first seen on line {seen[number]}",
                    lineno,
                    title,
                )
            )
        else:
            seen[number] = lineno
        if previous is not None and number > previous + 1:
            issues.append(
                AuditIssue(
                    "WARN",
                    "SECTION_NUMBER_GAP",
                    f"Section numbering jumps from {previous} to {number}",
                    lineno,
                    title,
                )
            )
        previous = number
    return issues


def _audit_citations(text: str) -> tuple[dict, list[AuditIssue]]:
    split = re.split(r"(?im)^\s*(?:[IVXLCDM]+\.\s+)?references\s*$", text, maxsplit=1)
    body = split[0]
    references = split[1] if len(split) == 2 else ""

    citations: set[tuple[str, str]] = set()
    for match in re.finditer(r"\b([A-Z][A-Za-z'’-]+)(?:\s+et\s+al\.|\s+and\s+[A-Z][A-Za-z'’-]+)?\s*\((20\d{2}|19\d{2})\)", body):
        citations.add((match.group(1).casefold(), match.group(2)))
    for match in re.finditer(r"\(([A-Z][A-Za-z'’-]+)(?:\s+et\s+al\.|\s*&[^,]+)?,\s*(20\d{2}|19\d{2})\)", body):
        citations.add((match.group(1).casefold(), match.group(2)))

    ref_keys: set[tuple[str, str]] = set()
    for match in re.finditer(r"(?m)^\s*([A-Z][A-Za-z'’-]+),.*?\((20\d{2}|19\d{2})\)", references):
        ref_keys.add((match.group(1).casefold(), match.group(2)))

    missing = sorted(citations - ref_keys)
    uncited = sorted(ref_keys - citations)
    issues = [
        AuditIssue(
            "BLOCK",
            "CITATION_MISSING_REFERENCE",
            f"In-text citation has no matching first-author/year reference: {author.title()} ({year})",
        )
        for author, year in missing
    ]
    issues.extend(
        AuditIssue(
            "NOTE",
            "REFERENCE_NOT_CITED",
            f"Reference entry was not matched to an in-text citation: {author.title()} ({year})",
        )
        for author, year in uncited
    )

    return {
        "in_text_count": len(citations),
        "reference_count": len(ref_keys),
        "missing_reference_entries": [f"{a.title()} ({y})" for a, y in missing],
        "unmatched_reference_entries": [f"{a.title()} ({y})" for a, y in uncited],
        "reference_section_found": bool(references.strip()),
    }, issues


def _audit_theory_language(text: str) -> list[AuditIssue]:
    issues: list[AuditIssue] = []
    lower = text.casefold()
    if "achievement goal theory" in lower and "goal setting theory" in lower:
        issues.append(
            AuditIssue(
                "WARN",
                "THEORY_NAMING_INCONSISTENCY",
                "Both Achievement Goal Theory and Goal Setting Theory appear. Verify that distinct theories are not being used interchangeably.",
            )
        )
    return issues


def _sentences(text: str) -> list[str]:
    cleaned = re.sub(r"\s+", " ", text).strip()
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", cleaned) if len(s.split()) >= 4]


def _ai_mediation_susceptibility(text: str) -> dict:
    """Return a style-risk signal, not an AI authorship probability."""
    lower = text.casefold()
    sentences = _sentences(text)
    words = re.findall(r"\b[a-zA-Z][a-zA-Z'-]*\b", lower)

    transition_hits = sum(lower.count(stem) for stem in SYNTHESIS_STEMS)
    transition_density = transition_hits / max(len(sentences), 1)

    hedge_terms = re.findall(r"\b(?:may|might|could|generally|appropriate|relevant)\b", lower)
    hedge_density = len(hedge_terms) / max(len(words), 1)

    lengths = [len(sentence.split()) for sentence in sentences]
    if len(lengths) >= 2 and statistics.mean(lengths) > 0:
        cv = statistics.pstdev(lengths) / statistics.mean(lengths)
        uniformity = max(0.0, 1.0 - min(cv / 0.65, 1.0))
    else:
        uniformity = 0.0

    trigrams = [tuple(words[i:i + 3]) for i in range(max(0, len(words) - 2))]
    if trigrams:
        counts = Counter(trigrams)
        repeated = sum(count - 1 for count in counts.values() if count > 1)
        repetition = repeated / len(trigrams)
    else:
        repetition = 0.0

    score = 100 * (
        0.35 * min(transition_density / 0.22, 1.0)
        + 0.20 * min(hedge_density / 0.025, 1.0)
        + 0.25 * uniformity
        + 0.20 * min(repetition / 0.06, 1.0)
    )
    score = int(round(max(0.0, min(score, 100.0))))
    if score >= 65:
        band = "HIGH"
    elif score >= 40:
        band = "MODERATE"
    else:
        band = "LOW"

    return {
        "kind": "STYLE_SUSCEPTIBILITY_NOT_AUTHORSHIP_PROBABILITY",
        "score": score,
        "band": band,
        "signals": {
            "repeated_synthesis_transition_density": round(transition_density, 4),
            "hedging_density": round(hedge_density, 4),
            "sentence_length_uniformity": round(uniformity, 4),
            "repeated_trigram_ratio": round(repetition, 4),
        },
        "interpretation": (
            "Higher values mean the prose contains more patterns that commonly trigger detector-style scrutiny. "
            "The score is not an AI-authorship probability and does not establish who or what authored the text."
        ),
    }
