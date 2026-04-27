---
phase: 01-foundation-document-pipeline
plan: 01
type: execute
wave: 0
depends_on: []
files_modified: []
autonomous: true
requirements: []
user_setup:
  - service: pytest
    why: "Test infrastructure for TDD workflow"
    env_vars: []
    dashboard_config: []

must_haves:
  truths:
    - "Developer can run pytest and see test discovery working"
    - "Test fixtures exist for sample documents"
    - "Each requirement has a corresponding test placeholder"
  artifacts:
    - path: "pyproject.toml"
      provides: "pytest configuration with coverage settings"
      min_lines: 10
    - path: "tests/conftest.py"
      provides: "Shared test fixtures"
      exports: ["fixture"]
    - path: "tests/fixtures/"
      provides: "Sample documents for testing"
      contains: "sample PDF, DOCX, HTML"
    - path: "tests/test_skill.py"
      provides: "SKILL.md validation tests"
      exports: ["test_"]
    - path: "tests/test_config.py"
      provides: "Configuration loading tests"
      exports: ["test_"]
    - path: "tests/test_init.py"
      provides: "Directory initialization tests"
      exports: ["test_"]
    - path: "tests/test_cli.py"
      provides: "CLI entry point tests"
      exports: ["test_"]
    - path: "tests/test_import_pdf.py"
      provides: "PDF import tests"
      exports: ["test_"]
    - path: "tests/test_import_docx.py"
      provides: "DOCX import tests"
      exports: ["test_"]
    - path: "tests/test_import_html.py"
      provides: "HTML import tests"
      exports: ["test_"]
    - path: "tests/test_markitdown.py"
      provides: "markitdown integration tests"
      exports: ["test_"]
    - path: "tests/test_storage.py"
      provides: "File storage tests"
      exports: ["test_"]
    - path: "tests/test_validation.py"
      provides: "Document validation tests"
      exports: ["test_"]
  key_links:
    - from: "tests/conftest.py"
      to: "tests/fixtures/"
      via: "sample document paths"
      pattern: "fixture.*sample"
---

<objective>
Establish test infrastructure with pytest configuration, shared fixtures, and test scaffolds for all Phase 1 requirements. This Wave 0 task enables TDD workflow for subsequent implementation.

Purpose: Enable test-driven development with quick feedback loops (< 15 seconds per test run).
Output: Working pytest configuration with all test files as stubs.
</objective>

<execution_context>
@/Users/wuliang/.claude/get-shit-done/workflows/execute-plan.md
@/Users/wuliang/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/phases/01-foundation-document-pipeline/01-CONTEXT.md
@.planning/phases/01-foundation-document-pipeline/01-RESEARCH.md
@.planning/phases/01-foundation-document-pipeline/01-VALIDATION.md
</context>

<interfaces>
<!-- Test infrastructure patterns from CONTEXT.md/RESEARCH.md -->

Python test structure (pytest):
```python
# tests/conftest.py - shared fixtures
import pytest
from pathlib import Path

@pytest.fixture
def temp_dir(tmp_path):
    """Create temp directory for tests."""
    return tmp_path

@pytest.fixture
def sample_pdf(tmp_path):
    """Create sample PDF for testing."""
    pdf_path = tmp_path / "sample.pdf"
    # Minimal PDF content
    pdf_path.write_bytes(b"%PDF-1.4\n%EOF")
    return pdf_path
```

pytest configuration:
```toml
# pyproject.toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_functions = ["test_*"]
addopts = "-v --tb=short"
```
</interfaces>

<tasks>

<task type="auto">
  <name>Task 1: Create pytest configuration</name>
  <files>pyproject.toml, requirements.txt</files>
  <action>
Create pyproject.toml with pytest configuration:

```toml
[project]
name = "pm-skill"
version = "0.1.0"
requires-python = ">=3.12"

[project.scripts]
pm-skill = "scripts.cli:app"

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_functions = ["test_*"]
addopts = "-v --tb=short --cov=scripts --cov-report=term-missing"
```

Note: Include [project.scripts] entry point definition now (pm-skill = "scripts.cli:app") so Plan 02 Task 4 can reference it. The entry point will become functional once scripts/cli.py with the Typer app is created in Plan 02.

Update requirements.txt to include dev dependencies:
- pytest>=8.0
- pytest-cov>=5.0

Install dependencies: pip install pytest pytest-cov
  </action>
  <verify>
    <automated>pytest --version && pip show pytest-cov</automated>
  </verify>
  <done>pytest runs and discovers tests, --cov option available</done>
</task>

<task type="auto">
  <name>Task 2: Create shared test fixtures</name>
  <files>tests/conftest.py, tests/fixtures/sample.pdf, tests/fixtures/sample.docx, tests/fixtures/sample.html</files>
  <action>
Create tests/conftest.py with shared fixtures:

1. temp_knowledge_base fixture: Creates temporary raw/wiki/log directories
2. sample_pdf fixture: Returns path to tests/fixtures/sample.pdf
3. sample_docx fixture: Returns path to tests/fixtures/sample.docx
4. sample_html fixture: Returns path to tests/fixtures/sample.html

Create minimal sample documents in tests/fixtures/:
- sample.pdf: Minimal valid PDF (use PyPDF2 to create or embed minimal PDF bytes)
- sample.docx: Minimal valid DOCX (can use python-docx or pre-created file)
- sample.html: Simple HTML document with tables and text

For sample files, create minimal valid documents:
- sample.pdf: Create a text file with .pdf extension containing "%PDF-1.4\n%content\n%EOF"
- sample.docx: Use predefined minimal DOCX bytes or copy from fixtures
- sample.html: Simple HTML like "&lt;!DOCTYPE html&gt;&lt;html&gt;&lt;body&gt;&lt;h1&gt;Test&lt;/h1&gt;&lt;/body&gt;&lt;/html&gt;"
  </action>
  <verify>
    <automated>pytest tests/conftest.py -v --collect-only</automated>
  </verify>
  <done>Fixtures defined and accessible, sample files exist</done>
</task>

<task type="auto">
  <name>Task 3: Create test file stubs</name>
  <files>tests/test_skill.py, tests/test_config.py, tests/test_init.py, tests/test_cli.py, tests/test_import_pdf.py, tests/test_import_docx.py, tests/test_import_html.py, tests/test_markitdown.py, tests/test_storage.py, tests/test_validation.py</files>
  <action>
Create test file stubs for each requirement. Each file should have:

1. tests/test_skill.py - Tests for SKILL.md frontmatter and structure (FND-01)
   - test_skill_md_exists(): Check SKILL.md file exists
   - test_skill_md_frontmatter(): Check frontmatter has name, description
   - test_scripts_directory_exists(): Check scripts/ directory exists

2. tests/test_config.py - Tests for TOML configuration (FND-02)
   - test_config_loads_from_xdg(): Test XDG path loading
   - test_config_loads_from_local(): Test .pm-skill.toml loading
   - test_config_defaults(): Test default values
   - test_config_raw_dir_path(): Test raw_dir configuration

3. tests/test_init.py - Tests for directory initialization (FND-03)
   - test_init_creates_directories(): Test raw/wiki/log creation
   - test_init_creates_index_db(): Test SQLite index creation
   - test_init_idempotent(): Running init twice should not error

4. tests/test_cli.py - Tests for CLI entry point (required by Plan 02 Task 4)
   - test_cli_help(): Test --help shows available commands
   - test_cli_init(): Test init command creates directories
   - test_cli_config_show(): Test config command shows settings
   - test_cli_import_pdf(): Test import command works for PDF
   - test_cli_import_quiet(): Test --quiet flag suppresses output

5. tests/test_import_pdf.py - Tests for PDF import (IMP-01)
   - test_import_pdf_creates_markdown(): Test PDF->MD conversion
   - test_import_pdf_content_preserved(): Test content extracted
   - test_import_pdf_encoding(): Test UTF-8 handling

6. tests/test_import_docx.py - Tests for DOCX import (IMP-02)
   - test_import_docx_creates_markdown(): Test DOCX->MD conversion
   - test_import_docx_tables(): Test table preservation

7. tests/test_import_html.py - Tests for HTML import (IMP-03)
   - test_import_html_creates_markdown(): Test HTML->MD conversion
   - test_import_html_links(): Test link preservation

8. tests/test_markitdown.py - Tests for markitdown usage (IMP-04)
   - test_markitdown_imports(): Test markitdown module available
   - test_markitdown_convert_pdf(): Test PDF conversion API
   - test_markitdown_convert_docx(): Test DOCX conversion API

9. tests/test_storage.py - Tests for raw/ storage (IMP-05)
   - test_markdown_saved_to_raw(): Test output path
   - test_markdown_filename_conversion(): Test filename handling
   - test_markdown_encoding(): Test UTF-8 write

10. tests/test_validation.py - Tests for validation (IMP-06)
   - test_validate_table_syntax(): Test table column alignment
   - test_validate_image_references(): Test image path checking
   - test_validate_format_integrity(): Test formatting checks

Each test should start with `pytest.skip("Wave 0 scaffold")` to mark as pending.
  </action>
  <verify>
    <automated>pytest tests/ --collect-only | grep "test_" | wc -l</automated>
  </verify>
  <done>All 10 test files exist with at least 3 tests each (30+ tests collected)</done>
</task>

</tasks>

<verification>
Run full test suite to verify infrastructure:
```bash
pytest tests/ -v --collect-only  # Should show all tests
pytest tests/ -v                  # Should skip all (scaffold)
```

Test infrastructure checklist:
- [ ] pytest installed and configured
- [ ] conftest.py with shared fixtures
- [ ] Sample documents in tests/fixtures/
- [ ] All 10 test files exist
- [ ] Each test file has 3+ test functions
- [ ] All tests are marked skip (Wave 0 scaffold)
</verification>

<success_criteria>
- pytest configuration complete with coverage support
- tests/ directory structure established
- Sample PDF, DOCX, HTML fixtures available
- All Phase 1 requirements have corresponding test files
- Test discovery works and shows all tests as skipped
- Test run completes in &lt; 5 seconds
</success_criteria>

<output>
After completion, create `.planning/phases/01-foundation-document-pipeline/01-SUMMARY.md`
</output>