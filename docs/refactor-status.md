# Refactor Status

> Owned by Agent 0 (Coordinator). Tracks progress of all agents in Phase 1.

## Baseline (2026-06-01)

### Git
- Branch: `major-restructure` (pushed to origin)
- Working tree: clean (only MULTI_AGENT_REFACTOR_PLAN.md untracked)

### Test Suite
- **214 passed**, **3 failed**, 6 warnings
- Failures (all in `tests/test_classifier.py`):
  1. `test_classifier_matches_regex_scanner_contextual_pii` — "Sara Hoffmann" matched with employee ID suffix included
  2. `test_classifier_semantic_phone_still_detects_contextual_phone` — phone matched as Regex_Match, expected Semantic_Match
  3. `test_classifier_blank_templates_are_not_flagged_as_contextual_pii` — blank templates (`______`) incorrectly flagged as PII
- Root-level `test_script.py` has `exit()` on line 13, blocks pytest collection at root
- Python 3.9.6, key packages: fastapi 0.128.8, uvicorn 0.39.0, SQLAlchemy 2.0.50, pytest 8.4.2

### App Startup
- Not yet smoke-tested

### Root Directory Clutter (preliminary)
See Agent 7 for full classification. Notable:
- `fix_main.py`, `fix_quotes.py`, `fix_zombies.py`, `repair.py`, `replace_emojis.py`
- `clean_script.js`, `clean_script2.js`, `temp_script.js`, `test_script2.js`
- `gemini-code-1780144486142.py`, `gemini-code-1780145060717.py`
- `diff.txt`, `gdpr_loaders.html`, `gdpr_modal.html`, `html_guide.md`
- `classified_results.json`, `scan_results.json`
- `test_script.py` (has exit())
- `test_inject.py`, `test_audit_file.py`, `test_ai_gatekeeper.py`, `test_pdf_pipeline.py` (root-level tests)
- `generate_gdpr_pdf_test_set.py`, `seed_json_data.py`, `seed_test_expired.py`, `demo.py`, `demo_ingest.py`
- `uvicorn.log`

---

## Agent Status

| Agent | Status | Files Changed | Tests | Notes |
|-------|--------|---------------|-------|-------|
| 0 - Coordinator | in_progress | - | baseline recorded | - |
| 1 - Architecture Map | pending | - | - | - |
| 2 - Test Baseline | pending | - | - | - |
| 3 - API Boundary | pending | - | - | - |
| 4 - Scan Engine | pending | - | - | - |
| 5 - DB Hardening | pending | - | - | - |
| 6 - Production Readiness | pending | - | - | - |
| 7 - Repo Hygiene | pending | - | - | - |
| 8 - UI Route Stabilization | pending | - | - | - |

## Execution Order

1. ✅ Agent 0: baseline recorded
2. ⏳ Agent 1: architecture map
3. Agent 2: test baseline and safety net
4. Agent 6: production-readiness audit
5. Agent 7: repo hygiene proposal
6. Agent 4: scan engine consolidation
7. Agent 5: DB hardening
8. Agent 3: API boundary cleanup
9. Agent 8: UI smoke validation
10. Agent 0: final integration pass
