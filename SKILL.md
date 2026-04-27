---
name: pm-skill
description: Product Manager Knowledge Assistant. Import PM documents (PDF/DOC/HTML), compile them into a searchable knowledge base, and generate PRD documents. Use this skill when users want to manage product documentation or create PRDs.
---

# PM Skill

A Claude Code skill for Product Managers to manage knowledge bases and generate PRD documents.

## Commands

### init

Initialize the knowledge base directory structure.

```bash
pm-skill init
```

Creates:
- `knowledge-base/raw/` - Imported Markdown files
- `knowledge-base/wiki/` - Compiled knowledge (Phase 2)
- `knowledge-base/log/` - Processing logs
- `knowledge-base/index.db` - SQLite metadata

### config

View or set configuration values.

```bash
pm-skill config           # Show all settings
pm-skill config raw_dir   # Show specific value
```

### import

Import documents into the knowledge base.

```bash
pm-skill import document.pdf
pm-skill import document.docx
pm-skill import document.html
pm-skill import ./docs/   # Batch import directory
```

Options:
- `--format` - Force specific format (pdf, docx, html)
- `--no-validate` - Skip validation checks
- `--quiet` - Suppress non-essential output

## Directory Structure

```
knowledge-base/
  raw/        # Imported Markdown files
  wiki/       # Compiled knowledge (Phase 2)
  log/        # Processing logs
  index.db    # SQLite metadata

~/.config/pm-skill/
  config.toml # User configuration
```

## Configuration

Configuration is loaded from (in order):
1. `~/.config/pm-skill/config.toml` (XDG Base Directory)
2. `./.pm-skill.toml` (local fallback)

Example `config.toml`:
```toml
raw_dir = "knowledge-base/raw"
wiki_dir = "knowledge-base/wiki"
log_dir = "knowledge-base/log"

[llm]
model = "claude-sonnet-4-6-20250528"
api_key_env = "ANTHROPIC_API_KEY"
```

## Use with Claude Code

When working with product documentation:

1. Import your PM documents: `pm-skill import ./my-docs/`
2. Documents are converted to Markdown and stored in `raw/`
3. Ask Claude to query or analyze your knowledge base

## Status

- Phase 1: Foundation & Document Import (current)
- Phase 2: Knowledge Compilation & Retrieval
- Phase 3: PRD Generation
- Phase 4: Competitive Analysis
