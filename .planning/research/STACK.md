# Stack Research

**Domain:** Claude Code Skill Development
**Researched:** 2026-04-27
**Confidence:** HIGH

## Recommended Stack

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| Python | 3.12+ | Primary language | Claude Code skills standardize on Python for CLI tools; excellent ecosystem for document processing and LLM integration |
| markitdown | 0.1.5 | Document to Markdown conversion | Microsoft's official library; supports PDF, DOCX, HTML, PPTX, XLSX out of the box; specifically designed for LLM ingestion |
| SQLite | 3.x | Knowledge storage | Lightweight, zero-config, built into Python; used in existing skills (echart-skill, mail-skill) for structured document metadata |
| Typer | 0.25.0 | CLI framework | Built on Click with modern type hints; rich terminal output via Rich integration; standard in Claude Code skill ecosystem |
| Pydantic | 2.12+ | Data validation | Type-safe configuration and data models; works seamlessly with Typer; used throughout skill ecosystem |

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| anthropic | 0.97.0 | Claude API client | Knowledge compilation (raw → wiki) and PRD generation |
| python-dotenv | 1.2.2 | Environment management | Loading API keys and configuration from .env files |
| pydantic-settings | 2.13+ | Settings management | Structured configuration with environment variable support |
| httpx | 0.28+ | HTTP client | API calls to Claude and other services; async support for batch processing |
| Rich | 14.0+ | Terminal output | Progress bars, tables, syntax highlighting in CLI |

### Development Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| pytest | Testing | Unit and integration tests targeting 80%+ coverage |
| ruff | Linting | Fast Python linter, replaces flake/black/isort |
| mypy | Type checking | Strict type verification for Pydantic models |

## Skill Architecture

Claude Code Skills follow a standardized structure:

```
skill-name/
  SKILL.md           # Skill definition with frontmatter (name, description)
  scripts/           # Executable Python scripts
    cli.py           # Main CLI entry point
    importer.py      # Document import logic
    compiler.py      # Knowledge compilation logic
  references/        # Static reference materials
    prompts/         # LLM prompts for specific tasks
  assets/            # Static assets (icons, templates)
  config.txt         # Configuration (copy example to customize)
  requirements.txt   # Python dependencies
```

**Key architectural decisions:**

1. **SKILL.md is the contract** - Contains frontmatter with `name` and `description` fields; the skill's behavior is encoded in this file, not in code
2. **CLI scripts are invoked by Claude** - Claude reads SKILL.md and executes the scripts based on user requests
3. **Configuration is file-based** - Use .env for secrets, config.txt or config.json for user preferences
4. **SQLite for structured data** - Document metadata, knowledge index, and session state

## Installation

```bash
# Core
pip install markitdown>=0.1.5 typer>=0.25.0 pydantic>=2.12 pydantic-settings>=2.13

# API and utilities
pip install anthropic>=0.97.0 python-dotenv>=1.2.0 httpx>=0.28.0 rich>=14.0

# Dev dependencies
pip install pytest ruff mypy
```

## Document Processing Strategy

### markitdown Capabilities

**Supported formats (HIGH confidence - verified working):**
- PDF (.pdf) - text extraction with structure preservation
- Word (.docx, .doc) - full document structure
- PowerPoint (.pptx) - slide content extraction
- Excel (.xlsx, .xls) - tabular data extraction
- HTML (.html, .htm) - web page content
- Text files (.txt, .md, .csv) - passthrough

**API pattern:**
```python
from markitdown import MarkItDown

md = MarkItDown()
result = md.convert("document.pdf")
markdown_content = result.text_content
```

**Key design decision:** markitdown handles all document formats uniformly - no need for format-specific parsers.

### Knowledge Storage Structure

Following the LLM Wiki methodology, organize knowledge as:

```
raw/           # Original documents (PDF, DOCX, etc.)
wiki/          # Compiled Markdown knowledge files
log/           # Processing logs and metadata
workspace.db   # SQLite index of all documents
```

**SQLite schema:**
```sql
CREATE TABLE documents (
    id TEXT PRIMARY KEY,
    path TEXT NOT NULL,
    original_path TEXT,
    format TEXT,
    title TEXT,
    created_at TIMESTAMP,
    compiled_at TIMESTAMP,
    status TEXT  -- 'raw', 'compiled', 'error'
);

CREATE TABLE knowledge_chunks (
    id TEXT PRIMARY KEY,
    document_id TEXT,
    content TEXT,
    embedding BLOB,  -- For semantic search (optional)
    metadata JSON
);
```

## LLM Integration

### Claude API for Knowledge Compilation

Use Claude to transform raw documents into structured wiki format:

```python
from anthropic import Anthropic

client = Anthropic()  # Reads ANTHROPIC_API_KEY from env

response = client.messages.create(
    model="claude-sonnet-4-6-20250528",
    max_tokens=4096,
    system="You are a knowledge compiler. Transform documents into structured wiki format...",
    messages=[{"role": "user", "content": markdown_content}]
)
```

**Model selection for skill:**
- Sonnet 4.6 - Knowledge compilation, PRD writing (balanced quality/cost)
- Haiku 4.5 - Quick queries, simple summarization

### Embedding Strategy (Optional)

For semantic search in the knowledge base:

| Option | Library | When to Use |
|--------|---------|-------------|
| Local embeddings | sentence-transformers 5.4+ | Offline, no API costs, moderate quality |
| Claude embeddings | anthropic SDK via Voyage AI | Best quality, requires API calls |
| No embeddings | SQLite full-text search (FTS5) | Simple keyword search, zero setup |

**Recommendation:** Start with SQLite FTS5 for simplicity. Add embeddings only if retrieval quality is insufficient.

## CLI Design Pattern

Following existing skills (mail-skill, echart-skill):

```python
# scripts/cli.py
import typer
from rich.console import Console

app = typer.Typer(help="PM Skill - Product Manager Knowledge Assistant")
console = Console()

@app.command()
def import_doc(path: str):
    """Import a document into the knowledge base."""
    console.print(f"[blue]Importing[/blue] {path}...")
    # Use markitdown to convert
    # Store in raw/ and index in SQLite

@app.command()
def compile_knowledge():
    """Compile raw documents into wiki format."""
    console.print("[green]Compiling knowledge base...[/green]")
    # Use Claude API to process documents
    # Output to wiki/

@app.command()
def query(query: str):
    """Query the knowledge base."""
    # Full-text search or semantic search
    pass

if __name__ == "__main__":
    app()
```

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| markitdown | pdfplumber + python-docx | When you need fine-grained control over PDF extraction or custom formatting |
| markitdown | unstructured.io | When processing many diverse formats (images, audio transcripts) |
| SQLite | ChromaDB | When you need built-in vector search from day one |
| SQLite | LanceDB | When you need columnar storage for analytics on documents |
| Typer | Click | When you don't need type hints or Rich integration |
| Typer | argparse | When you want zero dependencies beyond stdlib |

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| LangChain | Over-engineered for single-purpose skills; adds complexity without benefit | Direct anthropic SDK calls |
| Local LLMs (Ollama, LM Studio) | Inconsistent quality for structured PRD writing | Claude API for reliable output |
| Heavy ORMs (SQLAlchemy) | Overkill for simple document metadata | sqlite3 directly or sqlite-utils |
| Pandas for document storage | Not designed for text storage; memory inefficient for large documents | SQLite with TEXT columns |
| JSON files for knowledge storage | No query capability, hard to search | SQLite with FTS5 |

## Stack Patterns by Variant

**If team already uses Node.js:**
- Use Python only for markitdown (via subprocess)
- Implement CLI in Node with commander/yargs
- Keep SQLite for storage (better than JSON)

**If embedding quality is critical:**
- Use `sentence-transformers` with `all-MiniLM-L6-v2` model
- Store vectors in SQLite as BLOB (simpler than ChromaDB)
- Add vector similarity search in Python

**If offline operation is required:**
- Cache Claude API responses locally
- Use sentence-transformers for local embeddings
- Pre-compile knowledge in online mode, query offline

## Version Compatibility

| Package A | Compatible With | Notes |
|-----------|-----------------|-------|
| markitdown 0.1.5 | Python 3.9+ | Uses magika for file type detection |
| typer 0.25+ | click 8.3+ | Typer now independent of Click API changes |
| anthropic 0.97+ | httpx 0.28+ | Sync and async support |
| pydantic 2.12+ | pydantic-settings 2.13+ | Settings management requires pydantic v2 |

## Sources

- **markitdown** - PyPI package inspection, Python help() output - HIGH confidence (verified working)
- **Typer/Click** - pip show output, pip index versions - HIGH confidence
- **Skill architecture** - Examined existing skills (mail-skill, echart-skill, follow-builders) - HIGH confidence
- **Claude Code CLI** - `claude --help` output - HIGH confidence
- **ChromaDB vs SQLite** - pip show output, ecosystem knowledge - MEDIUM confidence (WebSearch unavailable)

---
*Stack research for: Claude Code Skill Development*
*Researched: 2026-04-27*
