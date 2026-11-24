from global_economic_news_intelligence.cli import main


def test_cli_version(capsys, monkeypatch) -> None:
    monkeypatch.setattr("sys.argv", ["geni", "version"])
    assert main() == 0
    assert capsys.readouterr().out.strip() == "0.1.0"


def test_cli_readiness_discloses_disabled_capabilities(capsys, monkeypatch) -> None:
    monkeypatch.setattr("sys.argv", ["geni", "readiness"])
    assert main() == 0
    output = capsys.readouterr().out
    assert "disabled" in output
    assert "docs/16-implementation-readiness-and-release-gates.md" in output
