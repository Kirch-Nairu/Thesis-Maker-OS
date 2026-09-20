from thesis_os.audit import audit_manuscript


def test_duplicate_and_gap_sections_are_flagged():
    text = """I. Introduction
Text.
II. Framework
Text.
IV. Methodology
Text.
IV. References
Smith, J. (2024). Example.
"""
    audit = audit_manuscript(text)
    codes = {issue["code"] for issue in audit["issues"]}
    assert "SECTION_NUMBER_GAP" in codes
    assert "SECTION_NUMBER_DUPLICATE" in codes


def test_missing_reference_entry_is_blocking():
    text = """I. Introduction
Jeong et al. (2023) reviewed the issue.
II. References
Smith, J. (2024). Example.
"""
    audit = audit_manuscript(text)
    codes = {issue["code"] for issue in audit["issues"]}
    assert "CITATION_MISSING_REFERENCE" in codes
    assert "Jeong (2023)" in audit["citation_audit"]["missing_reference_entries"]


def test_ai_output_is_susceptibility_not_probability():
    text = " ".join([
        "These findings suggest that the program may be relevant to performance.",
        "These studies demonstrate that the intervention may improve performance.",
        "This supports the inclusion of athlete perceptions in the study.",
    ] * 8)
    audit = audit_manuscript(text)
    signal = audit["ai_mediation"]
    assert signal["kind"] == "STYLE_SUSCEPTIBILITY_NOT_AUTHORSHIP_PROBABILITY"
    assert 0 <= signal["score"] <= 100
    assert "probability" in signal["interpretation"].lower()
