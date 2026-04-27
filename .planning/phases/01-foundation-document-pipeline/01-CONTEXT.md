# Phase 1: Foundation & Document Pipeline - Context

**Gathered:** 2026-04-27
**Status:** Ready for planning

<domain>
## Phase Boundary

Create the PM Skill foundation using skill-creator workflow, including SKILL.md definition, CLI scripts for document import (PDF/DOC/HTML → Markdown), proper directory structure (raw/wiki/log), and basic configuration management. Users can import documents and have them stored as Markdown in raw/ directory.

**In scope:**
- SKILL.md with frontmatter (name, description) and workflow instructions
- CLI scripts for document import
- Directory structure initialization
- Configuration file for paths
- Basic document validation

**Out of scope:**
- Knowledge compilation (Phase 2)
- PRD generation (Phase 3)
- Search/query functionality (Phase 2)

</domain>

<decisions>
## Implementation Decisions

### CLI Command Design
- Use `pm-skill` as primary command name
- Subcommands: `import`, `init`, `config`
- Import command: `pm-skill import <path>` with optional `--format` flag (auto-detect by default)
- Output uses Rich for colored terminal output with progress indicators
- Silent mode: `--quiet` flag suppresses non-essential output

### Configuration File Format
- Location: `~/.config/pm-skill/config.toml` (XDG Base Directory specification)
- Format: TOML (human-readable, supports comments)
- Fallback: `.pm-skill.toml` in current directory
- Config includes: `raw_dir`, `wiki_dir`, `log_dir`, `llm.model`, `llm.api_key_env`

### Directory Structure
```
pm-skill/
├── SKILL.md              # Skill definition
├── scripts/
│   ├── cli.py           # Main CLI entry point
│   ├── importer.py      # Document import logic
│   └── config.py        # Configuration management
├── references/
│   └── prompts/         # LLM prompts (prepared for Phase 2)
├── requirements.txt
└── README.md

# Runtime directories (created by init):
knowledge-base/
├── raw/                 # Imported Markdown files
├── wiki/                # Compiled knowledge (Phase 2)
├── log/                 # Processing logs
└── index.db             # SQLite metadata
```

### Document Validation
- Check: table syntax (pipe alignment), image references (path exists), format integrity
- Report: validation summary with pass/warn/fail counts
- On validation failure: save file but warn user, log details
- Skip validation: `--no-validate` flag

### Error Handling
- Import errors: log to file, continue with remaining files (batch mode)
- Single file error: print error message with suggestion, exit code 1
- Batch mode: summary at end, exit code 0 if any succeeded
- Log file: `log/import-{timestamp}.log`

### Claude's Discretion
- Exact progress bar styling
- Validation warning message format
- Error message wording
- Help text formatting

</decisions>

<specifics>
## Specific Ideas

- Following skill-creator pattern from research (SKILL.md + scripts/ structure)
- Using markitdown for all document conversion (verified working in research)
- Rich library for beautiful terminal output (standard in skill ecosystem)
- SQLite for metadata storage (consistent with existing skills like mail-skill)

</specifics>

<code_context>
## Existing Code Insights

### Reusable Assets
- None yet (first phase) - but following patterns from:
  - mail-skill: CLI structure with Typer + Rich
  - echart-skill: Configuration management
  - skill-creator: SKILL.md frontmatter format

### Established Patterns
- Python 3.12+ with type hints
- Typer for CLI (built on Click with Rich integration)
- Pydantic for configuration validation
- SQLite for structured metadata

### Integration Points
- Will use `markitdown` library for document conversion
- Will use `anthropic` SDK in Phase 2 (prepare config now)
- Will use SQLite FTS5 in Phase 2 (prepare schema now)

</code_context>

<deferred>
## Deferred Ideas

- Knowledge compilation prompts — Phase 2
- PRD template system — Phase 3
- Competitive analysis features — Phase 4
- Vector embeddings for search — Phase 2 (optional enhancement)

</deferred>

---

*Phase: 01-foundation-document-pipeline*
*Context gathered: 2026-04-27*