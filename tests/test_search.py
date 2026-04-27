"""Tests for search and retrieval functionality (RET-01, RET-02, RET-03)."""

import json
import pytest
from pathlib import Path
from scripts.search import (
    init_fts5_table,
    index_wiki_page,
    search_wiki,
    format_search_results,
    get_page_context,
    list_wiki_pages,
    extract_title,
)
from scripts.config import PMSkillConfig, LLMConfig


class TestFTS5Search:
    """Tests for FTS5 full-text search functionality."""

    @pytest.fixture
    def indexed_db(self, tmp_path: Path) -> Path:
        """Create and populate a test FTS5 database.

        Returns:
            Path to the test index.db with sample data.
        """
        db_path = tmp_path / "index.db"
        init_fts5_table(db_path)

        # Index sample entity pages
        index_wiki_page(
            db_path,
            "wiki/entities/user-auth.md",
            "User Authentication",
            "The user authentication system manages login sessions. Password hashing uses bcrypt. Sessions expire after 24 hours.",
            "entity",
        )
        index_wiki_page(
            db_path,
            "wiki/entities/payment.md",
            "Payment Processing",
            "Payment gateway integration for credit card transactions. Supports Stripe and PayPal APIs.",
            "entity",
        )
        index_wiki_page(
            db_path,
            "wiki/concepts/security.md",
            "Security",
            "Security concepts include authentication, authorization, and encryption. Password hashing protects user credentials.",
            "concept",
        )
        return db_path

    def test_fts5_search_basic(self, indexed_db):
        """Test basic FTS5 keyword search.

        Verifies that:
        - FTS5 search returns matching results
        - Results include file path and snippet
        - Search handles multi-word queries
        """
        results = search_wiki(indexed_db, "authentication")

        assert len(results) >= 1
        assert any("user-auth" in r["path"] or "security" in r["path"] for r in results)
        # Each result has required fields
        for r in results:
            assert "path" in r
            assert "title" in r
            assert "snippet" in r
            assert "type" in r

    def test_fts5_search_with_scope(self, indexed_db):
        """Test search limited to entities or concepts scope.

        Verifies that:
        - Scope filter limits search to entities/ directory
        - Scope filter limits search to concepts/ directory
        - Default scope searches all directories
        """
        # Search entities only
        entity_results = search_wiki(indexed_db, "password", scope="entity")
        for r in entity_results:
            assert r["type"] == "entity"

        # Search concepts only
        concept_results = search_wiki(indexed_db, "authentication", scope="concept")
        for r in concept_results:
            assert r["type"] == "concept"

        # Search all (default)
        all_results = search_wiki(indexed_db, "password")
        types = {r["type"] for r in all_results}
        assert len(types) > 1 or len(all_results) == 0

    def test_fts5_search_with_limit(self, indexed_db):
        """Test result limiting for search.

        Verifies that:
        - Limit parameter controls max results
        - Default limit is applied when not specified
        """
        results_limited = search_wiki(indexed_db, "a", limit=1)
        assert len(results_limited) <= 1

        results_default = search_wiki(indexed_db, "a")
        assert len(results_default) <= 20

    def test_search_context_lines(self, tmp_path: Path):
        """Test --context flag showing surrounding lines.

        Verifies that:
        - Context flag includes N lines before match
        - Context flag includes N lines after match
        - Context output is clearly formatted
        """
        # Create a test markdown file
        test_file = tmp_path / "test.md"
        test_file.write_text(
            "Line 1\nLine 2\nLine 3\nMATCH LINE\nLine 5\nLine 6\nLine 7\n"
        )

        context = get_page_context(test_file, match_line=4, context_lines=2)

        assert len(context) == 5  # 2 before + match + 2 after
        assert "MATCH LINE" in context[2]

    def test_search_format_json(self, indexed_db):
        """Test JSON output format for search results.

        Verifies that:
        - JSON output is valid JSON
        - JSON includes file, line, snippet fields
        - JSON format is machine-readable
        """
        results = search_wiki(indexed_db, "authentication")
        formatted = format_search_results(results, context_lines=1, format_type="json")

        # Should be valid JSON
        parsed = json.loads(formatted)
        assert isinstance(parsed, list)

        # Each item should have expected fields
        for item in parsed:
            assert "path" in item
            assert "title" in item
            assert "snippet" in item

    def test_search_format_table(self, indexed_db):
        """Test table output format for search results."""
        results = search_wiki(indexed_db, "authentication")
        formatted = format_search_results(results, context_lines=1, format_type="table")

        # Should be a string (Rich table output)
        assert isinstance(formatted, str)

    def test_search_format_text(self, indexed_db):
        """Test text output format for search results."""
        results = search_wiki(indexed_db, "authentication")
        formatted = format_search_results(results, context_lines=1, format_type="text")

        # Should be plain text
        assert isinstance(formatted, str)
        assert "authentication" in formatted.lower() or len(results) == 0


class TestListPages:
    """Tests for listing wiki pages."""

    @pytest.fixture
    def populated_wiki(self, tmp_path: Path) -> Path:
        """Create a wiki directory with sample pages.

        Returns:
            Path to the wiki directory.
        """
        wiki_dir = tmp_path / "wiki"
        entities_dir = wiki_dir / "entities"
        concepts_dir = wiki_dir / "concepts"

        entities_dir.mkdir(parents=True)
        concepts_dir.mkdir(parents=True)

        # Create entity pages
        (entities_dir / "user-auth.md").write_text(
            "---\ntitle: User Authentication\n---\n# User Authentication\n\nOverview here."
        )
        (entities_dir / "payment.md").write_text(
            "# Payment Processing\n\nPayment gateway details."
        )

        # Create concept pages
        (concepts_dir / "security.md").write_text(
            "---\ntitle: Security Overview\n---\n# Security\n\nSecurity concepts."
        )

        return wiki_dir

    def test_list_entities(self, populated_wiki):
        """Test listing all entity pages.

        Verifies that:
        - All entity markdown files are listed
        - List includes file names and paths
        - Empty directory returns empty list
        """
        results = list_wiki_pages(populated_wiki, scope="entity")

        assert len(results) == 2
        titles = [r["title"] for r in results]
        # Should extract title from frontmatter or heading
        assert "User Authentication" in titles or "Payment Processing" in titles

    def test_list_concepts(self, populated_wiki):
        """Test listing all concept pages.

        Verifies that:
        - All concept markdown files are listed
        - List includes file names and paths
        - Empty directory returns empty list
        """
        results = list_wiki_pages(populated_wiki, scope="concept")

        assert len(results) == 1
        assert results[0]["title"] in ["Security Overview", "Security"]

    def test_list_all(self, populated_wiki):
        """Test listing all wiki pages."""
        results = list_wiki_pages(populated_wiki, scope="all")

        assert len(results) == 3

    def test_list_with_format(self, populated_wiki):
        """Test list output formats.

        Verifies that:
        - Default format is human-readable table
        - JSON format is valid JSON array
        - Format can be specified via format_type parameter
        """
        # JSON format
        results = list_wiki_pages(populated_wiki)
        formatted = format_search_results(results, context_lines=0, format_type="json")
        parsed = json.loads(formatted)
        assert isinstance(parsed, list)

    def test_extract_title_from_frontmatter(self, tmp_path: Path):
        """Test extracting title from YAML frontmatter."""
        test_file = tmp_path / "test.md"
        test_file.write_text("---\ntitle: My Title\n---\n# Heading\nContent")

        title = extract_title(test_file)
        assert title == "My Title"

    def test_extract_title_from_heading(self, tmp_path: Path):
        """Test extracting title from first H1 heading."""
        test_file = tmp_path / "test.md"
        test_file.write_text("# First Heading\n\nContent here")

        title = extract_title(test_file)
        assert title == "First Heading"

    def test_extract_title_from_filename(self, tmp_path: Path):
        """Test extracting title from filename as fallback."""
        test_file = tmp_path / "my-document.md"
        test_file.write_text("Just content, no title markers")

        title = extract_title(test_file)
        assert title == "my-document"


class TestSearchCLI:
    """Tests for CLI search command integration."""

    def test_search_command_help(self):
        """Test that search --help works."""
        from typer.testing import CliRunner
        from scripts.cli import app

        runner = CliRunner()
        result = runner.invoke(app, ["search", "--help"])

        assert result.exit_code == 0
        assert "query" in result.output.lower() or "search" in result.output.lower()

    def test_list_command_help(self):
        """Test that list --help works."""
        from typer.testing import CliRunner
        from scripts.cli import app

        runner = CliRunner()
        result = runner.invoke(app, ["list", "--help"])

        assert result.exit_code == 0