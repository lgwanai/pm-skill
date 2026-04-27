"""Tests for markitdown integration (IMP-04)."""

from pathlib import Path

import pytest

from scripts.importer import import_document


def test_markitdown_integration(tmp_path: Path, sample_pdf: Path) -> None:
    """Test that markitdown is correctly integrated."""
    output_dir = tmp_path / "raw"
    output_dir.mkdir()

    output = import_document(sample_pdf, output_dir)

    assert output.exists()
    content = output.read_text()
    assert len(content) > 0


def test_markitdown_output_filename(tmp_path: Path, sample_pdf: Path) -> None:
    """Test that output filename is source stem + .md."""
    output_dir = tmp_path / "raw"
    output_dir.mkdir()

    output = import_document(sample_pdf, output_dir)

    assert output.name == f"{sample_pdf.stem}.md"


def test_markitdown_format_detection(tmp_path: Path, sample_pdf: Path, sample_docx: Path, sample_html: Path) -> None:
    """Test that markitdown auto-detects formats."""
    output_dir = tmp_path / "raw"
    output_dir.mkdir()

    pdf_out = import_document(sample_pdf, output_dir)
    docx_out = import_document(sample_docx, output_dir)
    html_out = import_document(sample_html, output_dir)

    assert pdf_out.exists()
    assert docx_out.exists()
    assert html_out.exists()
