# Multi-Agent Refactor Plan for TBH-BOSCH

## Goal

Turn the current hackathon/demo GDPR scanner into a cleaner, more maintainable engineering project without breaking the working demo.

The current project has useful production-style ideas, but the implementation is mixed across demo UI code, scan engine code, experimental modules, generated scripts, and legacy prototypes. The first priority is not to add features. The first priority is to separate responsibilities, remove naming confusion, protect working behavior with tests, and create a path toward an industrial-grade architecture.

## Current System Summary

This repository is a GDPR/PII document scanning demo for Bosch-style corporate data governance.

Main behavior:

1. Discover PDF/doc files from local/demo drives or connector abstractions.
2. Extract document text.
3. Classify document type.
4. Detect PII/GDPR findings with regex, semantic rules, optional AI.
5. Assign owners.
6. Persist files, findings, scan jobs, notifications to SQLite.
7. Show findings and workflows in admin/employee dashboards.

Main components:

- `main.py`: FastAPI web app with Jinja pages, login, dashboards, file actions, seed/startup logic.
- `api.py`: FastAPI scanning API with `/api/scan`, `/api/findings`, scan job status, review actions.
- `database.py`: SQLAlchemy models and SQLite setup.
- `src/`: main scan engine.
- `pii_filter/`: older/parallel fast filtering prototype.
- `templates/`, `static/`: UI.
- `demo_drive_rich/`, `data/`, `sample_docs/`: demo/test data.
- root-level `fix_*.py`, `clean_script*.js`, `gemini-code-*`, etc.: mostly temporary/generated/repair scripts.

## Non-Negotiable Constraints

- Do not rewrite the whole app at once.
- Do not delete working demo behavior until tests or manual checks prove it is unused.
- Do not change PII detection semantics casually. Changes here affect product behavior.
- Preserve current demo login/dashboard paths unless a migration note is written.
- Keep commits small and agent-owned.
- Every agent must run targeted tests for the files they touch.
- If an agent finds unexpected dirty files, do not revert them. Report and work around them.

## Desired End State

Target project shape:

```text
app/
  main.py                 # single FastAPI app factory / routing entry
  routes/
    pages.py
    scan.py
    findings.py
    admin.py
    employee.py
  templates/
  static/

scan_engine/
  connectors/
  parsers/
  classifiers/
  detectors/
  owners/
  pipeline.py
  models.py

data_access/
  database.py
  models.py
  repositories.py
  migrations/

scripts/
  dev/
  demo/
  maintenance/
  legacy/

tests/
docs/
```

This is a target direction, not a required one-shot move.

## Agent Assignments

### Agent 0: Coordinator / Integration Owner

Scope:

- Own the branch, sequencing, integration, and final verification.
- Do not make broad code changes except small coordination fixes.
- Keep a running checklist in `docs/refactor-status.md`.

Responsibilities:

1. Run baseline checks: `git status --short`, `python -m pytest`, smoke-test the app.
2. Record what currently passes/fails before refactoring.
3. Assign non-overlapping file ownership to each agent.
4. Review changes from other agents for cross-agent breakage.
5. After all agents finish, run the full test suite and manual smoke tests.

### Agent 1: Architecture Map and Naming Audit

Documentation only at first. Create `docs/architecture-map.md`. Mark components as active/legacy/experimental/duplicated.

### Agent 2: Test Baseline and Safety Net

Build confidence before refactor. Run tests, categorize failures, add core scan chain and API smoke tests.

### Agent 3: API Boundary Cleanup

Reduce confusion between `main.py` and `api.py`. Option A: single app imports scan routes. Option B: separate services.

### Agent 4: Scan Engine Consolidation

Clarify scan paths in `src/`. Document scan variants. Create `src/scan_service.py` wrapper.

### Agent 5: Database and Persistence Hardening

Split DB concerns, add tests for finding/file insert/update, document hardcoded defaults.

### Agent 6: Security and Compliance Reality Check

Create `docs/production-readiness.md`. Audit plaintext passwords, CORS, authz, audit trail, AI data risks.

### Agent 7: Repository Hygiene and Legacy Quarantine

Classify root files. Create move proposal for legacy/generated artifacts. Update `.gitignore`.

### Agent 8: Frontend/UI Route Stabilization

Map templates to routes. Identify JS API calls. Create smoke checklist. Fix broken references.

## Industrialization Backlog

High priority: real auth, PostgreSQL, Alembic migrations, job queue, structured config, audit logs, permission checks, retention policy.

Medium priority: normalize models, repository layer, OpenAPI docs, rate limiting, redaction, connector integration tests, observability.

Lower priority: frontend structure, package metadata, Dockerfile, CI, pre-commit hooks.

## Phase 2: Industrial Middleware

### Agent 9: PostgreSQL and Migration Layer
### Agent 10: Background Job Queue
### Agent 11: Configuration, Secrets, Environment Profiles
### Agent 12: Authentication, Authorization, Audit Trail
### Agent 13: Observability and Operations
### Agent 14: Containerization and Deployment

## Phase 3: Industrial Data Governance Enhancements

Real connector auth, delta tokens, retention policy engine, legal basis metadata, DPO escalation, immutable audit log, data minimization, human review SLAs, fine-grained permissions, AI governance.

## Suggested Execution Order

1. Agent 0 → 2. Agent 1 → 3. Agent 2 → 4. Agent 6 → 5. Agent 7 → 6. Agent 4 → 7. Agent 5 → 8. Agent 3 → 9. Agent 8 → 10. Agent 0 final pass

## Definition of Done

- Clear architecture map exists
- Reliable test baseline
- Active vs legacy documented
- Recommended app and scan entry points documented
- Production-readiness gaps documented
- Root clutter cleanup plan exists
- No working demo behavior broken
