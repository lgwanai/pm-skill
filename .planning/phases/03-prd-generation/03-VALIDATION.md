---
phase: 3
slug: prd-generation
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-27
---

# Phase 3 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (already configured) |
| **Config file** | pyproject.toml |
| **Quick run command** | `pytest tests/test_prd.py -x -v` |
| **Full suite command** | `pytest --cov=scripts --cov-report=term-missing` |
| **Estimated runtime** | ~15 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/test_prd.py -x -v`
- **After every plan wave:** Run `pytest --cov=scripts --cov-report=term-missing`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 15 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 03-01-01 | 01 | 0 | PRD-all | scaffold | `pytest tests/test_prd.py -x` | ❌ W0 | ⬜ pending |
| 03-02-01 | 02 | 1 | PRD-01 | unit | `pytest tests/test_prd.py::TestConversation -x` | ❌ W0 | ⬜ pending |
| 03-02-02 | 02 | 1 | PRD-02 | unit | `pytest tests/test_prd.py::TestSuggestion -x` | ❌ W0 | ⬜ pending |
| 03-03-01 | 03 | 2 | PRD-03 | integration | `pytest tests/test_prd.py::TestRetrieval -x` | ❌ W0 | ⬜ pending |
| 03-03-02 | 03 | 2 | PRD-04 | unit | `pytest tests/test_prd.py::TestIterativeRetrieval -x` | ❌ W0 | ⬜ pending |
| 03-04-01 | 04 | 3 | PRD-05 | unit | `pytest tests/test_prd.py::TestConflictDetection -x` | ❌ W0 | ⬜ pending |
| 03-04-02 | 04 | 3 | PRD-06 | unit | `pytest tests/test_prd.py::TestRiskAssessment -x` | ❌ W0 | ⬜ pending |
| 03-05-01 | 05 | 4 | PRD-07 | integration | `pytest tests/test_prd.py::TestPRDStructure -x` | ❌ W0 | ⬜ pending |
| 03-05-02 | 05 | 4 | PRD-08-11 | integration | `pytest tests/test_prd.py::TestTemplates -x` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_prd.py` — covers all PRD requirements
- [ ] `tests/conftest.py` — add PRD-related fixtures (mock conversations, sample PRD content)
- [ ] `references/templates/*.jinja2` — template files needed for tests
- [ ] `references/prompts/collect.md` — collection prompt template
- [ ] `references/prompts/suggest.md` — suggestion prompt template
- [ ] `references/prompts/assess.md` — risk assessment prompt template

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Multi-round UX flow | PRD-01 | Requires interactive terminal session | Run `pm-skill prd new`, complete 3+ turns, verify suggestions appear |
| PRD output quality | PRD-07 | Subjective assessment of document quality | Generate PRD, review for completeness and readability |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 15s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
