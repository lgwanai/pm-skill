"""Tests for raw/ storage (IMP-05)."""

from pathlib import Path

import pytest

from scripts.config import load_config
from scripts.importer import import_batch, import_document


def test_markdown_saved_to_raw(tmp_path: Path, sample_pdf: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that Markdown files are saved to raw/ directory from config."""
    # Create a config file in tmp_path
    config_content = """
[paths]
raw_dir = "knowledge-base/raw"
wiki_dir = "knowledge-base/wiki"
log_dir = "knowledge-base/log"
"""
    config_file = tmp_path / ".pm-skill.toml"
    config_file.write_text(config_content)

    # Create knowledge-base directory
    (tmp_path / "knowledge-base" / "raw").mkdir(parents=True)

    monkeypatch.chdir(tmp_path)
    config = load_config()
    output = import_document(sample_pdf, config.raw_dir)

    assert output.parent.name == "raw"


def test_markdown_filename_conversion(tmp_path: Path, sample_pdf: Path) -> None:
    """Test that output filename is source stem + .md."""
    output_dir = tmp_path / "raw"
    output_dir.mkdir()

    output = import_document(sample_pdf, output_dir)

    assert output.name == f"{sample_pdf.stem}.md"


def test_markdown_encoding(tmp_path: Path, sample_pdf: Path) -> None:
    """Test UTF-8 write."""
    output_dir = tmp_path / "raw"
    output_dir.mkdir()

    output = import_document(sample_pdf, output_dir)

    # Should not raise UnicodeDecodeError
    content = output.read_text(encoding="utf-8")
    assert isinstance(content, str)


def test_batch_import_processes_multiple(
    tmp_path: Path,
    sample_pdf: Path,
    sample_docx: Path,
    sample_html: Path,
) -> None:
    """Test that batch import processes multiple files."""
    output_dir = tmp_path / "raw"
    output_dir.mkdir()

    success, failures = import_batch(
        [sample_pdf, sample_docx, sample_html],
        output_dir,
    )

    assert success == 3
    assert failures == 0


def test_batch_import_logs_failures(tmp_path: Path, sample_pdf: Path) -> None:
    """Test that batch import logs failures."""
    output_dir = tmp_path / "raw"
    log_dir = tmp_path / "log"
    output_dir.mkdir()
    log_dir.mkdir()

    # Create a file that will fail
    bad_file = tmp_path / "bad.txt"
    bad_file.write_text("not a document")

    success, failures = import_batch(
        [sample_pdf, bad_file],
        output_dir,
        log_dir=log_dir,
    )

    assert success >= 1  # PDF should succeed
    assert failures >= 1  # Bad file should fail

    # Check log file was created
    log_files = list(log_dir.glob("import-*.log"))
    assert len(log_files) == 1
