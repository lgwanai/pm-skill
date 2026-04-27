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


def get_page_context(page_path: Path, match_line: int, context_lines: int) -> list[str]:
    """Get surrounding lines from a page around a match.

    Args:
        page_path: Path to the markdown file.
        match_line: 1-indexed line number of the match.
        context_lines: Number of lines to include before and after.

    Returns:
        List of lines including context around the match.
    """
    try:
        content = page_path.read_text(encoding="utf-8")
        lines = content.splitlines()

        start = max(0, match_line - 1 - context_lines)
        end = min(len(lines), match_line + context_lines)

        return lines[start:end]
    except Exception:
        return []


def format_search_results(
    results: list[dict],
    context_lines: int = 3,
    format_type: str = "text",
) -> str:
    """Format search results for output.

    Args:
        results: List of search result dictionaries.
        context_lines: Number of context lines (for text format).
        format_type: Output format - 'text', 'json', or 'table'.

    Returns:
        Formatted string output.
    """
    import json

    if format_type == "json":
        return json.dumps(results, indent=2)

    elif format_type == "table":
        from rich.console import Console
        from rich.table import Table

        console = Console()
        table = Table(title="Search Results")
        table.add_column("Type", style="cyan")
        table.add_column("Title", style="green")
        table.add_column("Path")
        table.add_column("Snippet")

        for r in results:
            table.add_row(
                r.get("type", ""),
                r.get("title", ""),
                r.get("path", ""),
                r.get("snippet", "")[:60] + "..." if len(r.get("snippet", "")) > 60 else r.get("snippet", ""),
            )

        with console.capture() as capture:
            console.print(table)
        return capture.get()

    else:  # text format
        output_lines = []
        for r in results:
            output_lines.append(f"[{r.get('type', 'unknown')}] {r.get('title', '')}")
            output_lines.append(f"  Path: {r.get('path', '')}")
            if r.get("snippet"):
                output_lines.append(f"  {r['snippet']}")
            output_lines.append("")
        return "\n".join(output_lines)


def list_wiki_pages(wiki_dir: Path, scope: str = "all") -> list[dict]:
    """List all wiki pages with metadata.

    Args:
        wiki_dir: Path to wiki/ directory.
        scope: Filter by type - 'entity', 'concept', or 'all'.

    Returns:
        List of dictionaries with:
        - path: File path relative to wiki root
        - title: Page title (from frontmatter or first heading)
        - type: 'entity' or 'concept'
    """
    results = []

    # Check entities
    if scope in ("entity", "all"):
        entities_dir = wiki_dir / "entities"
        if entities_dir.exists():
            for md_file in entities_dir.glob("*.md"):
                title = extract_title(md_file)
                results.append({
                    "path": str(md_file.relative_to(wiki_dir)),
                    "title": title,
                    "type": "entity",
                })

    # Check concepts
    if scope in ("concept", "all"):
        concepts_dir = wiki_dir / "concepts"
        if concepts_dir.exists():
            for md_file in concepts_dir.glob("*.md"):
                title = extract_title(md_file)
                results.append({
                    "path": str(md_file.relative_to(wiki_dir)),
                    "title": title,
                    "type": "concept",
                })

    # Sort by title
    results.sort(key=lambda x: x["title"].lower())
    return results


def extract_title(page_path: Path) -> str:
    """Extract title from a markdown page.

    Priority:
    1. YAML frontmatter 'title' field
    2. First H1 heading
    3. Filename (without extension)

    Args:
        page_path: Path to the markdown file.

    Returns:
        Extracted title string.
    """
    import re

    try:
        content = page_path.read_text(encoding="utf-8")
        lines = content.splitlines()

        # Check for YAML frontmatter
        if lines and lines[0].strip() == "---":
            # Find closing ---
            for i, line in enumerate(lines[1:], 1):
                if line.strip() == "---":
                    frontmatter = "\n".join(lines[1:i])
                    # Look for title field
                    match = re.search(r"^title:\s*(.+)$", frontmatter, re.MULTILINE)
                    if match:
                        return match.group(1).strip().strip('"\'')
                    break

        # Check for H1 heading
        for line in lines:
            if line.startswith("# "):
                return line[2:].strip()

        # Fall back to filename
        return page_path.stem

    except Exception:
        return page_path.stem
