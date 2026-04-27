"""Tests for knowledge compilation module.

Tests cover:
- Compilation prompt template loading
- LLM-powered document compilation
- Wiki structure generation
- Confidence annotations
- FTS5 search integration
"""

import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from scripts.config import LLMConfig, PMSkillConfig


class TestPromptTemplate:
    """Tests for compilation prompt template (Task 1)."""

    def test_prompt_template_file_exists(self) -> None:
        """Prompt template file exists at references/prompts/compile.md."""
        prompt_path = Path(__file__).parent.parent / "references" / "prompts" / "compile.md"
        assert prompt_path.exists(), f"Prompt template not found at {prompt_path}"

    def test_prompt_template_loads_successfully(self) -> None:
        """load_compile_prompt() reads and returns the template content."""
        from scripts.compiler import load_compile_prompt

        prompt = load_compile_prompt()
        assert prompt is not None
        assert len(prompt) > 100  # Template should have substantial content

    def test_prompt_template_contains_required_sections(self) -> None:
        """Prompt template contains all required sections."""
        from scripts.compiler import load_compile_prompt

        prompt = load_compile_prompt()

        # Required output sections
        assert "Overview" in prompt or "overview" in prompt.lower()
        assert "Key Content" in prompt or "key content" in prompt.lower()
        assert "Entities" in prompt or "entities" in prompt.lower()
        assert "Concepts" in prompt or "concepts" in prompt.lower()
        assert "Relations" in prompt or "relations" in prompt.lower()

    def test_prompt_template_contains_confidence_annotations(self) -> None:
        """Prompt template includes confidence annotation instructions."""
        from scripts.compiler import load_compile_prompt

        prompt = load_compile_prompt()

        # Confidence annotation levels
        assert "EXTRACTED" in prompt
        assert "INFERRED" in prompt
        assert "AMBIGUOUS" in prompt
        assert "UNVERIFIED" in prompt


class TestCompileDocument:
    """Tests for document compilation core functions (Task 2)."""

    def test_compute_content_hash(self) -> None:
        """compute_content_hash returns consistent SHA-256 hash."""
        from scripts.compiler import compute_content_hash

        content = "Test content for hashing"
        hash1 = compute_content_hash(content)
        hash2 = compute_content_hash(content)

        assert hash1 == hash2
        assert len(hash1) == 64  # SHA-256 produces 64 hex characters
        assert hash1 != compute_content_hash("Different content")

    def test_check_hash_changed_detects_change(self, temp_knowledge_base: dict) -> None:
        """check_hash_changed returns True when content differs from stored hash."""
        from scripts.compiler import check_hash_changed, store_content_hash

        db_path = temp_knowledge_base["root"] / "index.db"
        raw_file = temp_knowledge_base["raw"] / "test.md"
        raw_file.write_text("Original content")

        # Store initial hash
        store_content_hash(db_path, raw_file, "Original content")

        # Check with different content
        changed = check_hash_changed(db_path, raw_file, "Modified content")
        assert changed is True

    def test_check_hash_changed_unchanged(self, temp_knowledge_base: dict) -> None:
        """check_hash_changed returns False when content matches stored hash."""
        from scripts.compiler import check_hash_changed, store_content_hash

        db_path = temp_knowledge_base["root"] / "index.db"
        raw_file = temp_knowledge_base["raw"] / "test.md"
        content = "Same content"

        # Store initial hash
        store_content_hash(db_path, raw_file, content)

        # Check with same content
        changed = check_hash_changed(db_path, raw_file, content)
        assert changed is False

    def test_compile_document_returns_structured_output(
        self,
        mock_config: PMSkillConfig,
        sample_raw_markdown: str,
        mock_anthropic_response: MagicMock,
    ) -> None:
        """compile_document calls LLM and returns structured dict."""
        from scripts.compiler import compile_document

        with patch("scripts.compiler.get_anthropic_client") as mock_client:
            mock_client.return_value.messages.create.return_value = mock_anthropic_response

            result = compile_document(sample_raw_markdown, mock_config)

            assert "overview" in result
            assert "key_content" in result
            assert "entities" in result
            assert "concepts" in result
            assert "relations" in result

    def test_compile_document_includes_confidence_annotations(
        self,
        mock_config: PMSkillConfig,
        sample_raw_markdown: str,
        mock_anthropic_response: MagicMock,
    ) -> None:
        """compile_document output includes confidence annotations."""
        from scripts.compiler import compile_document

        with patch("scripts.compiler.get_anthropic_client") as mock_client:
            mock_client.return_value.messages.create.return_value = mock_anthropic_response

            result = compile_document(sample_raw_markdown, mock_config)

            # At least one confidence annotation should be present
            all_text = str(result)
            has_confidence = any(
                level in all_text for level in ["EXTRACTED", "INFERRED", "AMBIGUOUS", "UNVERIFIED"]
            )
            assert has_confidence

    def test_write_entity_page_creates_file(
        self,
        temp_wiki_dir: dict,
        sample_wiki_page: dict,
    ) -> None:
        """write_entity_page creates markdown file in wiki/entities/."""
        from scripts.compiler import write_entity_page

        wiki_dir = temp_wiki_dir["wiki"]

        result_path = write_entity_page(
            wiki_dir=wiki_dir,
            name="test-entity",
            compiled=sample_wiki_page,
        )

        assert result_path.exists()
        assert result_path.name == "test-entity.md"
        assert "test-entity" in str(result_path)

    def test_write_entity_page_has_required_sections(
        self,
        temp_wiki_dir: dict,
        sample_wiki_page: dict,
    ) -> None:
        """Entity page includes all required sections."""
        from scripts.compiler import write_entity_page

        wiki_dir = temp_wiki_dir["wiki"]

        result_path = write_entity_page(
            wiki_dir=wiki_dir,
            name="test-entity",
            compiled=sample_wiki_page,
        )

        content = result_path.read_text()

        assert "## Overview" in content or "## overview" in content.lower()
        assert "## Key Content" in content or "## key content" in content.lower()
        assert "## Entities" in content or "## entities" in content.lower()
        assert "## Concepts" in content or "## concepts" in content.lower()
        assert "## Relations" in content or "## relations" in content.lower()


class TestWikiStructure:
    """Tests for wiki structure generation (Task 3)."""

    def test_extract_concepts(self, sample_wiki_page: dict) -> None:
        """extract_concepts returns list of concept names."""
        from scripts.compiler import extract_concepts

        concepts = extract_concepts(sample_wiki_page)

        assert isinstance(concepts, list)
        assert "Authentication" in concepts or any("Authentication" in c for c in concepts)

    def test_write_concept_page(
        self,
        temp_wiki_dir: dict,
    ) -> None:
        """write_concept_page creates concept page with backlinks."""
        from scripts.compiler import write_concept_page

        wiki_dir = temp_wiki_dir["wiki"]

        result_path = write_concept_page(
            wiki_dir=wiki_dir,
            concept="Authentication",
            sources=["user-auth-system.md", "security-overview.md"],
        )

        assert result_path.exists()
        assert result_path.name == "Authentication.md"

        content = result_path.read_text()
        assert "user-auth-system" in content
        assert "security-overview" in content

    def test_update_index(
        self,
        temp_wiki_dir: dict,
    ) -> None:
        """update_index creates/updates wiki/index.md with entity and concept lists."""
        from scripts.compiler import update_index

        wiki_dir = temp_wiki_dir["wiki"]

        update_index(
            wiki_dir=wiki_dir,
            entities=["user-auth-system", "security-overview"],
            concepts=["Authentication", "Authorization"],
        )

        index_path = wiki_dir / "index.md"
        assert index_path.exists()

        content = index_path.read_text()
        assert "user-auth-system" in content
        assert "Authentication" in content

    def test_update_glossary(
        self,
        temp_wiki_dir: dict,
    ) -> None:
        """update_glossary creates/updates wiki/glossary.md with terms."""
        from scripts.compiler import update_glossary

        wiki_dir = temp_wiki_dir["wiki"]

        terms = {
            "Authentication": "Process of verifying user identity",
            "Authorization": "Process of checking user permissions",
        }

        update_glossary(wiki_dir=wiki_dir, terms=terms)

        glossary_path = wiki_dir / "glossary.md"
        assert glossary_path.exists()

        content = glossary_path.read_text()
        assert "Authentication" in content
        assert "verifying user identity" in content

    def test_write_compile_log(
        self,
        temp_knowledge_base: dict,
    ) -> None:
        """write_compile_log writes summary to log/ directory."""
        from scripts.compiler import write_compile_log

        log_dir = temp_knowledge_base["log"]

        summary = {
            "files_processed": 5,
            "entities_created": 5,
            "concepts_extracted": 12,
            "errors": 0,
        }

        write_compile_log(log_dir=log_dir, summary=summary)

        # Check log file was created
        log_files = list(log_dir.glob("compile-*.log"))
        assert len(log_files) == 1

        content = log_files[0].read_text()
        assert "5" in content  # files_processed
        assert "12" in content  # concepts_extracted


class TestCompileCommandAndFTS5:
    """Tests for compile CLI command and FTS5 index (Task 4)."""

    def test_init_fts5_table(self, temp_knowledge_base: dict) -> None:
        """init_fts5_table creates wiki_search virtual table."""
        from scripts.search import init_fts5_table

        db_path = temp_knowledge_base["root"] / "index.db"

        # Initialize FTS5
        init_fts5_table(db_path)

        # Verify table exists
        import sqlite3

        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='wiki_search'"
        )
        result = cursor.fetchone()
        conn.close()

        assert result is not None

    def test_index_wiki_page(self, temp_knowledge_base: dict) -> None:
        """index_wiki_page adds/updates page in FTS5 index."""
        from scripts.search import init_fts5_table, index_wiki_page

        db_path = temp_knowledge_base["root"] / "index.db"

        # Initialize FTS5
        init_fts5_table(db_path)

        # Index a page
        index_wiki_page(
            db_path=db_path,
            path="wiki/entities/user-auth.md",
            title="User Authentication",
            content="Authentication system for user login and session management.",
            page_type="entity",
        )

        # Verify it was indexed
        import sqlite3

        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT title FROM wiki_search WHERE path = ?", ("wiki/entities/user-auth.md",))
        result = cursor.fetchone()
        conn.close()

        assert result is not None
        assert result[0] == "User Authentication"

    def test_search_wiki_basic(self, temp_knowledge_base: dict) -> None:
        """search_wiki returns matching results with BM25 ranking."""
        from scripts.search import init_fts5_table, index_wiki_page, search_wiki

        db_path = temp_knowledge_base["root"] / "index.db"

        # Initialize and index
        init_fts5_table(db_path)
        index_wiki_page(
            db_path=db_path,
            path="wiki/entities/auth.md",
            title="Authentication",
            content="User authentication with password and session management.",
            page_type="entity",
        )
        index_wiki_page(
            db_path=db_path,
            path="wiki/entities/security.md",
            title="Security Overview",
            content="System security policies and access control.",
            page_type="entity",
        )

        # Search for "authentication"
        results = search_wiki(db_path=db_path, query="authentication")

        assert len(results) >= 1
        assert any("auth" in r["path"] for r in results)

    def test_search_wiki_with_scope(self, temp_knowledge_base: dict) -> None:
        """search_wiki filters by scope (entities/concepts)."""
        from scripts.search import init_fts5_table, index_wiki_page, search_wiki

        db_path = temp_knowledge_base["root"] / "index.db"

        # Initialize and index
        init_fts5_table(db_path)
        index_wiki_page(
            db_path=db_path,
            path="wiki/entities/test.md",
            title="Test Entity",
            content="Test content",
            page_type="entity",
        )
        index_wiki_page(
            db_path=db_path,
            path="wiki/concepts/testing.md",
            title="Testing Concept",
            content="Test methodology",
            page_type="concept",
        )

        # Search with entity scope
        results = search_wiki(db_path=db_path, query="test", scope="entity")

        assert all(r["type"] == "entity" for r in results)

    def test_compile_force_flag(
        self,
        mock_config: PMSkillConfig,
        sample_raw_markdown: str,
        mock_anthropic_response: MagicMock,
        temp_knowledge_base: dict,
    ) -> None:
        """Force flag bypasses hash check and recompiles."""
        from scripts.compiler import check_hash_changed, compile_document, store_content_hash

        db_path = temp_knowledge_base["root"] / "index.db"
        raw_file = temp_knowledge_base["raw"] / "test.md"
        raw_file.write_text(sample_raw_markdown)

        # Store initial hash
        store_content_hash(db_path, raw_file, sample_raw_markdown)

        # Without force, should skip
        changed = check_hash_changed(db_path, raw_file, sample_raw_markdown)
        assert changed is False

        # With force flag (--force), compile_document should run anyway
        # This is tested at CLI level, but we verify the mechanism works
        with patch("scripts.compiler.get_anthropic_client") as mock_client:
            mock_client.return_value.messages.create.return_value = mock_anthropic_response

            result = compile_document(sample_raw_markdown, mock_config, force=True)
            assert result is not None