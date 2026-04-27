"""Directory initialization logic (FND-03)."""

import sqlite3
from datetime import datetime
from pathlib import Path


def init_knowledge_base(base_path: Path) -> None:
    """Initialize knowledge base directory structure and SQLite index.

    Creates:
    - raw/ directory for imported Markdown files
    - wiki/ directory for compiled knowledge (Phase 2)
    - log/ directory for processing logs
    - index.db SQLite database with documents table

    Args:
        base_path: Root path for knowledge base (typically 'knowledge-base/')
    """
    # Create directories with parents, idempotent
    (base_path / "raw").mkdir(parents=True, exist_ok=True)
    (base_path / "wiki").mkdir(parents=True, exist_ok=True)
    (base_path / "log").mkdir(parents=True, exist_ok=True)

    # Create SQLite index database
    db_path = base_path / "index.db"
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    # Create documents table if not exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id TEXT PRIMARY KEY,
            path TEXT NOT NULL,
            original_path TEXT,
            format TEXT,
            title TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            compiled_at TIMESTAMP,
            status TEXT DEFAULT 'raw',
            hash TEXT
        )
    """)

    # Prepare FTS5 virtual table for Phase 2 (full-text search)
    # Create if not exists - will be used in knowledge compilation
    cursor.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS documents_fts USING fts5(
            id,
            content,
            content='documents',
            content_rowid='rowid'
        )
    """)

    conn.commit()
    conn.close()
