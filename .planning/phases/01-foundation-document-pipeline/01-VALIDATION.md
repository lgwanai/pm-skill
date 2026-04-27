---
phase: 01
slug: foundation-document-pipeline
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-27
---

# Phase 1 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.x |
| **Config file** | pyproject.toml (Wave 0 creates) |
| **Quick run command** | `pytest tests/ -q --tb=short` |
| **Full suite command** | `pytest tests/ -v --cov=scripts --cov-report=term-missing` |
| **Estimated runtime** | ~15 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/ -q --tb=short`
- **After every plan wave:** Run `pytest tests/ -v --cov=scripts --cov-report=term-missing`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 15 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 01-01-01 | 01 | 1 | FND-01 | unit | `pytest tests/test_skill.py -v` | ❌ W0 | ⬜ pending |
| 01-01-02 | 01 | 1 | FND-02 | unit | `pytest tests/test_config.py -v` | ❌ W0 | ⬜ pending |
| 01-02-01 | 02 | 1 | FND-03 | unit | `pytest tests/test_init.py -v` | ❌ W0 | ⬜ pending |
| 01-03-01 | 03 | 1 | IMP-01 | integration | `pytest tests/test_import_pdf.py -v` | ❌ W0 | ⬜ pending |
| 01-03-02 | 03 | 1 | IMP-02 | integration | `pytest tests/test_import_docx.py -v` | ❌ W0 | ⬜ pending |
| 01-03-03 | 03 | 1 | IMP-03 | integration | `pytest tests/test_import_html.py -v` | ❌ W0 | ⬜ pending |
| 01-03-04 | 03 | 1 | IMP-04 | unit | `pytest tests/test_markitdown.py -v` | ❌ W0 | ⬜ pending |
| 01-03-05 | 03 | 1 | IMP-05 | unit | `pytest tests/test_storage.py -v` | ❌ W0 | ⬜ pending |
| 01-03-06 | 03 | 1 | IMP-06 | unit | `pytest tests/test_validation.py -v` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/conftest.py` — shared fixtures (temp dirs, sample docs)
- [ ] `tests/test_skill.py` — SKILL.md validation tests
- [ ] `tests/test_config.py` — configuration loading tests
- [ ] `tests/test_init.py` — directory structure initialization tests
- [ ] `tests/test_import_pdf.py` — PDF import tests
- [ ] `tests/test_import_docx.py` — DOCX import tests
- [ ] `tests/test_import_html.py` — HTML import tests
- [ ] `tests/test_markitdown.py` — markitdown integration tests
- [ ] `tests/test_storage.py` — file storage tests
- [ ] `tests/test_validation.py` — document validation tests
- [ ] `tests/fixtures/` — sample documents for testing
- [ ] `pyproject.toml` — pytest configuration with coverage settings

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| CLI help output formatting | FND-01 | Visual output quality | Run `pm-skill --help` and verify formatting |
| Rich progress bar animation | IMP-01-06 | Animation requires visual inspection | Run `pm-skill import sample.pdf` and observe progress |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 15s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending