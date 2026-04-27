# Pitfalls Research

**Domain:** PM Skill - LLM-powered knowledge management and PRD generation
**Researched:** 2026-04-27
**Confidence:** MEDIUM

## Critical Pitfalls

### Pitfall 1: Knowledge Base Consistency After Updates/Deletions

**What goes wrong:**
When a source document is updated or deleted from `raw/`, the corresponding wiki pages in `wiki/` are not automatically updated or removed. This creates stale knowledge, broken links, and contradictions between the source and compiled knowledge.

**Why it happens:**
The LLM Wiki model treats `raw/` as immutable source material and `wiki/` as compiled knowledge. However, real-world document management requires updates and deletions. Without a cascade update mechanism, the wiki becomes inconsistent with its sources.

**How to avoid:**
1. Implement content hashing (SHA256) for all `raw/` files to detect changes
2. Maintain a cache mapping raw files to their derived wiki pages
3. On deletion/update, trace all affected wiki pages and either:
   - Remove orphaned content
   - Re-compile from updated source
   - Mark as stale with warning annotations
4. Add a `refresh` operation that detects changed sources and triggers re-ingest

**Warning signs:**
- Wiki pages reference deleted source files
- Content contradicts current raw/ sources
- Internal links point to non-existent files
- Index entries reference missing articles

**Phase to address:** Phase 2 (Knowledge Base Compilation) - build cascade update logic into the core ingestion workflow

---

### Pitfall 2: LLM Hallucination in PRD Generation

**What goes wrong:**
When generating PRDs from knowledge base content, the LLM may:
- Invent features not mentioned in any source
- Create fictional user personas or scenarios
- Fabricate competitive data or market statistics
- Generate plausible-sounding but incorrect technical specifications

**Why it happens:**
LLMs are trained to be helpful and complete patterns, not to strictly adhere to provided context. When asked to generate comprehensive PRDs, they may "fill in gaps" with fabricated content rather than admitting information gaps.

**How to avoid:**
1. Implement source attribution for every claim in generated PRDs
2. Use confidence annotations (EXTRACTED/INFERRED/AMBIGUOUS/UNVERIFIED) on all generated content
3. Require explicit source citation format: `[claim] (source: [[wiki/page]])`
4. Add validation step that cross-checks PRD content against wiki sources
5. Flag any content in PRD that lacks wiki backing as `<!-- needs verification -->`

**Warning signs:**
- PRD contains specific statistics without citations
- User personas are described in detail without source material
- Competitive analysis includes features not in the knowledge base
- Technical specs appear more precise than source documents allow

**Phase to address:** Phase 3 (PRD Generation) - build hallucination detection into the PRD generation workflow

---

### Pitfall 3: Context Window Overflow with Large Knowledge Bases

**What goes wrong:**
As the knowledge base grows, querying or generating PRDs requires reading more wiki pages than can fit in the LLM's context window. This leads to:
- Truncated context missing critical information
- Arbitrary selection of pages that may exclude relevant content
- Degraded output quality as the KB scales

**Why it happens:**
The naive approach loads all potentially relevant wiki pages into context. With hundreds of articles and thousands of entities, this quickly exceeds even large context windows (200K tokens).

**How to avoid:**
1. Implement hierarchical context loading:
   - First: Load `index.md` for high-level overview
   - Second: Load only most relevant topic/entity pages
   - Third: Load source pages only when specific claims are needed
2. Use embedding-based relevance scoring to prioritize pages
3. Implement progressive disclosure: start with summaries, expand on demand
4. Create "digest" pages that pre-summarize topics for common queries
5. Track token budgets explicitly and warn before truncation

**Warning signs:**
- Generated PRDs miss obvious information from the KB
- Queries return incomplete answers
- Context window warnings in logs
- Quality degradation as KB grows

**Phase to address:** Phase 2 (Knowledge Base Compilation) - design for scalability from the start

---

### Pitfall 4: Document Conversion Edge Cases

**What goes wrong:**
Converting PDFs, DOCX, and HTML to Markdown produces malformed output:
- Tables become unreadable or lose structure
- Images are referenced but not extracted
- Code blocks lose formatting or language hints
- Mathematical formulas become garbled
- Multi-column layouts create scrambled text
- Headers/footers interleave with content

**Why it happens:**
Markitdown and similar tools have limitations with complex document structures. They apply generic rules that fail on edge cases common in PM documents (tables, diagrams, specifications).

**How to avoid:**
1. Implement format-specific preprocessing:
   - PDFs: Detect tables, extract separately, reformat as Markdown tables
   - DOCX: Preserve heading hierarchy, handle embedded images
   - HTML: Clean navigation elements, extract main content only
2. Add post-conversion validation:
   - Check for broken table syntax
   - Verify image references have valid paths
   - Validate code block formatting
3. Implement fallback prompts: ask LLM to fix obvious conversion issues
4. Track conversion quality metrics and flag low-confidence conversions

**Warning signs:**
- Raw files contain `| | |` broken table syntax
- Image references with `![]()` missing URLs
- Code blocks without language specifiers
- Paragraphs that read like scrambled text
- Content appears in wrong order

**Phase to address:** Phase 1 (Document Conversion) - build robust conversion with validation

---

### Pitfall 5: Query Relevance and Ranking Failures

**What goes wrong:**
When querying the knowledge base:
- Irrelevant pages are retrieved while relevant ones are missed
- Ranking doesn't reflect actual relevance to the query
- Synonyms and related concepts aren't matched
- Query intent is misunderstood

**Why it happens:**
Without proper embedding-based retrieval and ranking, the system relies on simple text matching or LLM browsing, which fails at scale. PM queries often use domain-specific terminology that requires semantic understanding.

**How to avoid:**
1. Implement embedding-based similarity search for initial retrieval
2. Build a synonym/alias dictionary for PM-specific terms
3. Use two-stage retrieval: embedding similarity + LLM reranking
4. Track query success metrics and iterate on retrieval
5. Implement query expansion for ambiguous terms

**Warning signs:**
- Queries return "I couldn't find information about X" when X exists
- Retrieved pages are tangentially related at best
- Users reformulate queries multiple times
- Same query produces inconsistent results

**Phase to address:** Phase 2 (Knowledge Base Compilation) - implement robust retrieval early

---

### Pitfall 6: Orphaned and Isolated Knowledge

**What goes wrong:**
Wiki pages are created without proper linking to existing content:
- Entity pages have no inbound links from other wiki pages
- Topics exist in isolation without cross-references
- Knowledge becomes fragmented and hard to discover
- Graph visualization shows disconnected clusters

**Why it happens:**
During ingestion, the LLM focuses on processing the current source and may not fully integrate with existing wiki structure. Cross-linking requires awareness of all existing content, which is limited by context windows.

**How to avoid:**
1. During each ingest, explicitly scan for related existing pages:
   - Check entity pages for mentioned concepts
   - Check topic pages for overlapping themes
   - Suggest cross-references in generated pages
2. Implement periodic lint/healing:
   - Detect orphan pages (no inbound links)
   - Suggest relevant cross-references
   - Auto-link frequently co-mentioned concepts
3. Maintain a "concepts mentioned but not defined" list
4. Use graph analysis to identify isolated clusters

**Warning signs:**
- Pages exist but never appear in query results
- Knowledge graph shows disconnected components
- Users can't navigate between related topics
- Duplicate content appears across isolated pages

**Phase to address:** Phase 2 (Knowledge Base Compilation) - build cross-linking into ingestion

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Skip validation of converted documents | Faster ingestion | Corrupted knowledge base, missing tables/images | Never - validation is essential |
| Store raw content without hashing | Simpler implementation | Cannot detect updates, no change tracking | MVP only, add hashing before production |
| Generate PRDs without source citations | Faster generation | Hallucinated content, untrustworthy output | Never - citations are critical |
| Skip cross-linking during ingestion | Faster per-document processing | Fragmented knowledge, poor discoverability | MVP only, add in Phase 2 |
| Load all wiki pages for every query | Simpler retrieval logic | Context overflow, poor scalability | < 50 pages only |
| Ignore image extraction | Simpler conversion | Missing diagrams, broken visual references | Only for text-only documents |

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| Markitdown | Assume perfect conversion | Post-validate: check table syntax, image refs, code blocks |
| LLM API | Send full wiki for every query | Implement relevance-based page selection |
| File System | Case-sensitive path handling | Normalize all paths, validate existence before writing |
| Obsidian | Assume wikilinks work everywhere | Use `[[page]]` format, test link resolution |
| PDF sources | Extract text without structure | Preserve headings, detect tables, extract images separately |

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Linear page loading for queries | Slow queries, context waste | Hierarchical loading: index -> topics -> sources | > 50 wiki pages |
| Re-embedding all content on each update | Slow ingestion, wasted API calls | Incremental embedding, cache embeddings by content hash | > 100 sources |
| Full graph rebuild on each change | Slow graph generation | Incremental graph updates, cache edges | > 200 wiki pages |
| No caching for LLM calls | Repeated costs for same content | Cache by content hash, invalidate on change | Any scale |

## Security Mistakes

| Mistake | Risk | Prevention |
|---------|------|------------|
| Include API keys in raw sources | Keys leak into wiki, may be exposed | PII scan before ingestion, redact sensitive patterns |
| Store user PII in knowledge base | Privacy violation, GDPR issues | Privacy self-check prompt before processing |
| No access control on wiki files | Sensitive info accessible to all | Implement permission model, segregate sensitive topics |
| Trust all converted content blindly | Malicious content could execute | Sanitize markdown, validate links |

## UX Pitfalls

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| Silent conversion failures | Missing data, confused users | Report conversion quality, flag low-confidence sections |
| No progress feedback during ingestion | Users think system is hung | Show progress: "Analyzing...", "Creating pages...", "Updating index..." |
| Hallucinated PRD content accepted as fact | Wrong decisions based on fake data | Highlight unverified claims, require explicit approval |
| Orphan pages invisible | Knowledge exists but can't be found | Surface orphans in status, suggest linking |
| Query returns "nothing found" when content exists | Frustration, knowledge waste | Show "Did you mean..." suggestions, list related pages |

## "Looks Done But Isn't" Checklist

- [ ] **Document Conversion:** Often missing image extraction - verify `raw/assets/` has extracted images
- [ ] **Wiki Ingestion:** Often missing cross-links to existing pages - verify new pages link to relevant existing content
- [ ] **Index Update:** Often missing from ingest - verify `index.md` reflects new pages
- [ ] **Log Update:** Often skipped - verify `log.md` has operation record
- [ ] **PRD Generation:** Often missing source citations - verify every claim links to wiki source
- [ ] **Query Results:** Often missing relevant pages - verify multiple query formulations tested
- [ ] **Cache Update:** Often forgotten - verify cache reflects new raw->wiki mappings

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Stale wiki after source update | MEDIUM | 1. Detect changed files via hash, 2. Re-ingest changed sources, 3. Validate cross-references |
| Orphan pages | LOW | Run lint with auto-fix, manually review suggested links |
| Hallucinated PRD content | HIGH | 1. Strip all unverified content, 2. Re-generate with strict citation requirements, 3. Manual review |
| Context overflow | MEDIUM | 1. Implement hierarchical loading, 2. Add relevance scoring, 3. Test with full KB |
| Broken conversion | LOW | Re-convert with validation, manually fix edge cases |
| Missing cross-links | LOW | Run lint, accept suggested links, manual review |

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| Knowledge base consistency | Phase 2 (Knowledge Base Compilation) | Test: update raw file, verify wiki reflects changes |
| LLM hallucination in PRDs | Phase 3 (PRD Generation) | Test: generate PRD, verify all claims have sources |
| Context window overflow | Phase 2 (Knowledge Base Compilation) | Test: ingest 100+ pages, verify queries work |
| Document conversion edge cases | Phase 1 (Document Conversion) | Test: convert sample PDFs with tables/images |
| Query relevance failures | Phase 2 (Knowledge Base Compilation) | Test: query known content, verify retrieval |
| Orphaned knowledge | Phase 2 (Knowledge Base Compilation) | Test: lint on growing KB, verify cross-link suggestions |

## Sources

- **Karpathy LLM Wiki Methodology** - [Astro-Han/karpathy-llm-wiki](https://github.com/Astro-Han/karpathy-llm-wiki) (SKILL.md specification)
- **LLM Wiki Skill Implementation** - [sdyckjq-lab/llm-wiki-skill](https://github.com/sdyckjq-lab/llm-wiki-skill) (SKILL.md, competitive analysis)
- **PRD Template Best Practices** - [MorganMarshall/PRD](https://github.com/MorganMarshall/PRD)
- **Markitdown Documentation** - [microsoft/markitdown](https://github.com/microsoft/markitdown)

**Confidence Notes:**
- HIGH confidence on LLM Wiki methodology (direct source documentation)
- HIGH confidence on PRD structure (established templates)
- MEDIUM confidence on conversion edge cases (general knowledge, needs testing with actual documents)
- MEDIUM confidence on RAG/query relevance (well-known domain challenges, but implementation-specific)

---
*Pitfalls research for: PM Skill - LLM-powered knowledge management and PRD generation*
*Researched: 2026-04-27*
