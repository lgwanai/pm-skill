"""Tests for directory initialization (FND-03)."""

import sqlite3
from pathlib import Path

import pytest


def test_init_creates_directories(tmp_path):
    """Test raw/wiki/log creation."""
    from scripts.utils.init import init_knowledge_base

    init_knowledge_base(tmp_path)
    assert (tmp_path / "raw").is_dir()
    assert (tmp_path / "wiki").is_dir()
    assert (tmp_path / "log").is_dir()


def test_init_creates_index_db(tmp_path):
    """Test SQLite index creation."""
    from scripts.utils.init import init_knowledge_base

    init_knowledge_base(tmp_path)
    db_path = tmp_path / "index.db"
    assert db_path.exists()

    # Verify it's a valid SQLite database
    conn = sqlite3.connect(str(db_path))
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = {row[0] for row in cursor.fetchall()}
    conn.close()

    assert "documents" in tables


def test_init_idempotent(tmp_path):
    """Running init twice should not error."""
    from scripts.utils.init import init_knowledge_base

    init_knowledge_base(tmp_path)
    init_knowledge_base(tmp_path)  # Should not raise
    assert (tmp_path / "raw").exists()


def test_init_creates_documents_table(tmp_path):
    """Test documents table has correct schema."""
    from scripts.utils.init import init_knowledge_base

    init_knowledge_base(tmp_path)
    conn = sqlite3.connect(str(tmp_path / "index.db"))

    # Check columns exist
    cursor = conn.execute("PRAGMA table_info(documents)")
    columns = {row[1] for row in cursor.fetchall()}
    conn.close()

    assert "id" in columns
    assert "path" in columns
    assert "hash" in columns
    assert "created_at" in columns
