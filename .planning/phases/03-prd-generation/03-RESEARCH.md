# Phase 3: PRD Generation - Research

**Researched:** 2026-04-27
**Domain:** Multi-round requirement collection, LLM-powered PRD generation with knowledge enhancement
**Confidence:** MEDIUM (templates based on industry patterns, retrieval pattern needs validation)

## Summary

Phase 3 implements PRD (Product Requirements Document) generation through multi-round conversation, enhanced by iterative knowledge base retrieval. The system collects requirements from users, automatically suggests relevant concepts/features from the knowledge base, and generates industry-standard PRDs with proper citations.

Key technical challenges include: (1) multi-turn conversation state management, (2) iterative retrieval with keyword extraction from search results, (3) template-based PRD generation with four distinct templates (ToC, ToB, Backend, Mini-program), and (4) citation linking between PRD claims and source documents.

**Primary recommendation:** Use Anthropic SDK with structured output (Pydantic models) for conversation state and PRD content. Implement iterative retrieval as a loop: extract keywords from current context → search → analyze results → extract new keywords → repeat until no new content. Store PRD templates as Jinja2 templates in `references/templates/`.

<phase_requirements>

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| PRD-01 | Multi-round requirement collection via conversation | Multi-turn conversation with state management (Anthropic SDK) |
| PRD-02 | Auto-suggest concepts/features/APIs/data fields from knowledge base | FTS5 search integration, concept extraction from results |
| PRD-03 | Use suggestions as keywords to search knowledge base | Existing FTS5 `search_wiki()` function, keyword extraction prompt |
| PRD-04 | Iterative retrieval: understand results → extract new keywords → search again | Loop pattern with convergence detection |
| PRD-05 | Compare user input vs knowledge base, detect conflicts, confirm | LLM-based comparison prompt, conflict detection logic |
| PRD-06 | Assess implementation cost and risks (tech/business/legal) | Risk assessment prompt template, structured output |
| PRD-07 | Generated PRD follows industry standard syntax | Standard PRD sections defined in templates |
| PRD-08 | ToC product PRD template (UX/flows/errors/analytics focus) | Template with UX-heavy sections |
| PRD-09 | ToB product PRD template (business logic/permissions/approvals focus) | Template with workflow-heavy sections |
| PRD-10 | Backend system PRD template (lists/permissions/audit logs focus) | Template with admin-heavy sections |
| PRD-11 | Mini-program PRD template (scenarios/platform rules/performance focus) | Template with platform-specific sections |

</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| anthropic | Already used | LLM API for conversation and generation | Already integrated in Phase 2 |
| pydantic | Already used | Structured output models for PRD content | Already used for config |
| jinja2 | 3.1.x | PRD template rendering | Industry standard for templating |
| sqlite3 | Built-in | FTS5 search (already implemented) | Existing infrastructure |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| typer | Already used | CLI for `prd` command | New `prd` subcommand |
| rich | Already used | Progress display, tables | User feedback during collection |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| jinja2 | string.Template | Jinja2 provides conditionals, loops, includes for templates |
| anthropic SDK | LangChain | Direct SDK gives more control, less abstraction overhead |
| FTS5 keyword extraction | separate NLP library | FTS5 stemmer + LLM extraction is simpler, leverages existing index |

**Installation:**
```bash
pip install jinja2  # Only new dependency
```

## Architecture Patterns

### Recommended Project Structure
```
scripts/
├── prd/                    # New PRD module
│   ├── __init__.py
│   ├── conversation.py     # Multi-turn conversation state
│   ├── retrieval.py        # Iterative retrieval logic
│   ├── templates.py        # Template loading and rendering
│   ├── generator.py        # PRD generation orchestration
│   └── models.py           # Pydantic models for PRD structure
references/
├── templates/              # New PRD templates
│   ├── toc-prd.md.jinja2
│   ├── tob-prd.md.jinja2
│   ├── backend-prd.md.jinja2
│   └── miniprogram-prd.md.jinja2
├── prompts/                # Existing + new prompts
│   ├── compile.md          # Existing
│   ├── collect.md          # New: requirement collection prompt
│   ├── suggest.md          # New: keyword suggestion prompt
│   ├── assess.md           # New: cost/risk assessment prompt
│   └── compare.md          # New: conflict detection prompt
```

### Pattern 1: Multi-Turn Conversation with State

**What:** Maintain conversation state across multiple turns, accumulating requirement information.

**When to use:** PRD-01 (multi-round requirement collection)

**Example:**
```python
from dataclasses import dataclass, field
from typing import Any
from datetime import datetime

@dataclass
class ConversationTurn:
    """Single turn in the requirement collection conversation."""
    role: str  # "user" or "assistant"
    content: str
    suggestions: list[str] = field(default_factory=list)
    keywords_extracted: list[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class RequirementCollection:
    """State for ongoing requirement collection."""
    turns: list[ConversationTurn] = field(default_factory=list)
    collected_requirements: dict[str, Any] = field(default_factory=dict)
    template_type: str = "toc"  # toc, tob, backend, miniprogram
    status: str = "collecting"  # collecting, validating, generating

    def add_turn(self, role: str, content: str) -> ConversationTurn:
        turn = ConversationTurn(role=role, content=content)
        self.turns.append(turn)
        return turn

    def get_context_for_llm(self) -> list[dict]:
        """Format turns for Anthropic API messages."""
        return [{"role": t.role, "content": t.content} for t in self.turns]
```

### Pattern 2: Iterative Retrieval Loop

**What:** Repeatedly search knowledge base, extract new keywords from results, until convergence.

**When to use:** PRD-03, PRD-04 (iterative retrieval)

**Example:**
```python
def iterative_retrieval(
    initial_keywords: list[str],
    search_func,  # search_wiki function
    extract_keywords_func,  # LLM-based keyword extraction
    max_iterations: int = 5,
    min_new_keywords: int = 2,
) -> tuple[list[dict], list[str]]:
    """Iteratively search and extract keywords until convergence.

    Returns:
        Tuple of (all_results, all_keywords)
    """
    all_results = []
    searched_keywords = set(initial_keywords)
    pending_keywords = list(initial_keywords)

    for iteration in range(max_iterations):
        if not pending_keywords:
            break

        # Search with current keywords
        query = " ".join(pending_keywords)
        results = search_func(query=query, limit=10)
        all_results.extend(results)

        # Extract new keywords from results
        result_text = "\n".join([r["snippet"] for r in results])
        new_keywords = extract_keywords_func(result_text, searched_keywords)

        # Filter out already-searched
        pending_keywords = [k for k in new_keywords if k not in searched_keywords]
        searched_keywords.update(new_keywords)

        # Check convergence
        if len(pending_keywords) < min_new_keywords:
            break

    return all_results, list(searched_keywords)
```

### Pattern 3: Template-Based PRD Generation

**What:** Use Jinja2 templates for different PRD types with consistent structure.

**When to use:** PRD-07 through PRD-11 (PRD templates)

**Example:**
```python
# references/templates/toc-prd.md.jinja2
"""
# {{ title }}

## Background and Objectives
{{ background }}

## User Stories
{% for story in user_stories %}
- **As a** {{ story.actor }}, **I want to** {{ story.action }}, **so that** {{ story.benefit }}
{% endfor %}

## User Flows
{% for flow in user_flows %}
### {{ flow.name }}
{{ flow.description }}

**Steps:**
{% for step in flow.steps %}
{{ loop.index }}. {{ step.description }}
{% endfor %}

**Error Handling:**
{% for error in flow.errors %}
- {{ error.condition }}: {{ error.recovery }}
{% endfor %}
{% endfor %}

## Analytics Events
{% for event in analytics %}
- **{{ event.name }}**: {{ event.description }} | Trigger: {{ event.trigger }}
{% endfor %}

## References
{% for ref in references %}
- [{{ ref.title }}]({{ ref.path }}) {{ ref.relevance }}
{% endfor %}
"""

def render_prd(template_type: str, context: dict) -> str:
    from jinja2 import Environment, FileSystemLoader

    env = Environment(loader=FileSystemLoader("references/templates/"))
    template = env.get_template(f"{template_type}-prd.md.jinja2")
    return template.render(**context)
```

### Anti-Patterns to Avoid
- **Storing conversation in global state:** Use dataclasses with explicit state, not globals
- **Unbounded retrieval loops:** Always set `max_iterations` to prevent infinite loops
- **Template in Python strings:** Use separate `.jinja2` files for maintainability
- **Ignoring citation traceability:** Every claim in PRD should link to source document

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|------|
| Template rendering | String formatting with f-strings | Jinja2 | Conditionals, loops, includes, inheritance |
| Conversation state | Dictionary with manual tracking | Pydantic dataclass | Type safety, serialization, validation |
| Keyword extraction | Custom NLP pipeline | LLM prompt + FTS5 stemmer | Leverages existing LLM and FTS5 infrastructure |
| Citation linking | Manual string matching | Store source IDs in PRD sections | Enables verification and traceability |

**Key insight:** PRD generation is primarily a prompt engineering and state management problem, not a novel algorithm problem. Leverage existing LLM and FTS5 infrastructure.

## Common Pitfalls

### Pitfall 1: Conversation Context Window Overflow
**What goes wrong:** Long conversations exceed LLM context limit, losing early requirement information.
**Why it happens:** Each turn adds to message history; no summarization or compression.
**How to avoid:** Implement context summarization after N turns; extract key requirements into structured state; only send relevant context.
**Warning signs:** LLM responses become generic; early requirements are forgotten; token usage warnings.

### Pitfall 2: Retrieval Quality Degradation
**What goes wrong:** Iterative retrieval returns irrelevant or duplicate results, polluting PRD content.
**Why it happens:** No deduplication; keywords become too generic; no relevance scoring.
**How to avoid:** Use BM25 ranking (already in FTS5); deduplicate by path; track relevance scores; set minimum relevance threshold.
**Warning signs:** PRD contains unrelated content; same source cited multiple times; poor relevance scores.

### Pitfall 3: Template Mismatch
**What goes wrong:** User selects ToC template but requirements are backend-focused, resulting in awkward PRD.
**Why it happens:** Template selection happens before understanding the domain.
**How to avoid:** Analyze requirements first; suggest appropriate template; allow template switching.
**Warning signs:** Many empty sections; forced content in irrelevant sections; user requests re-generation.

### Pitfall 4: Missing Citations
**What goes wrong:** PRD makes claims without linking to source documents.
**Why it happens:** LLM generates content without tracking sources; retrieval context is lost.
**How to avoid:** Store source metadata with each retrieved snippet; inject into PRD context; require References section in templates.
**Warning signs:** PRD contains "as mentioned in..." without actual links; claims cannot be verified.

## Code Examples

### Multi-Turn Conversation with LLM

```python
from anthropic import Anthropic
from .models import RequirementCollection, PRDContent

def collect_requirements(
    collection: RequirementCollection,
    client: Anthropic,
    model: str = "claude-sonnet-4-6-20250528",
) -> tuple[str, list[str]]:
    """Process one turn of requirement collection.

    Returns:
        Tuple of (assistant_response, suggested_keywords)
    """
    # Load collection prompt
    prompt = load_prompt("collect")

    messages = collection.get_context_for_llm()

    response = client.messages.create(
        model=model,
        max_tokens=2048,
        system=prompt,
        messages=messages,
    )

    assistant_text = response.content[0].text

    # Extract suggested keywords from response
    # (could be structured output or parsed from text)
    suggestions = extract_suggestions(assistant_text)

    return assistant_text, suggestions
```

### Conflict Detection (PRD-05)

```python
def detect_conflicts(
    user_input: str,
    knowledge_base_results: list[dict],
    client: Anthropic,
    model: str,
) -> list[dict]:
    """Compare user input against knowledge base to find conflicts.

    Returns:
        List of conflicts with source citations.
    """
    prompt = load_prompt("compare")

    kb_text = "\n".join([
        f"[{r['path']}] {r['snippet']}"
        for r in knowledge_base_results
    ])

    response = client.messages.create(
        model=model,
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": f"{prompt}\n\n## User Input:\n{user_input}\n\n## Knowledge Base:\n{kb_text}"
        }],
    )

    # Parse structured conflict output
    conflicts = parse_conflicts(response.content[0].text)
    return conflicts
```

### Cost and Risk Assessment (PRD-06)

```python
from pydantic import BaseModel
from typing import Literal

class RiskAssessment(BaseModel):
    """Structured risk assessment output."""
    category: Literal["technical", "business", "legal"]
    risk_level: Literal["low", "medium", "high"]
    description: str
    mitigation: str
    source_citations: list[str]

class CostEstimate(BaseModel):
    """Structured cost estimation."""
    component: str
    effort: str  # e.g., "2-3 weeks", "1 sprint"
    complexity: Literal["low", "medium", "high"]
    dependencies: list[str]

def assess_risks(
    requirements: dict,
    knowledge_base_results: list[dict],
    client: Anthropic,
    model: str,
) -> tuple[list[RiskAssessment], list[CostEstimate]]:
    """Assess implementation risks and estimate costs."""
    prompt = load_prompt("assess")

    # Use structured output with tool use
    response = client.messages.create(
        model=model,
        max_tokens=2048,
        tools=[{
            "name": "risk_assessment",
            "description": "Output risk and cost assessments",
            "input_schema": {
                "type": "object",
                "properties": {
                    "risks": {"type": "array"},
                    "costs": {"type": "array"}
                }
            }
        }],
        messages=[{
            "role": "user",
            "content": f"{prompt}\n\n## Requirements:\n{requirements}\n\n## Context:\n{format_results(knowledge_base_results)}"
        }],
    )

    # Extract tool use result
    for block in response.content:
        if block.type == "tool_use":
            return parse_assessment(block.input)

    return [], []
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Static PRD templates | Dynamic template with LLM | 2023+ | Personalized, context-aware PRDs |
| Manual keyword search | Iterative retrieval with LLM extraction | 2024+ | Better knowledge coverage |
| Single-turn generation | Multi-turn conversation | 2024+ | More complete requirements |

**Deprecated/outdated:**
- Hardcoded PRD sections: Use template-based generation with conditional sections
- Manual citation insertion: Automate with retrieval metadata

## Open Questions

1. **How to handle long conversations exceeding context limits?**
   - What we know: Anthropic has 200K token limit; conversation state grows linearly
   - What's unclear: Optimal summarization strategy; when to compress vs. drop context
   - Recommendation: Summarize after every 5-10 turns; keep structured state separate from conversation history

2. **How to measure retrieval convergence?**
   - What we know: Can track new keywords found per iteration
   - What's unclear: Optimal threshold; semantic vs. keyword-based convergence
   - Recommendation: Start with keyword-based (stop when <2 new keywords); consider adding semantic similarity check

3. **How to handle conflicting information in knowledge base?**
   - What we know: Knowledge base may have contradictory documents
   - What's unclear: How to present conflicts to user; automatic resolution
   - Recommendation: Detect conflicts and present to user for confirmation; flag in PRD with multiple sources

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest (already configured) |
| Config file | pyproject.toml |
| Quick run command | `pytest tests/test_prd.py -x -v` |
| Full suite command | `pytest --cov=scripts --cov-report=term-missing` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| PRD-01 | Multi-round requirement collection | unit | `pytest tests/test_prd.py::TestConversation -x` | Wave 0 |
| PRD-02 | Auto-suggest concepts from knowledge base | unit | `pytest tests/test_prd.py::TestSuggestion -x` | Wave 0 |
| PRD-03 | Use suggestions as search keywords | integration | `pytest tests/test_prd.py::TestRetrieval -x` | Wave 0 |
| PRD-04 | Iterative retrieval until convergence | unit | `pytest tests/test_prd.py::TestIterativeRetrieval -x` | Wave 0 |
| PRD-05 | Detect conflicts between input and KB | unit | `pytest tests/test_prd.py::TestConflictDetection -x` | Wave 0 |
| PRD-06 | Assess implementation costs and risks | unit | `pytest tests/test_prd.py::TestRiskAssessment -x` | Wave 0 |
| PRD-07 | PRD follows industry standard syntax | integration | `pytest tests/test_prd.py::TestPRDStructure -x` | Wave 0 |
| PRD-08 | ToC template with UX focus | integration | `pytest tests/test_prd.py::TestTemplates -x` | Wave 0 |
| PRD-09 | ToB template with business focus | integration | `pytest tests/test_prd.py::TestTemplates -x` | Wave 0 |
| PRD-10 | Backend template with admin focus | integration | `pytest tests/test_prd.py::TestTemplates -x` | Wave 0 |
| PRD-11 | Mini-program template with platform focus | integration | `pytest tests/test_prd.py::TestTemplates -x` | Wave 0 |

### Sampling Rate
- **Per task commit:** `pytest tests/test_prd.py -x -v`
- **Per wave merge:** `pytest --cov=scripts --cov-report=term-missing`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/test_prd.py` — covers all PRD requirements
- [ ] `tests/conftest.py` — add PRD-related fixtures (mock conversations, sample PRD content)
- [ ] `references/templates/*.jinja2` — template files needed for tests
- [ ] `references/prompts/collect.md` — collection prompt template
- [ ] `references/prompts/suggest.md` — suggestion prompt template
- [ ] `references/prompts/assess.md` — risk assessment prompt template

## Sources

### Primary (HIGH confidence)
- Existing codebase: scripts/compiler.py, scripts/search.py, scripts/cli.py — architecture patterns
- references/prompts/compile.md — prompt template pattern
- Anthropic SDK documentation (known patterns)

### Secondary (MEDIUM confidence)
- Industry PRD patterns (common sections: background, user stories, flows, acceptance criteria)
- RAG iterative retrieval patterns (query expansion, convergence detection)

### Tertiary (LOW confidence)
- Specific template section names for ToC/ToB/Backend/Mini-program — may need adjustment based on user feedback
- Convergence threshold (2 keywords) — may need tuning

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — leveraging existing infrastructure (Anthropic SDK, FTS5, Pydantic)
- Architecture: HIGH — patterns established in Phase 2; extending for PRD
- Templates: MEDIUM — section structure based on industry patterns but unvalidated for this use case
- Retrieval loop: MEDIUM — pattern is sound but convergence detection needs validation

**Research date:** 2026-04-27
**Valid until:** 30 days (stable LLM API patterns)
