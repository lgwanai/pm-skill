# Feature Research

**Domain:** PM Assistant / LLM Wiki Knowledge Management
**Researched:** 2026-04-27
**Confidence:** MEDIUM (Project requirements well-defined, ecosystem research limited by web access)

## Feature Landscape

### Table Stakes (Users Expect These)

Features users assume exist. Missing these = product feels incomplete.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Document import | Users expect to add PDF, DOC, HTML files without friction | LOW | Use markitdown for conversion |
| Document search | Basic keyword search across all documents | LOW | ripgrep for fast CLI search |
| Folder organization | Documents in logical structure (raw/wiki/log) | LOW | Standard directory layout |
| Markdown support | All documents as editable Markdown | LOW | markitdown handles conversion |
| CLI commands | Terminal-based management and querying | MEDIUM | Core interface for this skill |
| PRD templates | Standard PRD structures ready to use | LOW | Templates from industry standards |
| Basic metadata | File names, dates, tags | LOW | Filesystem-based metadata |

### Differentiators (Competitive Advantage)

Features that set the product apart. Not required, but valuable.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| LLM Wiki compilation | Raw docs auto-transformed into structured wiki with entities, concepts, glossary | HIGH | Core innovation from Karpathy methodology |
| Knowledge-enhanced PRD | PRD writing augmented by automatic knowledge retrieval | HIGH | Multi-step retrieval: keywords → concepts → terms → deep search |
| Iterative knowledge retrieval | Retrieve → understand → retrieve again until exhausted | HIGH | Critical for thorough knowledge gathering |
| Product-type-aware PRD | ToC/ToB/Backend/Mini-program specific templates | MEDIUM | Industry-specific structures |
| Conflict detection | Compare user input against knowledge base, flag conflicts | MEDIUM | Strategy/rule/process/data conflicts |
| Risk assessment | Auto-evaluate implementation cost and risks (tech/business/legal) | MEDIUM | Enhances PRD quality |
| Entity extraction | Auto-identify concepts, features, interfaces, data items | MEDIUM | Drives knowledge retrieval |
| Glossary generation | Auto-build terminology from documents | LOW | Part of wiki compilation |
| Cross-reference discovery | Find related documents automatically | MEDIUM | Entity and concept linking |

### Anti-Features (Commonly Requested, Often Problematic)

Features that seem good but create problems.

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| Real-time collaboration | Seems useful for teams | Significant complexity, out of scope for CLI skill | Single-user workflow, export to shared docs |
| Git integration for versioning | Version control seems natural | Adds dependency complexity, steep learning curve | Simple log files track changes, manual git if needed |
| Mobile app | Access anywhere | Massive scope expansion, different UX paradigm | Web/terminal access, future consideration |
| Complex permission system | Multi-team security | Over-engineering for single-user CLI tool | Filesystem permissions, trust the user |
| Real-time sync | Cloud convenience | Infrastructure complexity, offline-first is simpler | Local files, optional manual sync |
| Rich text editor | WYSIWYG editing | Markdown is the lingua franca, editors add complexity | Any Markdown editor works |
| AI chat interface | Conversational access | CLI skill already provides Claude access, redundant | Use skill directly in Claude |

## Feature Dependencies

```
PRD Writing with Knowledge Enhancement
    └──requires──> Knowledge Retrieval
                       └──requires──> LLM Wiki Compilation
                                          └──requires──> Document Import (markitdown)
                                                          └──requires──> Directory Structure (raw/wiki/log)

Competitive Analysis
    └──requires──> Knowledge Retrieval
    └──requires──> Document Import

Conflict Detection
    └──requires──> Knowledge Retrieval
    └──requires──> User Input Collection

Risk Assessment
    └──requires──> Knowledge Retrieval
    └──requires──> PRD Structure Knowledge

CLI Query Commands
    └──requires──> Wiki Directory Structure
    └──enhances──> All other features (primary interface)
```

### Dependency Notes

- **PRD Writing requires Knowledge Retrieval:** Cannot enhance PRD without knowledge base
- **Knowledge Retrieval requires Wiki Compilation:** Raw docs must be compiled to wiki first
- **Wiki Compilation requires Document Import:** Need documents in raw/ before compiling
- **CLI enhances all features:** Primary interface for user interaction
- **Conflict Detection requires User Input Collection:** Need user info to compare against knowledge

## MVP Definition

### Launch With (v1)

Minimum viable product - what's needed to validate the concept.

- [ ] Document import (PDF/DOC/HTML → Markdown) — Entry point, users need to add documents
- [ ] Directory structure (raw/wiki/log) — Foundation for LLM Wiki methodology
- [ ] LLM Wiki compilation — Core innovation, must validate this works
- [ ] CLI query commands (rg, find, grep) — Basic usability
- [ ] PRD templates (ToC/ToB/Backend/Mini-program) — Immediate value delivery
- [ ] Basic PRD writing with multi-turn input collection — Validate user workflow

### Add After Validation (v1.x)

Features to add once core is working.

- [ ] Knowledge-enhanced PRD — Requires working wiki, adds significant value
- [ ] Iterative retrieval loop — Enhances knowledge gathering depth
- [ ] Entity extraction for retrieval keywords — Automates keyword discovery
- [ ] Conflict detection — Improves PRD quality
- [ ] Risk assessment — Adds professional depth
- [ ] Glossary and index generation — Wiki polish

### Future Consideration (v2+)

Features to defer until product-market fit is established.

- [ ] Competitive analysis features — Requires more structured approach
- [ ] Custom compilation prompts — Advanced customization
- [ ] Multiple knowledge bases — Multi-project support
- [ ] Export formats (HTML, PDF) — Distribution beyond Markdown
- [ ] API for programmatic access — Integration potential

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| Document import | HIGH | LOW | P1 |
| Directory structure | HIGH | LOW | P1 |
| CLI query commands | HIGH | LOW | P1 |
| PRD templates | HIGH | LOW | P1 |
| LLM Wiki compilation | HIGH | HIGH | P1 |
| PRD writing (basic) | HIGH | MEDIUM | P1 |
| Knowledge-enhanced PRD | HIGH | HIGH | P2 |
| Iterative retrieval | MEDIUM | HIGH | P2 |
| Entity extraction | MEDIUM | MEDIUM | P2 |
| Conflict detection | MEDIUM | MEDIUM | P2 |
| Risk assessment | MEDIUM | MEDIUM | P2 |
| Product-type templates | MEDIUM | LOW | P2 |
| Glossary generation | LOW | LOW | P2 |
| Competitive analysis | MEDIUM | HIGH | P3 |
| Multiple knowledge bases | LOW | MEDIUM | P3 |

**Priority key:**
- P1: Must have for launch
- P2: Should have, add when possible
- P3: Nice to have, future consideration

## Competitor Feature Analysis

| Feature | Notion | Obsidian | Linear | Our Approach |
|---------|--------|----------|--------|--------------|
| Document storage | Database + files | Local Markdown | Database | Local files (raw/wiki/log) |
| Knowledge linking | Backlinks | Wiki links, graph | Cross-references | Entity/concept linking via LLM |
| AI assistance | AI writing help | Plugin ecosystem | Linear AI | Claude via skill interface |
| Search | Full-text | Full-text + graph | Search + filters | ripgrep CLI (fast, familiar) |
| Templates | Template gallery | Community templates | Issue templates | Industry PRD templates (ToC/ToB/Backend/Mini-program) |
| Collaboration | Real-time | Plugin-based | Real-time | Single-user (MVP) |
| Knowledge compilation | Manual organization | Manual organization | Manual | **Auto LLM compilation** (differentiator) |
| PRD support | Manual | Manual | Issue-based | **Enhanced PRD writing** (differentiator) |

## Sources

- Karpathy LLM Wiki methodology (https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) - Core inspiration for knowledge compilation approach
- Project requirements from idea.md - Detailed PRD structure and workflow requirements
- Notion, Obsidian, Linear feature analysis - Competitor comparison
- markitdown tool - Document conversion dependency
- create-skill framework - Skill development foundation

---
*Feature research for: PM Skill / LLM Wiki Knowledge Management*
*Researched: 2026-04-27*
