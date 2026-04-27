"""Tests for CLI entry point (FND-01, FND-02, FND-03, IMP-01 to IMP-06)."""

from pathlib import Path

import pytest
from typer.testing import CliRunner


def test_cli_help() -> None:
    """Test --help shows available commands."""
    from scripts.cli import app

    runner = CliRunner()
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "init" in result.output
    assert "config" in result.output


def test_cli_init(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test init command creates directories."""
    from scripts.cli import app

    runner = CliRunner()
    kb_path = tmp_path / "knowledge-base"

    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["init", "--path", str(kb_path)])

    assert result.exit_code == 0
    assert (kb_path / "raw").exists()
    assert (kb_path / "wiki").exists()
    assert (kb_path / "log").exists()


def test_cli_config_show() -> None:
    """Test config command shows settings."""
    from scripts.cli import app

    runner = CliRunner()
    result = runner.invoke(app, ["config"])

    assert result.exit_code == 0
    assert "raw_dir" in result.output.lower()


def test_cli_init_default_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test init command uses default path."""
    from scripts.cli import app

    runner = CliRunner()
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["init"])

    assert result.exit_code == 0
    assert (tmp_path / "knowledge-base" / "raw").exists()


def test_cli_import_pdf(tmp_path: Path, sample_pdf: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test import command creates raw/sample.md."""
    from scripts.cli import app

    runner = CliRunner()

    # Create knowledge-base structure and config
    kb_path = tmp_path / "knowledge-base"
    (kb_path / "raw").mkdir(parents=True)

    # Create config file pointing to knowledge-base
    config_content = f"""
[paths]
raw_dir = "{kb_path / 'raw'}"
wiki_dir = "{kb_path / 'wiki'}"
log_dir = "{kb_path / 'log'}"
"""
    (tmp_path / ".pm-skill.toml").write_text(config_content)

    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["import", str(sample_pdf)])

    assert result.exit_code == 0
    assert (kb_path / "raw" / f"{sample_pdf.stem}.md").exists()


def test_cli_import_quiet(tmp_path: Path, sample_pdf: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test import --quiet produces minimal output."""
    from scripts.cli import app

    runner = CliRunner()

    kb_path = tmp_path / "knowledge-base"
    (kb_path / "raw").mkdir(parents=True)

    # Create config file
    config_content = f"""
[paths]
raw_dir = "{kb_path / 'raw'}"
wiki_dir = "{kb_path / 'wiki'}"
log_dir = "{kb_path / 'log'}"
"""
    (tmp_path / ".pm-skill.toml").write_text(config_content)

    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["import", str(sample_pdf), "--quiet"])

    assert result.exit_code == 0


def test_cli_import_no_validate(tmp_path: Path, sample_pdf: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test import --no-validate skips validation."""
    from scripts.cli import app

    runner = CliRunner()

    kb_path = tmp_path / "knowledge-base"
    (kb_path / "raw").mkdir(parents=True)

    # Create config file
    config_content = f"""
[paths]
raw_dir = "{kb_path / 'raw'}"
wiki_dir = "{kb_path / 'wiki'}"
log_dir = "{kb_path / 'log'}"
"""
    (tmp_path / ".pm-skill.toml").write_text(config_content)

    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["import", str(sample_pdf), "--no-validate"])

    assert result.exit_code == 0
    assert (kb_path / "raw" / f"{sample_pdf.stem}.md").exists()


def test_cli_import_format(tmp_path: Path, sample_pdf: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test import --format forces format."""
    from scripts.cli import app

    runner = CliRunner()

    kb_path = tmp_path / "knowledge-base"
    (kb_path / "raw").mkdir(parents=True)

    # Create config file
    config_content = f"""
[paths]
raw_dir = "{kb_path / 'raw'}"
wiki_dir = "{kb_path / 'wiki'}"
log_dir = "{kb_path / 'log'}"
"""
    (tmp_path / ".pm-skill.toml").write_text(config_content)

    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["import", str(sample_pdf), "--format", "pdf"])

    assert result.exit_code == 0
    assert (kb_path / "raw" / f"{sample_pdf.stem}.md").exists()
