"""Shared test fixtures for pm-skill tests."""

import pytest
from pathlib import Path


@pytest.fixture
def temp_knowledge_base(tmp_path: Path) -> dict[str, Path]:
    """Create temporary knowledge base directory structure.

    Returns:
        dict with 'raw', 'wiki', 'log' Path entries
    """
    kb_dir = tmp_path / "knowledge-base"
    raw_dir = kb_dir / "raw"
    wiki_dir = kb_dir / "wiki"
    log_dir = kb_dir / "log"

    raw_dir.mkdir(parents=True)
    wiki_dir.mkdir(parents=True)
    log_dir.mkdir(parents=True)

    return {
        "root": kb_dir,
        "raw": raw_dir,
        "wiki": wiki_dir,
        "log": log_dir,
    }


@pytest.fixture
def sample_pdf() -> Path:
    """Return path to sample PDF fixture.

    Returns:
        Path to tests/fixtures/sample.pdf
    """
    return Path(__file__).parent / "fixtures" / "sample.pdf"


@pytest.fixture
def sample_docx() -> Path:
    """Return path to sample DOCX fixture.

    Returns:
        Path to tests/fixtures/sample.docx
    """
    return Path(__file__).parent / "fixtures" / "sample.docx"


@pytest.fixture
def sample_html() -> Path:
    """Return path to sample HTML fixture.

    Returns:
        Path to tests/fixtures/sample.html
    """
    return Path(__file__).parent / "fixtures" / "sample.html"


@pytest.fixture
def temp_config_file(tmp_path: Path) -> Path:
    """Create temporary config file.

    Returns:
        Path to temporary .pm-skill.toml
    """
    config_content = """
[paths]
raw_dir = "raw"
wiki_dir = "wiki"
log_dir = "log"

[llm]
model = "claude-3-sonnet"
api_key_env = "ANTHROPIC_API_KEY"
"""
    config_path = tmp_path / ".pm-skill.toml"
    config_path.write_text(config_content)
    return config_path
