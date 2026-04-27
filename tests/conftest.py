"""Shared test fixtures for pm-skill tests."""

import pytest
from pathlib import Path
from unittest.mock import MagicMock
from scripts.config import PMSkillConfig, LLMConfig


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


# Phase 2 fixtures for knowledge compilation and retrieval


@pytest.fixture
def mock_anthropic_response() -> MagicMock:
    """Create a mock Anthropic API response with structured wiki content.

    Returns:
        MagicMock with structured content including Overview, Entities,
        Concepts sections with confidence annotations.
    """
    response = MagicMock()
    response.content = [
        MagicMock(
            type="text",
            text="""# Compiled Wiki Page

## Overview
This document describes the user authentication system. [CONFIDENCE: EXTRACTED]

## Entities
- **User**: Represents an authenticated user with credentials. [CONFIDENCE: EXTRACTED]
- **Session**: Manages user login state and expiration. [CONFIDENCE: INFERRED]

## Concepts
- **Authentication**: Process of verifying user identity. [CONFIDENCE: EXTRACTED]
- **Authorization**: Process of checking user permissions. [CONFIDENCE: INFERRED]

## Relations
- User -- authenticates --> Authentication
- User -- has --> Session
- Session -- expires after --> 24 hours [CONFIDENCE: AMBIGUOUS]
""",
        )
    ]
    return response


@pytest.fixture
def sample_raw_markdown() -> str:
    """Provide a sample raw markdown document for compilation testing.

    Returns:
        String containing sample markdown content with various sections.
    """
    return """# User Authentication System

## Introduction
This document outlines the user authentication system for our application.

## Features
- Username/password login
- Session management
- Password reset flow
- Two-factor authentication (optional)

## Technical Details
- Passwords are hashed using bcrypt
- Sessions expire after 24 hours
- Maximum 5 failed login attempts before lockout

## API Endpoints
- POST /auth/login - Authenticate user
- POST /auth/logout - End session
- POST /auth/reset-password - Request password reset
"""


@pytest.fixture
def sample_wiki_page() -> dict:
    """Provide expected wiki page structure for validation.

    Returns:
        Dictionary with expected wiki page fields and structure.
    """
    return {
        "title": "User Authentication System",
        "overview": "This document describes the user authentication system.",
        "entities": [
            {"name": "User", "description": "Represents an authenticated user with credentials.", "confidence": "EXTRACTED"},
            {"name": "Session", "description": "Manages user login state and expiration.", "confidence": "INFERRED"},
        ],
        "concepts": [
            {"name": "Authentication", "description": "Process of verifying user identity.", "confidence": "EXTRACTED"},
            {"name": "Authorization", "description": "Process of checking user permissions.", "confidence": "INFERRED"},
        ],
        "relations": [
            {"source": "User", "relation": "authenticates", "target": "Authentication"},
            {"source": "User", "relation": "has", "target": "Session"},
        ],
        "confidence_annotations": ["EXTRACTED", "INFERRED", "AMBIGUOUS", "UNVERIFIED"],
    }


@pytest.fixture
def temp_wiki_dir(tmp_path: Path) -> dict[str, Path]:
    """Create a temporary wiki/ directory structure for integration tests.

    Returns:
        Dictionary with 'entities', 'concepts', 'index', and 'glossary' paths.
    """
    wiki_dir = tmp_path / "wiki"
    entities_dir = wiki_dir / "entities"
    concepts_dir = wiki_dir / "concepts"

    entities_dir.mkdir(parents=True)
    concepts_dir.mkdir(parents=True)

    return {
        "wiki": wiki_dir,
        "entities": entities_dir,
        "concepts": concepts_dir,
        "index": wiki_dir / "index.md",
        "glossary": wiki_dir / "glossary.md",
    }


@pytest.fixture
def mock_config(tmp_path: Path) -> PMSkillConfig:
    """Provide a mock PMSkillConfig with test settings.

    Returns:
        PMSkillConfig instance with temporary directories.
    """
    return PMSkillConfig(
        raw_dir=tmp_path / "raw",
        wiki_dir=tmp_path / "wiki",
        log_dir=tmp_path / "log",
        llm=LLMConfig(
            model="claude-sonnet-4-6-20250528",
            api_key_env="ANTHROPIC_API_KEY",
        ),
    )
