# Phase 2: Knowledge Compilation & Retrieval - Context

**Gathered:** 2026-04-27
**Status:** Ready for planning

<domain>
## Phase Boundary

Transform raw Markdown documents into structured wiki knowledge using LLM-powered compilation. Enable CLI-based search and retrieval for the compiled knowledge base. Users can compile documents and search/query the knowledge.

**In scope:**
- Knowledge compilation (raw → wiki transformation)
- Entity and concept page generation
- Index and glossary maintenance
- LLM API integration for compilation
- Confidence annotations in compiled output
- CLI search commands (rg, find, grep wrappers)
- SQLite FTS5 full-text search

**Out of scope:**
- PRD generation (Phase 3)
- Competitive analysis (Phase 4)
- Vector embeddings (optional future enhancement)

</domain>

<decisions>
## Implementation Decisions

### Compile Command Design
- Command: `pm-skill compile [options]`
- Default: compile all files in raw/ directory
- Options:
  - `--file <path>` — compile single file
  - `--force` — recompile even if hash matches
  - `--dry-run` — show what would be compiled without executing
  - `--model <model>` — override LLM model from config
- Output: Rich progress indicator, summary with counts (entities, concepts, terms)

### LLM Integration
- Use anthropic SDK directly (not LangChain)
- Model from config: `llm.model` (default: claude-sonnet-4-6)
- API key from environment: `llm.api_key_env` (default: ANTHROPIC_API_KEY)
- Prompt stored in `references/prompts/compile.md`
- Batch processing: one file at a time (parallel in future if needed)

### Compilation Prompt Structure
The prompt for compiling raw → wiki follows LLM Wiki methodology:
```
You are a knowledge compiler. Transform the document into structured wiki format.

Output sections:
1. **Overview** — document purpose, source, key information
2. **Key Content** — extracted main content summary
3. **Entities** — specific items mentioned (products, features, APIs)
4. **Concepts** — abstract ideas that span multiple documents
5. **Relations** — links to other documents/concepts

Confidence annotation per claim:
- EXTRACTED — directly stated in source
- INFERRED — logically derived from source
- AMBIGUOUS — unclear or multiple interpretations
- UNVERIFIED — needs external validation
```

### Wiki Page Structure
```
wiki/
├── entities/
│   └── {source-file-name}.md     — one page per raw document
├── concepts/
│   └── {concept-name}.md         — auto-extracted concepts
├── index.md                      — navigable knowledge map
├── glossary.md                   — terminology definitions
└── relations.md                  — cross-reference links (optional)
```

Each entity page includes:
- Source file reference
- Document overview
- Key content summary
- Extracted entities list
- Related concepts
- Confidence annotations

### Search Command Design
- Command: `pm-skill search <query> [options]`
- Options:
  - `--context <n>` — show n lines of context (default: 3)
  - `--format <fmt>` — output format: text, json, table
  - `--scope <dir>` — search in entities, concepts, or all
  - `--limit <n>` — max results (default: 20)
- Backend: SQLite FTS5 for structured search, ripgrep for fallback/raw search

### List Command
- Command: `pm-skill list [options]`
- Options:
  - `--scope <dir>` — list entities, concepts, or all
  - `--format <fmt>` — output format: text, json
- Output: file names with titles (from frontmatter/first heading)

### SQLite FTS5 Schema
```sql
-- Update existing index.db with FTS5
CREATE VIRTUAL TABLE IF NOT EXISTS wiki_search USING fts5(
  path,
  title,
  content,
  type,        -- 'entity' or 'concept'
  tokenize = 'porter unicode61'
);

-- Index all wiki pages on compile
INSERT INTO wiki_search(path, title, content, type)
VALUES ('wiki/entities/{name}.md', '{title}', '{content}', 'entity');
```

### Content Hash for Consistency
- Store SHA-256 hash of raw file content in SQLite
- On compile: check if hash changed → recompile only changed files
- Prevents stale wiki when raw updates

### Claude's Discretion
- Exact prompt wording for compilation
- Entity/concept naming conventions
- Cross-reference link format
- Progress bar design for compilation
- Search result formatting

</decisions>

<specifics>
## Specific Ideas

- LLM Wiki methodology from Karpathy: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
- Confidence annotations prevent hallucination in downstream PRD generation
- FTS5 provides fast search without vector embeddings (add embeddings later if needed)
- Content hash ensures wiki stays synchronized with raw

</specifics>

<code_context>
## Existing Code Insights

### Reusable Assets from Phase 1
- `scripts/cli.py` — add compile and search subcommands
- `scripts/config.py` — already has llm.model and llm.api_key_env
- `scripts/utils/init.py` — creates wiki/ directory structure
- `SQLite schema in index.db` — extend with wiki_search FTS5 table

### Established Patterns
- Typer for CLI (same pattern as import command)
- Rich for progress/output (consistent with Phase 1)
- Pydantic for config validation (already in use)
- TOML configuration (same format)

### Integration Points
- `scripts/importer.py` — importer stores hash in SQLite after import
- `scripts/config.py` — compile uses LLM config fields
- New files needed:
  - `scripts/compiler.py` — LLM-powered compilation
  - `scripts/search.py` — FTS5 and ripgrep search
  - `references/prompts/compile.md` — compilation prompt template

</code_context>

<deferred>
## Deferred Ideas

- Vector embeddings for semantic search — Phase 2 optional enhancement, add if FTS5 insufficient
- Parallel batch compilation — future optimization for large document sets
- Knowledge graph visualization — Phase 4+ feature
- Automatic cross-reference discovery enhancement — iterative improvement

</deferred>

---

*Phase: 02-knowledge-compilation-retrieval*
*Context gathered: 2026-04-27*