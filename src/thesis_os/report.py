from __future__ import annotations

from .gates import GateResult


def render_markdown(audit: dict, gates: list[GateResult] | None = None) -> str:
    summary = audit["summary"]
    mediation = audit["ai_mediation"]
    lines = [
        "# Thesis Maker OS — Audit Report",
        "",
        "## Decision surface",
        "",
        f"- Blocking manuscript findings: **{summary['blocking']}**",
        f"- Warnings: **{summary['warnings']}**",
        f"- Notes: **{summary['notes']}**",
        f"- AI-mediation susceptibility: **{mediation['band']} ({mediation['score']}/100)**",
        "",
        "> The AI-mediation score is a style-susceptibility diagnostic, not an authorship probability or misconduct finding.",
        "",
    ]

    if gates is not None:
        lines.extend(["## Research-model gates", ""])
        for gate in gates:
            lines.append(f"### {gate.status} — {gate.name}")
            if not gate.findings:
                lines.append("No blocking or warning findings.")
            else:
                for finding in gate.findings:
                    lines.append(f"- **{finding.severity} / {finding.code}:** {finding.message}")
            lines.append("")

    lines.extend(["## Manuscript findings", ""])
    if not audit["issues"]:
        lines.append("No heuristic manuscript findings.")
    else:
        for issue in audit["issues"]:
            location = f" line {issue['line']}" if issue.get("line") else ""
            lines.append(f"- **{issue['severity']} / {issue['code']}**{location}: {issue['message']}")
            if issue.get("excerpt"):
                lines.append(f"  - `{issue['excerpt']}`")

    citation = audit["citation_audit"]
    lines.extend([
        "",
        "## Citation parity",
        "",
        f"- In-text author/year keys: {citation['in_text_count']}",
        f"- Reference author/year keys: {citation['reference_count']}",
        f"- Reference section found: {citation['reference_section_found']}",
    ])
    if citation["missing_reference_entries"]:
        lines.append("- Missing reference entries: " + ", ".join(citation["missing_reference_entries"]))
    if citation["unmatched_reference_entries"]:
        lines.append("- Unmatched reference entries: " + ", ".join(citation["unmatched_reference_entries"]))

    lines.extend(["", "## AI-mediation signals", ""])
    for name, value in mediation["signals"].items():
        lines.append(f"- {name}: `{value}`")
    lines.extend(["", mediation["interpretation"], ""])
    return "\n".join(lines)
