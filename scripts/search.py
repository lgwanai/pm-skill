"""FTS5 search functionality for wiki knowledge base.

This module provides full-text search capabilities using SQLite FTS5:
- init_fts5_table: Create the wiki_search virtual table
- index_wiki_page: Add/update a page in the search index
- search_wiki: Search the wiki with BM25 ranking

The FTS5 index enables fast keyword search across all compiled wiki pages.
"""

import logging
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)


def init_fts5_table(db_path: Path) -> None:
    """Initialize the FTS5 virtual table for wiki search.

    Creates the wiki_search virtual table with:
    - path: File path relative to wiki root
    - title: Page title
    - content: Full page content
    - type: 'entity' or 'concept'

    Args:
        db_path: Path to index.db SQLite file.
    """
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    # Create FTS5 virtual table with porter stemmer
    cursor.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS wiki_search USING fts5(
            path,
            title,
            content,
            type,
            tokenize = 'porter unicode61'
        )
    """)

    conn.commit()
    conn.close()
    logger.info("Initialized FTS5 table in %s", db_path)


def index_wiki_page(
    db_path: Path,
    path: str,
    title: str,
    content: str,
    page_type: str,
) -> None:
    """Add or update a wiki page in the FTS5 index.

    Args:
        db_path: Path to index.db SQLite file.
        path: File path relative to wiki root (e.g., "wiki/entities/auth.md").
        title: Page title for search results.
        content: Full page content for full-text search.
        page_type: 'entity' or 'concept' for filtering.
    """
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    # Delete existing entry for this path (FTS5 doesn't support UPSERT)
    cursor.execute("DELETE FROM wiki_search WHERE path = ?", (path,))

    # Insert new/updated entry
    cursor.execute(
        "INSERT INTO wiki_search (path, title, content, type) VALUES (?, ?, ?, ?)",
        (path, title, content, page_type),
    )

    conn.commit()
    conn.close()
    logger.debug("Indexed wiki page: %s", path)


def search_wiki(
    db_path: Path,
    query: str,
    scope: str | None = None,
    limit: int = 20,
) -> list[dict]:
    """Search the wiki using FTS5 with BM25 ranking.

    Args:
        db_path: Path to index.db SQLite file.
        query: Search query string.
        scope: Optional filter by type ('entity' or 'concept').
        limit: Maximum number of results to return.

    Returns:
        List of dictionaries with:
        - path: File path
        - title: Page title
        - snippet: Content snippet
        - type: 'entity' or 'concept'
        - rank: BM25 relevance score
    """
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    # Build query with optional scope filter
    if scope:
        # Use FTS5 column filter for scope
        fts_query = f"{query} type:{scope}"
    else:
        fts_query = query

    try:
        # Search with BM25 ranking and snippet generation
        cursor.execute(
            """
            SELECT
                path,
                title,
                snippet(wiki_search, 2, '>>>', '<<<', '...', 20) as snippet,
                type,
                bm25(wiki_search) as rank
            FROM wiki_search
            WHERE wiki_search MATCH ?
            ORDER BY rank
            LIMIT ?
            """,
            (fts_query, limit),
        )

        results = []
        for row in cursor.fetchall():
            results.append({
                "path": row[0],
                "title": row[1],
                "snippet": row[2],
                "type": row[3],
                "rank": row[4],
            })

        return results

    except sqlite3.OperationalError as e:
        # Handle case where FTS5 query syntax is invalid
        logger.warning("FTS5 query error: %s", e)
        return []

    finally:
        conn.close()


def clear_search_index(db_path: Path) -> None:
    """Clear all entries from the FTS5 index.

    Args:
        db_path: Path to index.db SQLite file.
    """
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    cursor.execute("DELETE FROM wiki_search")

    conn.commit()
    conn.close()
    logger.info("Cleared FTS5 search index")


def get_index_stats(db_path: Path) -> dict:
    """Get statistics about the search index.

    Args:
        db_path: Path to index.db SQLite file.

    Returns:
        Dictionary with:
        - total_pages: Total number of indexed pages
        - entity_count: Number of entity pages
        - concept_count: Number of concept pages
    """
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT COUNT(*) FROM wiki_search")
        total = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM wiki_search WHERE type = 'entity'")
        entity_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM wiki_search WHERE type = 'concept'")
        concept_count = cursor.fetchone()[0]

        return {
            "total_pages": total,
            "entity_count": entity_count,
            "concept_count": concept_count,
        }
    except sqlite3.OperationalError:
        return {
            "total_pages": 0,
            "entity_count": 0,
            "concept_count": 0,
        }
    finally:
        conn.close()
