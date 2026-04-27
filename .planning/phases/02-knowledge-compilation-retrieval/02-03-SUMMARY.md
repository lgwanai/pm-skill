---
phase: 02-knowledge-compilation-retrieval
plan: 03
subsystem: search-retrieval
tags: [cli, search, fts5, retrieval]
requires: [02-02]
provides: [search-command, list-command]
affects: [scripts/cli.py, scripts/search.py]

key-decisions:
  - "Multiple output formats (text, json, table) for all retrieval commands"
  - "Title extraction priority: frontmatter > H1 heading > filename"
  - "FTS5 snippet function for context highlighting in search results"

tech-stack:
  added: [rich-table, json-output]
  patterns: [cli-commands, title-extraction, format-polymorphism]

key-files:
  created: []
  modified:
    - scripts/cli.py (added search and list commands)
    - scripts/search.py (added format_search_results, list_wiki_pages, extract_title, get_page_context)
    - tests/test_search.py (16 new tests)

metrics:
  duration: 8 minutes
  tasks_completed: 2
  tests_added: 16
  coverage: 80% (search.py)
---

# Phase 2 Plan 3: Search and List Commands Summary

## One-liner

Implemented CLI search and list commands with FTS5 full-text search backend, supporting multiple output formats (text, json, table) and context-aware result formatting.

## What Was Built

### Search Command

- `pm-skill search <query>` - FTS5-powered full-text search across wiki pages
- Options: `--context` (context lines), `--format` (text/json/table), `--scope` (entity/concept/all), `--limit` (max results)
- BM25 ranking for relevance scoring
- Snippet generation with match highlighting

### List Command

- `pm-skill list` - List all wiki pages with metadata
- Options: `--scope` (entity/concept/all), `--format` (text/json/table)
- Title extraction from frontmatter, heading, or filename

### Helper Functions

- `format_search_results()` - Polymorphic output formatting (text, json, table)
- `get_page_context()` - Extract surrounding lines around a match
- `list_wiki_pages()` - Enumerate wiki pages with metadata
- `extract_title()` - Priority-based title extraction

## Key Decisions

1. **Multiple output formats**: Supports text (human-readable), json (machine-readable), and table (Rich-formatted) for flexibility in scripting and interactive use.

2. **Title extraction priority**: YAML frontmatter > H1 heading > filename. This ensures semantic titles are preferred while falling back to filename.

3. **FTS5 snippet function**: Uses SQLite FTS5's built-in `snippet()` function for context highlighting rather than custom implementation.

## Deviations from Plan

None - plan executed exactly as written.

## Tests Added

16 tests covering:

- FTS5 search (basic, scope filtering, limiting)
- Context line extraction
- Output format rendering (json, table, text)
- List entities and concepts
- Title extraction from all sources
- CLI command help

## Files Modified

| File | Changes |
|------|---------|
| scripts/cli.py | Added `search` and `list` commands with full option support |
| scripts/search.py | Added formatting, listing, and title extraction functions |
| tests/test_search.py | 16 comprehensive tests for all functionality |

## Verification

```bash
# All tests pass
pytest tests/test_search.py -v

# CLI commands work
pm-skill search --help
pm-skill list --help
```

## Self-Check: PASSED

- scripts/cli.py - FOUND
- scripts/search.py - FOUND
- tests/test_search.py - FOUND
- 02-03-SUMMARY.md - FOUND
- Commit 122a37d - FOUND
