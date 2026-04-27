# Architecture Research

**Domain:** Claude Code Skills - Product Manager Assistant
**Researched:** 2026-04-27
**Confidence:** HIGH

## Standard Architecture

### System Overview

```
+------------------------------------------------------------------+
|                        PM Skill (SKILL.md)                        |
|  [Description + Workflow Documentation + Command Reference]       |
+------------------------------------------------------------------+
|                           CLI Layer                               |
|  +-------------+  +-------------+  +-------------+               |
|  |   pm-cli    |  |   search    |  |   compile   |               |
|  |  (router)   |  |  (query)    |  |  (pipeline) |               |
|  +------+------+  +------+------+  +------+------+               |
|         |                |                |                       |
+---------+----------------+----------------+-----------------------+
|                      Processing Layer                              |
|  +--------------------+  +--------------------+                   |
|  | Document Processor |  | Knowledge Compiler |                   |
|  |  (markitdown)      |  |    (LLM API)       |                   |
|  +---------+----------+  +---------+----------+                   |
|            |                       |                               |
+------------+-----------------------+-------------------------------+
|                        Storage Layer                               |
|  +------------+  +------------+  +------------+  +------------+  |
|  |   raw/     |  |   wiki/    |  |   log/     |  |  index.db  |  |
|  | (original) |  | (compiled) |  |  (ops)     |  |  (search)  |  |
|  +------------+  +------------+  +------------+  +------------+  |
+-------------------------------------------------------------------+
```

### Component Responsibilities

| Component | Responsibility | Typical Implementation |
|-----------|----------------|------------------------|
| SKILL.md | Skill definition, workflow docs, command reference | Markdown with YAML frontmatter |
| scripts/ | Executable CLI commands | Python CLI (argparse/click) |
| references/ | Deep-dive documentation, PRD templates, examples | Markdown files |
| templates/ | Ready-to-use PRD templates by product type | Markdown with placeholders |
| raw/ | Original document storage (PDF, DOCX, HTML, etc.) | File system, organized by source |
| wiki/ | Compiled knowledge in LLM-ready format | Markdown files with metadata |
| log/ | Operation logs, compilation history | JSONL files |
| index.db | Search index for knowledge retrieval | SQLite with FTS5 |

## Recommended Project Structure

```
pm-skill/
├── SKILL.md                    # Main skill definition (entry point)
├── README.md                   # User documentation
├── requirements.txt            # Python dependencies
├── .env.example                # Environment template
│
├── scripts/                    # CLI commands
│   ├── pm_cli.py               # Main CLI router
│   ├── doc_ingest.py           # Document ingestion (raw/)
│   ├── doc_convert.py          # Format conversion (markitdown)
│   ├── knowledge_compile.py    # Raw -> Wiki compilation
│   ├── knowledge_search.py     # Search/index operations
│   ├── prd_generate.py         # PRD generation
│   └── utils/                  # Shared utilities
│       ├── __init__.py
│       ├── llm_client.py       # LLM API wrapper
│       ├── file_ops.py         # File operations
│       └── config.py           # Configuration loader
│
├── references/                 # Deep-dive documentation
│   ├── prd-templates/          # PRD templates by type
│   │   ├── toc-product.md      # ToC consumer product
│   │   ├── tob-product.md      # ToB enterprise product
│   │   ├── backend-system.md   # Backend admin system
│   │   └── mini-program.md     # Mini program (WeChat, etc.)
│   ├── workflows/              # Workflow guides
│   │   ├── competitive-analysis.md
│   │   └── knowledge-management.md
│   └── llm-wiki-method.md      # LLM Wiki methodology reference
│
├── data/                       # Local data storage
│   ├── raw/                    # Original documents
│   │   ├── pdf/
│   │   ├── docx/
│   │   └── html/
│   ├── wiki/                   # Compiled knowledge
│   │   └── *.md                # LLM-optimized markdown
│   ├── log/                    # Operation logs
│   │   ├── compile.jsonl       # Compilation history
│   │   └── search.jsonl        # Search history
│   └── index.db                # SQLite search index
│
└── config/                     # Configuration
    ├── default.json            # Default settings
    └── prd-prompts/            # PRD generation prompts
        ├── requirement-collect.md
        └── prd-draft.md
```

### Structure Rationale

- **scripts/**: All CLI commands as separate modules for maintainability. Main router delegates to subcommands.
- **references/**: PRD templates and workflow guides that Claude can reference during PRD generation.
- **data/**: Follows LLM Wiki methodology (raw -> wiki -> log) with added index.db for search.
- **config/**: Separate configuration directory for prompts and settings.

## Architectural Patterns

### Pattern 1: LLM Wiki Pipeline (Raw -> Wiki -> Log)

**What:** Three-stage document lifecycle from Karpathy's LLM Wiki methodology.

**When to use:** All document-based knowledge management.

**Trade-offs:**
- Pros: Clear separation of concerns, audit trail, reproducible
- Cons: More storage, requires explicit compilation step

**Example:**
```python
# Document lifecycle
raw/document.pdf          # Original document
    ↓ (markitdown convert)
raw/document.md           # Intermediate markdown
    ↓ (LLM compile)
wiki/document.md          # Compiled knowledge with metadata
    ↓ (search index)
index.db                  # Full-text search index
```

### Pattern 2: CLI Router with Subcommands

**What:** Single entry point (pm_cli.py) routing to specialized handlers.

**When to use:** Skills with multiple operations (ingest, compile, search, generate).

**Trade-offs:**
- Pros: Consistent interface, easy to extend, testable
- Cons: Slightly more complex than single-file scripts

**Example:**
```python
# pm_cli.py
import click

@click.group()
def cli():
    """PM Skill - Product Manager Assistant"""
    pass

@cli.command()
@click.argument('path', type=click.Path(exists=True))
def ingest(path):
    """Ingest document into raw/ directory"""
    from .doc_ingest import ingest_document
    ingest_document(path)

@cli.command()
@click.option('--all', is_flag=True)
def compile(all):
    """Compile raw documents to wiki knowledge"""
    from .knowledge_compile import compile_all
    compile_all()

@cli.command()
@click.argument('query')
def search(query):
    """Search knowledge base"""
    from .knowledge_search import search_knowledge
    search_knowledge(query)

@cli.command()
@click.option('--type', type=click.Choice(['toc', 'tob', 'backend', 'mini']))
def prd(type):
    """Generate PRD with multi-round collection"""
    from .prd_generate import generate_prd
    generate_prd(type)
```

### Pattern 3: Template-Based PRD Generation

**What:** PRD generation uses templates with multi-round information collection.

**When to use:** Structured document generation with LLM assistance.

**Trade-offs:**
- Pros: Consistent output, customizable, knowledge-context-aware
- Cons: Requires template maintenance

**Example:**
```python
# PRD generation flow
def generate_prd(product_type):
    # 1. Load template
    template = load_template(f"references/prd-templates/{product_type}.md")
    
    # 2. Multi-round collection
    requirements = collect_requirements(product_type)
    
    # 3. Search relevant knowledge
    context = search_knowledge(requirements.keywords)
    
    # 4. Generate with context
    prd = llm_generate(template, requirements, context)
    
    return prd
```

## Data Flow

### Document Ingestion Flow

```
[User: pm ingest document.pdf]
        ↓
[doc_ingest.py] → Validate format → Copy to raw/pdf/
        ↓
[doc_convert.py] → markitdown convert → raw/document.md
        ↓
[knowledge_compile.py] → LLM compile → wiki/document.md
        ↓
[index.db] → Update FTS index
```

### PRD Generation Flow

```
[User: pm prd --type toc]
        ↓
[prd_generate.py] → Load template → references/prd-templates/toc-product.md
        ↓
[Multi-round collection] → Collect requirements via LLM dialogue
        ↓
[knowledge_search.py] → Query index.db for relevant context
        ↓
[LLM generate] → Combine template + requirements + context → Output PRD
```

### Knowledge Search Flow

```
[User: pm search "user authentication"]
        ↓
[knowledge_search.py] → Query index.db FTS5
        ↓
[Rank results] → Relevance scoring
        ↓
[Return] → List of wiki/*.md paths with snippets
```

### Key Data Flows

1. **Ingestion:** User document -> raw/ -> markdown -> wiki/ -> index.db
2. **Compilation:** raw/*.md -> LLM API -> wiki/*.md (with metadata)
3. **Search:** Query -> index.db -> wiki paths -> Context retrieval
4. **Generation:** Template + Requirements + Knowledge Context -> PRD

## Scaling Considerations

| Scale | Architecture Adjustments |
|-------|--------------------------|
| 0-100 documents | SQLite FTS5, file-based storage, single-threaded compile |
| 100-1000 documents | Batch compilation, parallel LLM calls, optimize index |
| 1000+ documents | Consider vector embeddings, external search (Meilisearch), caching |

### Scaling Priorities

1. **First bottleneck:** LLM API rate limits during compilation. Fix: Batch processing, retry logic, rate limiting.
2. **Second bottleneck:** Search latency with large knowledge base. Fix: Add vector embeddings for semantic search.

## Anti-Patterns

### Anti-Pattern 1: Reading Documents into Context Window

**What people do:** Reading entire PDF/DOCX content directly into context.

**Why it's wrong:** Consumes massive context tokens, truncates large documents, slow and expensive.

**Do this instead:** Use markitdown to convert to markdown first, then process in wiki/ with metadata and chunking.

### Anti-Pattern 2: Storing Knowledge Without Indexing

**What people do:** Storing compiled wiki/*.md files without search index.

**Why it's wrong:** Can't retrieve relevant knowledge efficiently, defeats purpose of knowledge base.

**Do this instead:** Always update index.db after compilation. Use SQLite FTS5 for full-text search.

### Anti-Pattern 3: Hardcoded PRD Templates

**What people do:** Embedding PRD templates directly in code.

**Why it's wrong:** Hard to customize, requires code changes for template updates.

**Do this instead:** Store templates in references/prd-templates/ as markdown files. Allow user customization.

### Anti-Pattern 4: Single-Shot PRD Generation

**What people do:** Generating PRD in one LLM call with minimal input.

**Why it's wrong:** Missing critical details, generic output, doesn't leverage knowledge base.

**Do this instead:** Multi-round dialogue to collect requirements, then search knowledge base for context, then generate.

## Integration Points

### External Services

| Service | Integration Pattern | Notes |
|---------|---------------------|-------|
| markitdown | CLI subprocess call | Document conversion (PDF, DOCX, HTML -> MD) |
| LLM API | HTTP client (requests/httpx) | Knowledge compilation, PRD generation |
| OpenAI/Anthropic | API key via .env | Primary LLM providers |

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| CLI -> Scripts | Python imports | Direct function calls |
| Scripts -> Storage | File system + SQLite | Read/write files, SQL queries |
| Scripts -> LLM | HTTP client | Async preferred for batch operations |

## Build Order Implications

Based on dependencies between components, recommended build order:

### Phase 1: Foundation (Core Infrastructure)
1. **SKILL.md** - Define skill interface and workflow
2. **scripts/utils/** - Configuration loader, file operations
3. **scripts/doc_convert.py** - markitdown integration
4. **data/raw/** - Directory structure

### Phase 2: Document Pipeline
1. **scripts/doc_ingest.py** - Document ingestion
2. **scripts/utils/llm_client.py** - LLM API wrapper
3. **scripts/knowledge_compile.py** - Raw -> Wiki compilation
4. **data/wiki/** - Compiled knowledge storage
5. **data/log/** - Operation logging

### Phase 3: Knowledge Retrieval
1. **scripts/knowledge_search.py** - Search functionality
2. **data/index.db** - SQLite FTS5 index
3. Index update on compilation

### Phase 4: PRD Generation
1. **references/prd-templates/** - PRD templates by type
2. **config/prd-prompts/** - Generation prompts
3. **scripts/prd_generate.py** - PRD generation with context
4. **scripts/pm_cli.py** - Main CLI router (final integration)

### Phase 5: Polish
1. **references/workflows/** - Workflow documentation
2. **README.md** - User documentation
3. Error handling, validation, testing

## Sources

- Claude Code Skills: Analyzed agent-browser, mail-skill, echart-skill, follow-builders (local installation)
- markitdown: Local installation v0.1.2, CLI help documentation
- LLM Wiki methodology: Referenced from PROJECT.md (Karpathy gist)

---
*Architecture research for: PM Skill*
*Researched: 2026-04-27*
