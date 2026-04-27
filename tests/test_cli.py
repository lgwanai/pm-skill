"""Tests for CLI entry point (FND-01, FND-02, FND-03)."""

from pathlib import Path

import pytest
from typer.testing import CliRunner


def test_cli_help():
    """Test --help shows available commands."""
    from scripts.cli import app

    runner = CliRunner()
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "init" in result.output
    assert "config" in result.output


def test_cli_init(tmp_path, monkeypatch):
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


def test_cli_config_show():
    """Test config command shows settings."""
    from scripts.cli import app

    runner = CliRunner()
    result = runner.invoke(app, ["config"])

    assert result.exit_code == 0
    assert "raw_dir" in result.output.lower()


def test_cli_init_default_path(tmp_path, monkeypatch):
    """Test init command uses default path."""
    from scripts.cli import app

    runner = CliRunner()
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["init"])

    assert result.exit_code == 0
    assert (tmp_path / "knowledge-base" / "raw").exists()