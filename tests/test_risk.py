from underwriting.agents.risk import score_facts
from underwriting.fixtures import APP_1001, APP_1003, enrichment_for


def test_app_1001_score_13_band_low():
    result = score_facts(enrichment_for(APP_1001))
    assert result["score"] == 13
    assert result["band"] == "low"
    assert result["factors"] == ["base", "credit excellent"]
    assert result["hard_refer"] == []


def test_app_1003_score_and_band():
    result = score_facts(enrichment_for(APP_1003))
    assert result["score"] == 100
    assert result["band"] == "severe"
