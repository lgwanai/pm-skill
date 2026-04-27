# Phase 2 Research: Knowledge Compilation & Retrieval

**Phase:** 02
**Researched:** 2026-04-27
**Confidence:** HIGH

## Key Findings

### 1. LLM Wiki Compilation Pattern
- Use anthropic SDK directly with structured prompt
- Single-file processing: read raw → call LLM → write wiki
- Prompt enforces confidence annotations (EXTRACTED/INFERRED/AMBIGUOUS/UNVERIFIED)

### 2. SQLite FTS5 Integration
- Python sqlite3 has built-in FTS5 support
- Virtual table for full-text search with porter stemming
- Rank by relevance using bm25()

### 3. Content Hash Strategy
- SHA-256 of raw file content
- Store in documents table
- Compile only when hash changes

### 4. Search Commands
- Wrap ripgrep for fallback (already available)
- FTS5 for structured wiki search
- --context flag for showing surrounding lines

## Validation Architecture

### Tests Required (Wave 0)
- tests/test_compiler.py — LLM compilation tests (mocked)
- tests/test_search.py — FTS5 and ripgrep search tests
- tests/test_wiki_structure.py — wiki page generation tests

### Acceptance Criteria
1. compile command creates wiki/entities/ pages from raw/
2. Each entity page has required sections (Overview, Content, Entities, Concepts)
3. Confidence annotations present in all extracted claims
4. search command returns results with context
5. FTS5 index properly updated after compile