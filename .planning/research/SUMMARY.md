# Project Research Summary

**Project:** PM Skill
**Domain:** Claude Code Skill Development / LLM-powered Knowledge Management
**Researched:** 2026-04-27
**Confidence:** HIGH

## Executive Summary

PM Skill is a Claude Code Skill that implements a Product Manager knowledge assistant following Karpathy's LLM Wiki methodology. The skill ingests PM documents (PDFs, DOCX, HTML), compiles them into structured wiki knowledge, and uses that knowledge to enhance PRD generation. The recommended approach uses Python with markitdown for document conversion, SQLite with FTS5 for search, and direct Anthropic API calls for LLM operations — deliberately avoiding over-engineered frameworks like LangChain.

The architecture follows a three-stage pipeline: raw documents -> compiled wiki -> searchable index. This is the core innovation from the LLM Wiki methodology, where documents are transformed by LLMs into structured knowledge with entities, concepts, and cross-links. PRD generation then leverages this knowledge base through multi-round requirement collection and context-aware generation with source attribution.

Key risks include LLM hallucination in PRD generation (mitigate with mandatory source citations), knowledge base consistency after updates (mitigate with content hashing and cascade updates), and context window overflow with large knowledge bases (mitigate with hierarchical loading and relevance-based retrieval). These must be addressed during implementation, not deferred.

## Key Findings

### Recommended Stack

Python-based CLI skill using markitdown for document conversion, SQLite with FTS5 for search, and direct Anthropic API for LLM operations. The stack prioritizes simplicity over framework complexity — Typer for CLI, Pydantic for validation, and file-based storage following the skill ecosystem patterns observed in mail-skill, echart-skill, and follow-builders.

**Core technologies:**
- Python 3.12+ — Primary language, standard for Claude Code skills
- markitdown 0.1.5 — Document to Markdown conversion, supports PDF/DOCX/HTML out of the box
- SQLite with FTS5 — Knowledge storage with full-text search, zero configuration
- Typer 0.25+ — CLI framework with Rich integration for terminal output
- Pydantic 2.12+ — Data validation and configuration management
- anthropic SDK 0.97+ — Direct API calls for knowledge compilation and PRD generation

### Expected Features

**Must have (table stakes):**
- Document import (PDF/DOC/HTML to Markdown) — Entry point, users expect frictionless document addition
- Directory structure (raw/wiki/log) — Foundation for LLM Wiki methodology
- CLI query commands — Basic usability for a CLI skill
- PRD templates (ToC/ToB/Backend/Mini-program) — Immediate value delivery
- Basic PRD writing with multi-turn input collection — Core user workflow

**Should have (competitive):**
- LLM Wiki compilation — Core innovation, transforms raw docs into structured wiki
- Knowledge-enhanced PRD — PRD generation augmented by automatic knowledge retrieval
- Iterative knowledge retrieval — Retrieve until knowledge exhausted
- Entity extraction — Auto-identify concepts, features, interfaces
- Conflict detection — Flag contradictions between user input and knowledge base
- Risk assessment — Auto-evaluate implementation cost and risks

**Defer (v2+):**
- Competitive analysis features — Requires more structured approach
- Multiple knowledge bases — Multi-project support
- Export formats (HTML, PDF) — Distribution beyond Markdown
- API for programmatic access — Integration potential

### Architecture Approach

Three-tier architecture: CLI Layer (pm_cli.py router with subcommands for ingest/compile/search/prd), Processing Layer (markitdown for conversion, LLM API for compilation), and Storage Layer (raw/wiki/log directories plus index.db). Follows the LLM Wiki methodology where raw documents are compiled into wiki knowledge with entities, concepts, and cross-links.

**Major components:**
1. SKILL.md — Skill definition with frontmatter, workflow documentation, command reference
2. scripts/ — CLI commands (ingest, compile, search, prd) plus utilities
3. references/ — PRD templates by product type, workflow guides
4. data/ — raw/ (original documents), wiki/ (compiled knowledge), log/ (operations), index.db (FTS5)

### Critical Pitfalls

1. **Knowledge base consistency after updates** — When source documents change, wiki pages become stale. Prevent with content hashing (SHA256) to detect changes, maintain raw->wiki mapping cache, and cascade updates/deletions.

2. **LLM hallucination in PRD generation** — LLMs fabricate features not in source material. Prevent with mandatory source attribution format `[claim] (source: [[wiki/page]])`, confidence annotations (EXTRACTED/INFERRED/AMBIGUOUS), and validation step that flags unverified content.

3. **Context window overflow with large knowledge bases** — Loading all wiki pages exhausts context. Prevent with hierarchical loading (index -> topics -> sources), embedding-based relevance scoring, and explicit token budget tracking.

4. **Document conversion edge cases** — Tables, images, code blocks convert poorly. Prevent with format-specific preprocessing, post-conversion validation, and fallback LLM prompts to fix obvious issues.

5. **Orphaned and isolated knowledge** — Wiki pages created without links to existing content. Prevent by scanning for related pages during ingestion and implementing periodic lint/healing to suggest cross-references.

## Implications for Roadmap

Based on research, suggested phase structure:

### Phase 1: Foundation and Document Pipeline
**Rationale:** Core infrastructure must exist before any higher-level features. Document conversion is the entry point for all knowledge.
**Delivers:** Working document import, conversion, and storage following LLM Wiki methodology
**Addresses:** Document import, directory structure, CLI commands (from FEATURES.md)
**Avoids:** Document conversion edge cases (Pitfall 4) — build validation from the start
**Uses:** markitdown, Typer, Pydantic (from STACK.md)
**Implements:** CLI Layer, Storage Layer directories (from ARCHITECTURE.md)

### Phase 2: Knowledge Base Compilation
**Rationale:** Raw documents must be compiled into wiki before any search or PRD features work. This is the core innovation.
**Delivers:** LLM-powered compilation of raw documents into structured wiki knowledge with entities and cross-links
**Addresses:** LLM Wiki compilation (from FEATURES.md)
**Avoids:** Knowledge base consistency (Pitfall 1), context window overflow (Pitfall 3), query relevance (Pitfall 5), orphaned knowledge (Pitfall 6) — build these mitigations into compilation
**Uses:** anthropic SDK, SQLite FTS5 (from STACK.md)
**Implements:** Processing Layer, index.db (from ARCHITECTURE.md)

### Phase 3: PRD Generation
**Rationale:** PRD generation depends on working knowledge base. This is the primary user value.
**Delivers:** Template-based PRD generation with multi-round requirement collection and knowledge context
**Addresses:** PRD templates, PRD writing (from FEATURES.md)
**Avoids:** LLM hallucination (Pitfall 2) — build source attribution into generation
**Uses:** PRD templates, generation prompts (from ARCHITECTURE.md)

### Phase 4: Knowledge Enhancement
**Rationale:** Adds competitive differentiation once core functionality is validated.
**Delivers:** Knowledge-enhanced PRD, iterative retrieval, entity extraction, conflict detection, risk assessment
**Addresses:** Differentiator features (from FEATURES.md)
**Uses:** Knowledge retrieval integration (from ARCHITECTURE.md)

### Phase 5: Polish and Extension
**Rationale:** Documentation, error handling, and v2 feature preparation.
**Delivers:** Complete documentation, robust error handling, workflow guides
**Addresses:** Anti-features education, v2 feature planning (from FEATURES.md)

### Phase Ordering Rationale

- **Phase 1 first:** Document import is the entry point. Without documents, there is no knowledge to manage.
- **Phase 2 second:** Compilation must exist before search or PRD features can work. This is the dependency bottleneck.
- **Phase 3 third:** PRD generation is the primary user value and depends on compiled knowledge.
- **Phase 4 fourth:** Enhancement features add value but require working core.
- **Phase 5 last:** Polish comes after features are working.

### Research Flags

Phases likely needing deeper research during planning:
- **Phase 2:** Complex LLM integration for compilation; prompt engineering for entity/concept extraction needs iteration
- **Phase 3:** PRD template design varies by product type; need to validate multi-round collection UX
- **Phase 4:** Conflict detection logic is domain-specific; may need user feedback to refine

Phases with standard patterns (skip research-phase):
- **Phase 1:** Well-documented; markitdown API is straightforward, directory structure is standard
- **Phase 5:** Documentation and error handling are routine

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Verified with pip show, official docs, and existing skill analysis |
| Features | MEDIUM | Project requirements well-defined; ecosystem research limited by web access |
| Architecture | HIGH | Based on direct analysis of existing skills (mail-skill, echart-skill, follow-builders) |
| Pitfalls | MEDIUM | Based on LLM Wiki methodology and general domain knowledge; needs validation with actual documents |

**Overall confidence:** HIGH

### Gaps to Address

- **PRD template refinement:** Templates for ToC/ToB/Backend/Mini-program need validation with actual PM workflows. Handle by iterating during Phase 3 implementation.
- **Compilation prompt quality:** Entity extraction and cross-linking quality depends on prompt engineering. Handle by testing with sample documents and refining prompts iteratively.
- **Retrieval relevance:** Embedding-based vs keyword search trade-offs need real-world testing. Start with FTS5, add embeddings only if retrieval quality is insufficient.
- **Conversion edge cases:** Complex tables, diagrams, and multi-column layouts need testing with actual PM documents. Handle by building validation into Phase 1 and maintaining a test corpus.

## Sources

### Primary (HIGH confidence)
- markitdown — PyPI package inspection, Python help() output — document conversion capability verified
- Typer/Click — pip show output, pip index versions — CLI framework details
- Claude Code Skills — Examined existing skills (mail-skill, echart-skill, follow-builders) — architecture patterns
- Claude Code CLI — `claude --help` output — skill structure requirements
- Karpathy LLM Wiki methodology — Astro-Han/karpathy-llm-wiki — core knowledge compilation approach

### Secondary (MEDIUM confidence)
- LLM Wiki Skill Implementation — sdyckjq-lab/llm-wiki-skill — SKILL.md patterns and competitive analysis
- PRD Template Best Practices — MorganMarshall/PRD — template structure guidance
- Notion, Obsidian, Linear — feature comparison for differentiators

### Tertiary (LOW confidence)
- ChromaDB vs SQLite — pip show output, ecosystem knowledge — storage alternatives (WebSearch unavailable for deep comparison)
- Embedding quality trade-offs — general knowledge, needs validation with actual documents

---
*Research completed: 2026-04-27*
*Ready for roadmap: yes*