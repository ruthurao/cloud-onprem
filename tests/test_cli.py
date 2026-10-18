from underwriting.__main__ import main


def test_cli_prints_rule_score_and_rationale(monkeypatch, capsys):
    monkeypatch.setenv("LLM_PROVIDER", "ollama")
    monkeypatch.setattr(
        "underwriting.__main__.complete",
        lambda prompt, provider: '{"rationale": "Clear history and excellent credit."}',
    )
    assert main(["APP-1001"]) == 0
    out = capsys.readouterr().out
    assert "application: APP-1001" in out
    assert "name: Alice Chen" in out
    assert "product: homeowners" in out
    assert "score: 13" in out
    assert "band: low" in out
    assert 'factors: ["base", "credit excellent"]' in out
    assert "hard_refer: []" in out
    assert "rationale: Clear history and excellent credit." in out
    assert "quality_miss" not in out


def test_cli_reports_quality_miss_without_changing_score(monkeypatch, capsys):
    monkeypatch.setattr(
        "underwriting.__main__.complete",
        lambda prompt, provider: "I think the score should be 40.",
    )
    assert main(["APP-1001"]) == 0
    out = capsys.readouterr().out
    assert "score: 13" in out
    assert "band: low" in out
    assert "quality miss" in out
    assert "quality_miss: true" in out
