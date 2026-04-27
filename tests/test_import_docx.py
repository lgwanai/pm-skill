"""Tests for DOCX import (IMP-02)."""

from pathlib import Path

import pytest

from scripts.importer import import_document


def test_import_docx_creates_markdown(tmp_path: Path, sample_docx: Path) -> None:
    """Test that DOCX import creates a Markdown file."""
    output_dir = tmp_path / "raw"
    output_dir.mkdir()

    output = import_document(sample_docx, output_dir)

    assert output.suffix == ".md"
    assert output.exists()


def test_import_docx_content_extracted(tmp_path: Path, sample_docx: Path) -> None:
    """Test that content is extracted from DOCX."""
    output_dir = tmp_path / "raw"
    output_dir.mkdir()

    output = import_document(sample_docx, output_dir)
    content = output.read_text()

    assert len(content) > 0


def test_import_docx_uses_markitdown(tmp_path: Path, sample_docx: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that markitdown is used for conversion."""
    import scripts.importer as imp

    original_convert = imp.MarkItDown.convert
    called = []

    def track_convert(self: imp.MarkItDown, path: str) -> object:
        called.append(path)
        return original_convert(self, path)

    monkeypatch.setattr(imp.MarkItDown, "convert", track_convert)

    output_dir = tmp_path / "raw"
    output_dir.mkdir()
    import_document(sample_docx, output_dir)

    assert len(called) == 1
