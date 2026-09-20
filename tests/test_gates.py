from thesis_os.gates import validate_research_model
from thesis_os.models import ResearchModel


def test_unresolved_model_blocks():
    model = ResearchModel.from_dict({
        "title": "Example",
        "population": "Students",
        "research_design": "correlational",
        "variables": [
            {
                "name": "Exposure",
                "role": "predictor",
                "construct": "TBD",
                "operational_definition": "TBD",
                "measurement_scale": "TBD",
                "instrument": "TBD",
                "scoring": "TBD",
                "status": "unresolved"
            },
            {
                "name": "Outcome",
                "role": "outcome",
                "construct": "Performance",
                "operational_definition": "Measured score",
                "measurement_scale": "ratio",
                "instrument": "standard test",
                "scoring": "raw score",
                "status": "resolved"
            }
        ],
        "planned_tests": []
    })
    gates = validate_research_model(model)
    assert any(g.status == "BLOCK" for g in gates)
    codes = {f.code for g in gates for f in g.findings}
    assert "VARIABLE_UNRESOLVED" in codes
    assert "ANALYSIS_PLAN_EMPTY" in codes


def test_resolved_minimum_model_has_no_block():
    model = ResearchModel.from_dict({
        "title": "Exposure and performance",
        "population": "Students",
        "research_design": "cross-sectional correlational",
        "variables": [
            {
                "name": "Exposure",
                "role": "predictor",
                "construct": "Weekly exposure",
                "operational_definition": "Minutes per week over prior four weeks",
                "measurement_scale": "ratio",
                "instrument": "training log",
                "scoring": "sum weekly minutes",
                "status": "resolved"
            },
            {
                "name": "Outcome",
                "role": "outcome",
                "construct": "Performance",
                "operational_definition": "Mean velocity across three valid trials",
                "measurement_scale": "ratio",
                "instrument": "calibrated radar device",
                "scoring": "km/h mean",
                "status": "resolved"
            }
        ],
        "theory_links": [],
        "planned_tests": [
            {
                "test": "Pearson correlation",
                "variables": ["Exposure", "Outcome"],
                "assumptions": ["linearity", "no influential outliers", "bivariate normality for inference"],
                "rationale": "Both variables are continuous ratio measures and the inferential target is linear association.",
                "status": "resolved"
            }
        ]
    })
    gates = validate_research_model(model)
    assert not any(g.status == "BLOCK" for g in gates)
