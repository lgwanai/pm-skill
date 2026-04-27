---
phase: 01-foundation-document-pipeline
plan: 03
type: tdd
wave: 2
depends_on: ["01", "02"]
files_modified:
  - scripts/importer.py
  - scripts/utils/validation.py
  - requirements.txt
autonomous: true
requirements:
  - IMP-01
  - IMP-02
  - IMP-03
  - IMP-04
  - IMP-05
  - IMP-06

must_haves:
  truths:
    - "User can import a PDF file and find it converted to Markdown in raw/"
    - "User can import a DOC/DOCX file and find it converted to Markdown in raw/"
    - "User can import an HTML file and find it converted to Markdown in raw/"
    - "Converted files have basic validation (tables, images, format)"
    - "Import shows progress indicator with Rich"
  artifacts:
    - path: "scripts/importer.py"
      provides: "Document import logic using markitdown"
      exports: ["import_document", "import_batch"]
    - path: "scripts/utils/validation.py"
      provides: "Markdown validation utilities"
      exports: ["validate_markdown", "ValidationIssue"]
    - path: "requirements.txt"
      provides: "Dependencies including markitdown"
      contains: "markitdown"
  key_links:
    - from: "scripts/importer.py"
      to: "markitdown library"
      via: "from markitdown import MarkItDown"
      pattern: "MarkItDown"
    - from: "scripts/importer.py"
      to: "scripts/utils/validation.py"
      via: "from .utils.validation import validate_markdown"
      pattern: "validate_markdown"
    - from: "scripts/importer.py"
      to: "scripts/config.py"
      via: "from .config import load_config"
      pattern: "raw_dir"
---

<objective>
Implement document import pipeline using markitdown for PDF/DOCX/HTML to Markdown conversion, with validation checks for table syntax, image references, and format integrity. Users can import documents via CLI and have them stored as Markdown in the raw/ directory.

Purpose: Enable the core document import workflow that feeds the knowledge compilation phase.
Output: Working import command with markitdown integration and validation.
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
@.planning/phases/01-foundation-document-pipeline/02-SUMMARY.md
</context>

<interfaces>
<!-- Key interfaces from Plan 02 and RESEARCH.md -->

Configuration interface (from Plan 02):
```python
from scripts.config import PMSkillConfig, load_config

config = load_config()
raw_dir = config.raw_dir  # Path object
```

markitdown API (from RESEARCH.md):
```python
from markitdown import MarkItDown

md = MarkItDown()
result = md.convert(str(source_path))  # Returns DocumentConverterResult
markdown_content = result.markdown      # The converted text
title = result.title                    # Extracted document title or None
```

CLI command pattern (from CONTEXT.md locked decisions):
```python
@app.command()
def import_doc(
    path: Path = typer.Argument(..., exists=True),
    format: str = typer.Option(None, "--format", "-f"),
    no_validate: bool = typer.Option(False, "--no-validate"),
    quiet: bool = typer.Option(False, "--quiet", "-q")
):
    """Import a document into the knowledge base."""
```
</interfaces>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: Create validation utilities</name>
  <files>scripts/utils/validation.py</files>
  <behavior>
    - Test 1: validate_markdown() returns empty list for valid content
    - Test 2: validate_markdown() detects table column mismatches
    - Test 3: validate_markdown() warns on missing image references
    - Test 4: ValidationIssue has level, message, line attributes
    - Test 5: Validation levels: error, warn, info
  </behavior>
  <action>
Write tests first in tests/test_validation.py:
```python
from scripts.utils.validation import validate_markdown, ValidationIssue

def test_validate_clean_markdown():
    content = "# Heading\n\nParagraph text."
    issues = validate_markdown(content)
    assert issues == []

def test_validate_table_column_mismatch():
    content = "| Col1 | Col2 |\n|-----|\n| A | B | C |"
    issues = validate_markdown(content)
    assert any(i.level == "error" and "column" in i.message.lower() for i in issues)

def test_validate_image_reference():
    content = "![alt](missing-image.png)"
    issues = validate_markdown(content)
    assert any(i.level == "warn" and "image" in i.message.lower() for i in issues)

def test_validation_issue_structure():
    issues = validate_markdown("| A |\n|--|\n| B | C |")
    assert len(issues) > 0
    assert hasattr(issues[0], 'level')
    assert hasattr(issues[0], 'message')
    assert hasattr(issues[0], 'line')
```

Create scripts/utils/validation.py:
- ValidationIssue dataclass with level, message, line
- validate_markdown(content: str) -> list[ValidationIssue]
- Check table syntax: column count consistency
- Check image references: warn if local path doesn't exist
- Check format integrity: unclosed code blocks, broken links
- Levels: error (blocking issues), warn (potential issues), info (suggestions)

Validation rules from CONTEXT.md:
- Table rows must have same column count as header (ERROR)
- Image paths should exist or be valid URLs (WARN)
- Orphaned reference links (WARN)
- Code block language hints missing (INFO)

Run tests: pytest tests/test_validation.py -v
  </action>
  <verify>
    <automated>pytest tests/test_validation.py -v</automated>
  </verify>
  <done>Validation utilities work with all test cases passing</done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: Create document import logic with markitdown</name>
  <files>scripts/importer.py, requirements.txt</files>
  <behavior>
    - Test 1: import_document() converts PDF to Markdown
    - Test 2: import_document() converts DOCX to Markdown
    - Test 3: import_document() converts HTML to Markdown
    - Test 4: Converted content is saved to raw/ directory
    - Test 5: Output filename is source.stem + ".md"
    - Test 6: markitdown library is used for conversion
  </behavior>
  <action>
Write tests first in tests/test_import_pdf.py, tests/test_import_docx.py, tests/test_import_html.py:

```python
# tests/test_import_pdf.py
from pathlib import Path
from scripts.importer import import_document

def test_import_pdf_creates_markdown(tmp_path, sample_pdf):
    output = import_document(sample_pdf, tmp_path / "raw")
    assert output.suffix == ".md"
    assert output.exists()
    content = output.read_text()
    assert len(content) > 0

def test_import_pdf_uses_markitdown(tmp_path, sample_pdf, monkeypatch):
    import scripts.importer as imp
    original_convert = imp.MarkItDown.convert
    called = []
    def track_convert(self, path):
        called.append(path)
        return original_convert(self, path)
    monkeypatch.setattr(imp.MarkItDown, 'convert', track_convert)
    import_document(sample_pdf, tmp_path / "raw")
    assert len(called) == 1
```

Update requirements.txt:
```
markitdown>=0.1.5
```

Create scripts/importer.py:
- import_document(source_path: Path, output_dir: Path, format: str = None, no_validate: bool = False) -> Path
- Use MarkItDown().convert() for all formats
- Auto-detect format from file extension if not specified
- Save output to output_dir / source.stem + ".md"
- Call validate_markdown() unless no_validate=True
- Log validation issues (warn but don't block)
- Return path to created Markdown file

Format detection:
- .pdf -> PDF
- .doc, .docx -> DOCX
- .html, .htm -> HTML

Run tests: pytest tests/test_import_pdf.py tests/test_import_docx.py tests/test_import_html.py -v
  </action>
  <verify>
    <automated>pytest tests/test_import_pdf.py tests/test_import_docx.py tests/test_import_html.py tests/test_markitdown.py -v</automated>
  </verify>
  <done>All import tests pass, markitdown integration verified</done>
</task>

<task type="auto" tdd="true">
  <name>Task 3: Add storage and batch import support</name>
  <files>scripts/importer.py</files>
  <behavior>
    - Test 1: Markdown files saved to raw/ directory from config
    - Test 2: Batch import processes multiple files
    - Test 3: Batch import shows progress with Rich
    - Test 4: Batch import logs failures to log/import-{timestamp}.log
    - Test 5: UTF-8 encoding is used for all file writes
  </behavior>
  <action>
Write tests first in tests/test_storage.py:
```python
from scripts.importer import import_document, import_batch
from scripts.config import load_config

def test_markdown_saved_to_config_raw_dir(tmp_path, sample_pdf, monkeypatch):
    monkeypatch.chdir(tmp_path)
    config = load_config()
    output = import_document(sample_pdf, config.raw_dir)
    assert output.parent.name == "raw"

def test_batch_import_processes_multiple(tmp_path, sample_pdf, sample_docx, sample_html):
    outputs = import_batch([sample_pdf, sample_docx, sample_html], tmp_path / "raw")
    success, failures = outputs
    assert success == 3
    assert failures == 0

def test_batch_import_logs_failures(tmp_path, sample_pdf):
    # Create a file that will fail
    bad_file = tmp_path / "bad.txt"
    bad_file.write_text("not a document")
    success, failures = import_batch([sample_pdf, bad_file], tmp_path / "raw", log_dir=tmp_path / "log")
    assert success >= 1  # PDF should succeed
    assert failures >= 1  # Bad file should fail
```

Update scripts/importer.py:
- Add import_batch(paths: list[Path], output_dir: Path, no_validate: bool = False, quiet: bool = False, log_dir: Path = None) -> tuple[int, int]
- Use Rich Progress for batch processing
- Log failures to log/import-{timestamp}.log
- Return (success_count, failure_count)
- Use UTF-8 encoding for all file writes

Error handling from CONTEXT.md:
- Import errors: log to file, continue with remaining files
- Single file error: print error message with suggestion
- Batch mode: summary at end

Run tests: pytest tests/test_storage.py -v
  </action>
  <verify>
    <automated>pytest tests/test_storage.py -v</automated>
  </verify>
  <done>Storage and batch import working, all storage tests pass</done>
</task>

<task type="auto" tdd="true">
  <name>Task 4: Add import command to CLI</name>
  <files>scripts/cli.py</files>
  <behavior>
    - Test 1: pm-skill import sample.pdf creates raw/sample.md
    - Test 2: pm-skill import --quiet produces no output
    - Test 3: pm-skill import --no-validate skips validation
    - Test 4: pm-skill import --format pdf forces format
    - Test 5: Import shows progress indicator
  </behavior>
  <action>
Update tests/test_cli.py:
```python
def test_cli_import_pdf(tmp_path, sample_pdf, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["import", str(sample_pdf)])
    assert result.exit_code == 0
    assert (tmp_path / "knowledge-base" / "raw" / f"{sample_pdf.stem}.md").exists()

def test_cli_import_quiet(tmp_path, sample_pdf, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["import", str(sample_pdf), "--quiet"])
    assert result.exit_code == 0
    assert result.output == ""

def test_cli_import_no_validate(tmp_path, sample_pdf, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["import", str(sample_pdf), "--no-validate"])
    assert result.exit_code == 0
```

Update scripts/cli.py:
- Add import_doc command (alias: import)
- Arguments: path (required), --format/-f, --no-validate, --quiet/-q
- Load config for raw_dir path
- Call import_document or import_batch based on path type
- Handle single file vs directory (if directory, batch import all supported files)
- Print success message with Rich (unless --quiet)
- Print validation warnings (unless --no-validate or --quiet)

Command signature from CONTEXT.md locked decision:
```python
@app.command("import")
def import_doc(
    path: Path = typer.Argument(..., exists=True, help="Document path to import"),
    format: str = typer.Option(None, "--format", "-f", help="Force format (pdf, docx, html)"),
    no_validate: bool = typer.Option(False, "--no-validate", help="Skip validation checks"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress non-essential output")
):
```

Run tests: pytest tests/test_cli.py -v
  </action>
  <verify>
    <automated>pytest tests/test_cli.py -v && pm-skill import --help</automated>
  </verify>
  <done>CLI import command works with all options, all CLI tests pass</done>
</task>

</tasks>

<verification>
Run all import tests:
```bash
pytest tests/test_import_*.py tests/test_storage.py tests/test_validation.py tests/test_markitdown.py -v
```

Manual verification:
```bash
pm-skill import tests/fixtures/sample.pdf      # Should create raw/sample.md
pm-skill import tests/fixtures/sample.docx     # Should create raw/sample.md
pm-skill import tests/fixtures/sample.html     # Should create raw/sample.md
pm-skill import tests/fixtures/sample.pdf -q   # Should be silent
cat knowledge-base/raw/sample.md               # Should show Markdown content
```

Full test suite:
```bash
pytest tests/ -v --cov=scripts --cov-report=term-missing
```
</verification>

<success_criteria>
- PDF import creates valid Markdown in raw/
- DOCX import creates valid Markdown in raw/
- HTML import creates valid Markdown in raw/
- markitdown is used for all conversions (verified in tests)
- Validation checks table syntax and image references
- Import shows progress with Rich
- --quiet flag suppresses output
- --no-validate skips validation
- All 6 IMP requirements satisfied
- All tests pass with &gt;80% coverage
</success_criteria>

<output>
After completion, create `.planning/phases/01-foundation-document-pipeline/03-SUMMARY.md`
</output>
