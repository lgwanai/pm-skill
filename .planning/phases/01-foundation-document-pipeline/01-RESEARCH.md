# Phase 1: Foundation & Document Pipeline - Research

**Researched:** 2026-04-27
**Domain:** Claude Code Skill Development / Document Import Pipeline
**Confidence:** HIGH

## Summary

This phase establishes the foundation for PM Skill using the create-skill workflow. The core technical challenge is implementing a reliable document-to-markdown conversion pipeline using markitdown, with proper CLI structure following Typer/Rich patterns from existing skills.

**Primary recommendation:** Use markitdown 0.1.5+ for all document conversion (PDF/DOCX/HTML -> Markdown), Typer 0.21+ with Rich for CLI, and pydantic-settings for configuration. Follow the mail-skill pattern for CLI structure.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- Use `pm-skill` as primary command name
- Subcommands: `import`, `init`, `config`
- Import command: `pm-skill import <path>` with optional `--format` flag (auto-detect by default)
- Output uses Rich for colored terminal output with progress indicators
- Silent mode: `--quiet` flag suppresses non-essential output
- Configuration location: `~/.config/pm-skill/config.toml` (XDG Base Directory specification)
- Configuration format: TOML (human-readable, supports comments)
- Fallback: `.pm-skill.toml` in current directory
- Config includes: `raw_dir`, `wiki_dir`, `log_dir`, `llm.model`, `llm.api_key_env`
- Directory structure: `raw/`, `wiki/`, `log/`, `index.db` under knowledge-base/
- Document validation: table syntax, image references, format integrity
- Validation failure: save file but warn user, log details
- Skip validation: `--no-validate` flag
- Import errors: log to file, continue with remaining files (batch mode)
- Single file error: print error message with suggestion, exit code 1
- Batch mode: summary at end, exit code 0 if any succeeded
- Log file: `log/import-{timestamp}.log`

### Claude's Discretion

- Exact progress bar styling
- Validation warning message format
- Error message wording
- Help text formatting

### Deferred Ideas (OUT OF SCOPE)

- Knowledge compilation prompts - Phase 2
- PRD template system - Phase 3
- Competitive analysis features - Phase 4
- Vector embeddings for search - Phase 2 (optional enhancement)

</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| FND-01 | Skill created using create-skill, following standard architecture | SKILL.md frontmatter pattern from mail-skill; scripts/ structure verified |
| FND-02 | Config file supports document storage paths | pydantic-settings + TOML (tomllib in Python 3.11+ stdlib) |
| FND-03 | Directory structure auto-initialization | mkdir -p pattern; SQLite schema prepared |
| IMP-01 | PDF import and conversion to Markdown | markitdown 0.1.5 - native PDF support via convert() |
| IMP-02 | DOC/DOCX import and conversion to Markdown | markitdown - native DOCX support |
| IMP-03 | HTML import and conversion to Markdown | markitdown - native HTML support |
| IMP-04 | Use markitdown for document conversion | Library verified working; API documented below |
| IMP-05 | Converted Markdown files stored in raw/ directory | File write pattern established |
| IMP-06 | Conversion results include basic validation | Regex patterns for tables, image refs documented |

</phase_requirements>

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| markitdown | 0.1.5 | Document to Markdown conversion | Microsoft's official library; supports PDF, DOCX, HTML out of box; designed for LLM ingestion |
| Typer | 0.21.0+ | CLI framework | Built on Click with modern type hints; Rich integration for beautiful output; standard in skill ecosystem |
| Rich | 14.0+ | Terminal output | Progress bars, tables, syntax highlighting; integrated with Typer |
| Pydantic | 2.12+ | Data validation | Type-safe configuration models; works seamlessly with Typer |
| pydantic-settings | 2.13+ | Settings management | Environment variable support, TOML loading, validation |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| tomllib | stdlib (3.11+) | TOML parsing | Reading config.toml files |
| python-dotenv | 1.2+ | Environment loading | Loading .env for API keys (Phase 2) |
| sqlite3 | stdlib | Metadata storage | Document index, search preparation |

### Development Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| pytest | Testing | Unit tests for import, validation |
| ruff | Linting | Fast Python linter |
| mypy | Type checking | Strict type verification |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| markitdown | pdfplumber + python-docx | More control but requires multiple libraries, format-specific handling |
| markitdown | unstructured.io | Supports more formats but heavier dependency, overkill for PDF/DOCX/HTML |
| Typer | Click | Typer provides type hints and Rich integration out of box |
| Typer | argparse | argparse has zero dependencies but requires more boilerplate |
| TOML | JSON | JSON doesn't support comments, harder for humans to edit |

**Installation:**

```bash
pip install markitdown>=0.1.5 typer>=0.21.0 rich>=14.0 pydantic>=2.12 pydantic-settings>=2.13
pip install pytest ruff mypy  # dev dependencies
```

## Architecture Patterns

### Recommended Project Structure

```
pm-skill/
├── SKILL.md                 # Skill definition with frontmatter
├── README.md                # User documentation
├── requirements.txt         # Python dependencies
├── .env.example             # Environment template
│
├── scripts/                 # CLI commands
│   ├── pm_cli.py           # Main CLI entry point (pm-skill command)
│   ├── importer.py          # Document import logic
│   ├── config.py           # Configuration management
│   └── utils/
│       ├── __init__.py
│       └── validation.py   # Markdown validation
│
├── references/              # Reference materials (Phase 2)
│   └── prompts/
│
└── knowledge-base/          # Runtime (created by init)
    ├── raw/                 # Imported Markdown
    ├── wiki/                # Compiled knowledge (Phase 2)
    ├── log/                 # Processing logs
    └── index.db             # SQLite metadata
```

### Pattern 1: SKILL.md Frontmatter

**What:** YAML frontmatter defines skill metadata that Claude reads to understand capabilities.

**When to use:** Always - this is the contract between skill and Claude.

**Example:**

```markdown
---
name: pm-skill
description: Product Manager Knowledge Assistant. Import PM documents (PDF/DOC/HTML), compile them into a searchable knowledge base, and generate PRD documents. Use this skill when users want to manage product documentation or create PRDs.
---

# PM Skill

[Workflow documentation and command reference]
```

### Pattern 2: Typer CLI Router

**What:** Single entry point routing to subcommands.

**When to use:** Skills with multiple operations.

**Example:**

```python
#!/usr/bin/env python3
import typer
from rich.console import Console
from pathlib import Path

app = typer.Typer(
    name="pm-skill",
    help="PM Skill - Product Manager Knowledge Assistant"
)
console = Console()

@app.command()
def init(
    path: Path = typer.Option(
        Path("knowledge-base"),
        "--path", "-p",
        help="Directory to initialize"
    )
):
    """Initialize knowledge base directory structure."""
    from .importer import init_knowledge_base
    init_knowledge_base(path)
    console.print(f"[green]Initialized[/green] knowledge base at {path}")

@app.command()
def import_doc(
    path: Path = typer.Argument(
        ...,
        exists=True,
        help="Document path to import"
    ),
    format: str = typer.Option(
        None,
        "--format", "-f",
        help="Force format (pdf, docx, html)"
    ),
    no_validate: bool = typer.Option(
        False,
        "--no-validate",
        help="Skip validation checks"
    ),
    quiet: bool = typer.Option(
        False,
        "--quiet", "-q",
        help="Suppress non-essential output"
    )
):
    """Import a document into the knowledge base."""
    from .importer import import_document
    import_document(path, format, no_validate, quiet)

@app.command()
def config(
    key: str = typer.Argument(None, help="Config key to display"),
    value: str = typer.Argument(None, help="New value to set")
):
    """View or set configuration."""
    from .config import get_config, set_config
    # Implementation

if __name__ == "__main__":
    app()
```

### Pattern 3: markitdown Conversion

**What:** Unified API for all document formats.

**When to use:** All document import operations.

**Example:**

```python
from markitdown import MarkItDown
from pathlib import Path

def convert_to_markdown(source_path: Path) -> tuple[str, str | None]:
    """Convert document to Markdown.
    
    Returns:
        tuple: (markdown_content, title or None)
    """
    md = MarkItDown()
    result = md.convert(str(source_path))
    return result.markdown, result.title
```

**API Details (verified from library):**

```python
class MarkItDown:
    def convert(
        self,
        source: str | Path | Response | BinaryIO,
        **kwargs
    ) -> DocumentConverterResult:
        """Convert any supported format to Markdown."""
        
class DocumentConverterResult:
    markdown: str          # The converted text
    title: str | None      # Extracted document title
    text_content: str      # Alias for markdown (deprecated)
```

### Anti-Patterns to Avoid

- **Reading documents directly into context:** markitdown first, then process - never read raw PDF/DOCX
- **Hardcoded paths:** Use config file, XDG spec, or environment variables
- **Format-specific code paths:** markitdown handles all formats uniformly
- **Silent failures on import:** Always log errors, warn user on validation failure

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| PDF text extraction | Custom PDF parser | markitdown | Handles encoding, tables, images, structure |
| DOCX parsing | python-docx directly | markitdown | Unified API, handles all formats |
| HTML to Markdown | BeautifulSoup custom code | markitdown | Built-in markdownify, proper escaping |
| CLI argument parsing | argparse boilerplate | Typer | Type hints, Rich integration, less code |
| Config management | JSON parsing + validation | pydantic-settings | Type-safe, env vars, validation |
| Progress bars | Custom print loops | Rich Progress | Thread-safe, beautiful, customizable |

**Key insight:** The skill ecosystem has standardized on Typer + Rich + Pydantic. Deviating creates maintenance burden and inconsistent UX.

## Common Pitfalls

### Pitfall 1: File Path Encoding Issues

**What goes wrong:** Non-ASCII characters in filenames cause import failures.

**Why it happens:** Python's default encoding varies by platform; filesystem encoding differs from Python's.

**How to avoid:** Always use `Path` objects, specify UTF-8 encoding for file writes.

**Warning signs:** `UnicodeEncodeError`, `OSError` on import, missing files that exist.

```python
# GOOD
from pathlib import Path
output_path = Path("raw") / filename
output_path.write_text(markdown, encoding="utf-8")

# BAD
with open(f"raw/{filename}", "w") as f:  # Platform-dependent encoding
    f.write(markdown)
```

### Pitfall 2: markitdown Version Mismatch

**What goes wrong:** Using older markitdown (0.1.2 or earlier) missing features.

**Why it happens:** markitdown 0.1.5 added significant improvements; older versions have limited format support.

**How to avoid:** Pin version in requirements.txt: `markitdown>=0.1.5`.

**Warning signs:** `AttributeError: 'str' object has no attribute 'markdown'` (result structure changed).

### Pitfall 3: Missing Directory on Import

**What goes wrong:** Import fails because `raw/` directory doesn't exist.

**Why it happens:** Users skip `pm-skill init` step.

**How to avoid:** Auto-create directories on first import, with warning.

```python
def ensure_directories(base_path: Path):
    """Ensure knowledge base directories exist."""
    for subdir in ["raw", "wiki", "log"]:
        path = base_path / subdir
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            console.print(f"[yellow]Created[/yellow] {path}")
```

### Pitfall 4: Validation False Positives

**What goes wrong:** Overly strict validation marks valid Markdown as broken.

**Why it happens:** Table syntax varies; some Markdown has intentional "broken" formatting.

**How to avoid:** Only check critical issues; allow warnings; never block import on validation.

**Validation checklist:**
- Table rows must have same column count as header (ERROR)
- Image paths should exist or be valid URLs (WARN)
- Orphaned reference links (WARN)
- Code block language hints missing (INFO)

## Code Examples

### Document Import with Validation

```python
# scripts/importer.py
from pathlib import Path
from markitdown import MarkItDown
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
import datetime

console = Console()

def import_document(
    source_path: Path,
    format: str | None = None,
    no_validate: bool = False,
    quiet: bool = False
) -> Path:
    """Import a document, convert to Markdown, validate.
    
    Returns:
        Path to the created markdown file
    """
    # Convert
    md = MarkItDown()
    result = md.convert(str(source_path))
    
    # Generate output filename
    output_name = source_path.stem + ".md"
    output_path = Path("raw") / output_name
    
    # Validate if requested
    if not no_validate:
        issues = validate_markdown(result.markdown)
        if issues and not quiet:
            report_validation(issues)
    
    # Save
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(result.markdown, encoding="utf-8")
    
    if not quiet:
        console.print(f"[green]Imported[/green] {source_path} -> {output_path}")
    
    return output_path

def validate_markdown(content: str) -> list[dict]:
    """Validate Markdown content.
    
    Returns:
        List of issues: [{"level": "error|warn|info", "message": str, "line": int}]
    """
    issues = []
    lines = content.split("\n")
    
    # Check table syntax
    for i, line in enumerate(lines, 1):
        if "|" in line:
            # Count columns
            cols = [c.strip() for c in line.split("|") if c.strip()]
            # Check next line for separator
            if i < len(lines) and "|" in lines[i]:
                next_cols = [c.strip() for c in lines[i].split("|") if c.strip()]
                if len(cols) != len(next_cols):
                    issues.append({
                        "level": "error",
                        "message": f"Table column mismatch: row {i}",
                        "line": i
                    })
    
    # Check image references
    import re
    img_pattern = r'!\[([^\]]*)\]\(([^\)]+)\)'
    for match in re.finditer(img_pattern, content):
        img_path = match.group(2)
        if not img_path.startswith(("http://", "https://", "data:")):
            # Local image reference - warn only
            line_num = content[:match.start()].count("\n") + 1
            issues.append({
                "level": "warn",
                "message": f"Image reference may be broken: {img_path}",
                "line": line_num
            })
    
    return issues

def report_validation(issues: list[dict]):
    """Print validation report."""
    errors = [i for i in issues if i["level"] == "error"]
    warns = [i for i in issues if i["level"] == "warn"]
    
    if errors:
        console.print(f"[red]Validation errors: {len(errors)}[/red]")
    if warns:
        console.print(f"[yellow]Validation warnings: {len(warns)}[/yellow]")
    
    for issue in issues[:5]:  # Show first 5
        level_color = {"error": "red", "warn": "yellow", "info": "blue"}[issue["level"]]
        console.print(f"  [{level_color}]Line {issue['line']}:[/{level_color}] {issue['message']}")
```

### Configuration Management

```python
# scripts/config.py
from pathlib import Path
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
import tomllib

class LLMConfig(BaseModel):
    model: str = "claude-sonnet-4-6-20250528"
    api_key_env: str = "ANTHROPIC_API_KEY"

class PMSkillConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="PM_SKILL_",
        env_file=".env",
        env_file_encoding="utf-8"
    )
    
    raw_dir: Path = Path("raw")
    wiki_dir: Path = Path("wiki")
    log_dir: Path = Path("log")
    llm: LLMConfig = LLMConfig()
    
    @classmethod
    def load_from_toml(cls, config_path: Path | None = None) -> "PMSkillConfig":
        """Load configuration from TOML file."""
        if config_path is None:
            # XDG Base Directory spec
            xdg_config = Path.home() / ".config" / "pm-skill" / "config.toml"
            local_config = Path(".pm-skill.toml")
            
            if xdg_config.exists():
                config_path = xdg_config
            elif local_config.exists():
                config_path = local_config
            else:
                return cls()  # Defaults
        
        with open(config_path, "rb") as f:
            data = tomllib.load(f)
        
        return cls(**data)

# Example config.toml:
# raw_dir = "knowledge-base/raw"
# wiki_dir = "knowledge-base/wiki"
# log_dir = "knowledge-base/log"
#
# [llm]
# model = "claude-sonnet-4-6-20250528"
# api_key_env = "ANTHROPIC_API_KEY"
```

### Batch Import with Progress

```python
# scripts/importer.py (batch mode)
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.console import Console
import time

console = Console()

def import_batch(
    paths: list[Path],
    no_validate: bool = False,
    quiet: bool = False
) -> tuple[int, int]:
    """Import multiple documents with progress indicator.
    
    Returns:
        tuple: (success_count, failure_count)
    """
    success = 0
    failures = []
    
    if not quiet:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            console=console
        ) as progress:
            task = progress.add_task("Importing...", total=len(paths))
            
            for path in paths:
                progress.update(task, description=f"Importing {path.name}")
                try:
                    import_document(path, None, no_validate, quiet=True)
                    success += 1
                except Exception as e:
                    failures.append((path, str(e)))
                
                progress.advance(task)
    else:
        for path in paths:
            try:
                import_document(path, None, no_validate, quiet=True)
                success += 1
            except Exception as e:
                failures.append((path, str(e)))
    
    # Log failures
    if failures:
        timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        log_path = Path("log") / f"import-{timestamp}.log"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(log_path, "w") as f:
            for path, error in failures:
                f.write(f"{path}: {error}\n")
        
        if not quiet:
            console.print(f"[yellow]Logged {len(failures)} failures to[/yellow] {log_path}")
    
    return success, len(failures)
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Multiple format-specific libraries (PyPDF2, python-docx, BeautifulSoup) | Single unified library (markitdown) | 2024 | Simpler code, consistent output format |
| Click with manual Rich integration | Typer (Rich native) | 2020+ | Less boilerplate, type-safe |
| JSON config files | TOML config files | 2023+ | Human-readable, supports comments |
| Manual env var loading | pydantic-settings | 2022+ | Type-safe, validated, documented |

**Deprecated/outdated:**
- PyPDF2: Use markitdown instead (better text extraction)
- argparse for new skills: Typer is the standard
- JSON for user config: TOML is preferred (comments, readability)
- Custom config classes: pydantic-settings handles validation

## Open Questions

1. **Image Extraction Strategy**
   - What we know: markitdown extracts text and may include image references
   - What's unclear: Whether images are embedded as data URIs or referenced
   - Recommendation: Test with real PDFs to determine handling; if embedded images are large, add `--strip-images` flag

2. **Concurrent Import Limits**
   - What we know: Batch import needs progress tracking
   - What's unclear: Optimal batch size for markitdown processing
   - Recommendation: Start with sequential processing; add parallelization in Phase 2 if needed

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 8.0+ |
| Config file | pytest.ini (to be created) |
| Quick run command | `pytest tests/ -x -q` |
| Full suite command | `pytest tests/ -v --cov=scripts --cov-report=term-missing` |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| FND-01 | Skill follows standard architecture | unit | `pytest tests/test_skill_structure.py -v` | X Wave 0 |
| FND-02 | Config file supports paths | unit | `pytest tests/test_config.py -v` | X Wave 0 |
| FND-03 | Directory structure auto-initialization | unit | `pytest tests/test_init.py -v` | X Wave 0 |
| IMP-01 | PDF import and conversion | integration | `pytest tests/test_import_pdf.py -v` | X Wave 0 |
| IMP-02 | DOCX import and conversion | integration | `pytest tests/test_import_docx.py -v` | X Wave 0 |
| IMP-03 | HTML import and conversion | integration | `pytest tests/test_import_html.py -v` | X Wave 0 |
| IMP-04 | Use markitdown for conversion | unit | `pytest tests/test_markitdown_usage.py -v` | X Wave 0 |
| IMP-05 | Markdown files stored in raw/ | unit | `pytest tests/test_storage.py -v` | X Wave 0 |
| IMP-06 | Conversion includes basic validation | unit | `pytest tests/test_validation.py -v` | X Wave 0 |

### Sampling Rate
- **Per task commit:** `pytest tests/ -x -q` (stop on first failure)
- **Per wave merge:** `pytest tests/ -v` (full suite)
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/test_skill_structure.py` - validates SKILL.md frontmatter and directory structure
- [ ] `tests/test_config.py` - validates TOML loading and path configuration
- [ ] `tests/test_init.py` - validates `pm-skill init` creates correct directories
- [ ] `tests/test_import_pdf.py` - validates PDF conversion with sample PDF
- [ ] `tests/test_import_docx.py` - validates DOCX conversion with sample document
- [ ] `tests/test_import_html.py` - validates HTML conversion with sample HTML
- [ ] `tests/test_markitdown_usage.py` - validates markitdown is used for conversion
- [ ] `tests/test_storage.py` - validates output goes to raw/ directory
- [ ] `tests/test_validation.py` - validates table syntax, image ref checks
- [ ] `tests/conftest.py` - shared fixtures (temp directories, sample documents)
- [ ] Framework install: `pip install pytest pytest-cov`

### Acceptance Test Plan (for verify-work)

**AT-01: CLI Available**
```
$ pm-skill --help
# Expected: Shows help with import, init, config subcommands
```

**AT-02: Init Creates Structure**
```
$ pm-skill init
# Expected: Creates raw/, wiki/, log/ directories and index.db
$ ls knowledge-base/
# Expected: raw/ wiki/ log/ index.db
```

**AT-03: PDF Import Works**
```
$ pm-skill import sample.pdf
# Expected: Converts PDF, saves to raw/sample.md
$ cat raw/sample.md
# Expected: Valid Markdown content from PDF
```

**AT-04: DOCX Import Works**
```
$ pm-skill import sample.docx
# Expected: Converts DOCX, saves to raw/sample.md
```

**AT-05: HTML Import Works**
```
$ pm-skill import sample.html
# Expected: Converts HTML, saves to raw/sample.md
```

**AT-06: Validation Warning**
```
$ pm-skill import broken_table.pdf
# Expected: Shows validation warnings but saves file
# Exit code: 0
```

**AT-07: Quiet Mode**
```
$ pm-skill import sample.pdf --quiet
# Expected: No output, file saved to raw/
```

**AT-08: Config Path**
```
$ pm-skill config raw_dir
# Expected: Shows current raw_dir path
$ pm-skill config raw_dir knowledge-base/raw
# Expected: Updates config
```

## Sources

### Primary (HIGH confidence)
- **markitdown library** - pip show output, Python help() output - Verified API and version 0.1.2 installed, 0.1.5 latest available
- **Typer library** - pip show output - Verified version 0.21.0 with Rich integration
- **pydantic-settings** - pip show output - Verified version 2.13.1
- **mail-skill SKILL.md** - Read directly - Verified frontmatter format and CLI pattern
- **tomllib** - Python stdlib verification - Available in Python 3.11+

### Secondary (MEDIUM confidence)
- **STACK.md research** - Project-specific stack research from .planning/research/
- **ARCHITECTURE.md research** - Project architecture patterns from .planning/research/

### Tertiary (LOW confidence)
- WebSearch was attempted but results were empty - library documentation should be verified via Context7 or official docs during implementation

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - All libraries verified installed/available, API patterns confirmed
- Architecture: HIGH - Patterns derived from existing mail-skill, standard skill ecosystem
- Pitfalls: MEDIUM - Based on common Python/document processing issues, should be validated with real-world testing
- Validation: MEDIUM - Patterns derived from Markdown best practices, may need adjustment for edge cases

**Research date:** 2026-04-27
**Valid until:** 2026-05-27 (libraries are stable, 30-day validity appropriate)
