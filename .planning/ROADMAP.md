# Roadmap: PM Skill

## Overview

PM Skill transforms raw PM documents into structured wiki knowledge and leverages that knowledge to generate high-quality, industry-standard PRDs. The journey starts with document import infrastructure, builds the LLM Wiki compilation engine, enables PRD generation with multi-round requirement collection, and concludes with competitive analysis capabilities.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [ ] **Phase 1: Foundation & Document Pipeline** - Core Skill infrastructure and document-to-Markdown conversion
- [ ] **Phase 2: Knowledge Compilation & Retrieval** - LLM-powered wiki compilation and FTS5 search
- [ ] **Phase 3: PRD Generation** - Multi-round PRD writing with knowledge enhancement
- [ ] **Phase 4: Competitive Analysis** - Knowledge-based competitor analysis

## Phase Details

### Phase 1: Foundation & Document Pipeline
**Goal**: Users can import PM documents (PDF/DOC/HTML) and have them stored as Markdown in the raw/ directory, with a working CLI and proper directory structure.
**Depends on**: Nothing (first phase)
**Requirements**: FND-01, FND-02, FND-03, IMP-01, IMP-02, IMP-03, IMP-04, IMP-05, IMP-06
**Success Criteria** (what must be TRUE):
  1. User can run `pm-skill` CLI and see available commands
  2. User can configure document storage paths in a config file
  3. User can import a PDF file and find it converted to Markdown in raw/
  4. User can import a DOC/DOCX file and find it converted to Markdown in raw/
  5. User can import an HTML file and find it converted to Markdown in raw/
  6. Converted files pass basic validation (table syntax, image references, format integrity)
**Plans**: 3 plans in 3 waves

Plans:
- [x] 01-PLAN.md — Wave 0: Test infrastructure (pytest setup, fixtures, test scaffolds)
- [x] 02-PLAN.md — Wave 1: Skill foundation (SKILL.md, CLI, config, init command) [FND-01, FND-02, FND-03]
- [ ] 03-PLAN.md — Wave 2: Document import pipeline (markitdown integration, validation) [IMP-01-06]

### Phase 2: Knowledge Compilation & Retrieval
**Goal**: Raw documents are compiled into a structured wiki knowledge base with entities, concepts, and cross-links, searchable via CLI and FTS5.
**Depends on**: Phase 1
**Requirements**: CMP-01, CMP-02, CMP-03, CMP-04, CMP-05, CMP-06, CMP-07, CMP-08, RET-01, RET-02, RET-03, RET-04
**Success Criteria** (what must be TRUE):
  1. User can run a compile command and see raw/ files transformed into wiki/ structure
  2. Each raw document generates an entity page in wiki/entities/
  3. Concepts are auto-extracted and linked in wiki/concepts/
  4. wiki/index.md provides a browsable knowledge map
  5. User can search the wiki by keyword and see results with context
  6. Search results include confidence annotations (EXTRACTED/INFERRED/AMBIGUOUS/UNVERIFIED)
**Plans**: TBD

### Phase 3: PRD Generation
**Goal**: Users can generate industry-standard PRDs through multi-round requirement collection, enhanced by knowledge base retrieval.
**Depends on**: Phase 2
**Requirements**: PRD-01, PRD-02, PRD-03, PRD-04, PRD-05, PRD-06, PRD-07, PRD-08, PRD-09, PRD-10, PRD-11
**Success Criteria** (what must be TRUE):
  1. User can initiate PRD creation and be guided through multi-round requirement collection
  2. System automatically suggests relevant concepts/features from knowledge base during collection
  3. Generated PRD includes citations linking claims to source documents
  4. User can choose ToC template and get PRD focused on UX/flows/errors/analytics
  5. User can choose ToB template and get PRD focused on business logic/permissions/approvals
  6. User can choose backend template and get PRD focused on lists/permissions/audit logs
  7. User can choose mini-program template and get PRD focused on scenarios/platform rules/performance
**Plans**: TBD

### Phase 4: Competitive Analysis
**Goal**: Users can generate competitive analysis reports based on competitor documents in the knowledge base.
**Depends on**: Phase 3
**Requirements**: ANA-01
**Success Criteria** (what must be TRUE):
  1. User can run a competitive analysis command with competitor names
  2. System retrieves relevant competitor documents from wiki
  3. Analysis report includes feature comparisons, strengths/weaknesses, and differentiation opportunities
**Plans**: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Foundation & Document Pipeline | 2/3 | In progress | 01-PLAN, 02-PLAN |
| 2. Knowledge Compilation & Retrieval | 0/0 | Not started | - |
| 3. PRD Generation | 0/0 | Not started | - |
| 4. Competitive Analysis | 0/0 | Not started | - |

---
*Roadmap created: 2026-04-27*
*Based on research: .planning/research/SUMMARY.md*
*Last updated: 2026-04-27 - Plan 01-02 completed*