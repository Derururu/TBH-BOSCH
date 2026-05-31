# Architecture Map and Naming Audit

**Date:** 2026-06-01
**Author:** Agent 1 (Architecture Map and Naming Audit)
**Status:** Living document — update as the refactor progresses.

---

## Table of Contents

1. [Quick Start for a New Developer](#1-quick-start-for-a-new-developer)
2. [Project Overview](#2-project-overview)
3. [Current Architecture](#3-current-architecture)
4. [Main Entry Points](#4-main-entry-points)
5. [Runtime Paths](#5-runtime-paths)
   - 5.1 main.py Web Dashboard Flow
   - 5.2 api.py Scan API Flow
   - 5.3 src/scanner.py Scan Engine Flow
   - 5.4 database.py Persistence Flow
6. [Component Status Catalogue](#6-component-status-catalogue)
7. [Naming Confusion Table](#7-naming-confusion-table)
8. [Duplicate / Overlapping Logic](#8-duplicate--overlapping-logic)
9. [Do Not Delete Yet](#9-do-not-delete-yet)
10. [Proposed Rename / Move Plan](#10-proposed-rename--move-plan)

---

## 1. Quick Start for a New Developer

This project is a **GDPR / PII document scanning demo** built for the TechON Hackathon 2026 (Bosch problem statement). It discovers PDFs and office documents, extracts text, detects personal data (PII/GDPR items), assigns data owners, and presents findings via two separate FastAPI applications.

**There are two servers you can run:**

```bash
# The web dashboard (login, admin, employee views, some API endpoints)
uvicorn main:app --reload --port 8000

# The dedicated scan API (trigger scans, query findings, review actions)
uvicorn api:app --reload --port 8000
```

The scan engine lives in `src/` and is shared between both apps.

**Supporting tools:**
```bash
# CLI scan pipeline (no web server needed)
python -m src.pipeline full-scan --repo ./data/sample_pdfs --output ./data/output
python -m src.pipeline ai-scan --repo ./data/sample_pdfs --output ./data/output
python -m src.pipeline delta-scan --repo ./data/sample_pdfs --previous-state ./data/state/latest.json
```

---

## 2. Project Overview

The system detects GDPR-relevant personal data in corporate documents using:
1. **File discovery** via connector abstractions (local filesystem, Google Drive, Microsoft Graph)
2. **PDF text extraction** via `pdfplumber`
3. **Regex-based PII detection** (emails, phone numbers, IBANs, passport numbers, tax IDs, etc.)
4. **Optional AI enrichment** via OpenRouter API (Claude-based document classification)
5. **Owner assignment** via hints, path analysis, or document fields
6. **Delta scanning** to skip unchanged files across runs
7. **Persistence** to SQLite via SQLAlchemy

The project grew from a hackathon prototype into a multi-component system, resulting in naming overlaps, duplicate logic, and mixed responsibilities.

---

## 3. Current Architecture

```
TBH-BOSCH/
  main.py               # FastAPI web app (dashboard + mixed API routes)
  api.py                # FastAPI scan API (dedicated, separate app)
  database.py           # SQLAlchemy ORM models + SQLite setup
  scanner.py            # [LEGACY] Root-level delta scan script

  src/                  # Main scan engine (active, shared)
    __init__.py
    ai_parser.py        # AI enrichment via OpenRouter
    ai_queue.py         # Async AI queue
    benchmark.py        # Scan benchmarking tool
    classifier.py       # Regex PII detection + document type classification
    connector.py        # Abstract connector + LocalSampleRepoConnector
    db_writer.py        # Bulk DB writer (batch flush)
    delta.py            # Delta state persistence & comparison
    delta_planner.py    # Delta planning
    discovery.py        # File discovery
    extractor.py        # Memory-safe file extraction pipeline (newer)
    fusion.py           # Result fusion layer (?)
    google_drive.py     # Google Drive connector
    microsoft_graph.py  # Microsoft Graph connector
    models.py           # Dataclass data contracts
    ocr_scanner.py      # OCR image scanning
    owner.py            # Owner assignment (3-tier resolution)
    pdf_parser.py       # PDF page extraction
    pipeline.py         # CLI entry point for scan commands
    review.py           # Human review queue
    scanner.py          # Core scan orchestration (run_full_scan, run_ai_scan)
    streaming_scanner.py # Streaming scan engine (ProcessPoolExecutor)

  pii_filter/           # Experimental fast-filtering prototype
    __init__.py
    file_ingestor.py    # File reader
    models.py           # Pydantic models (DocumentInput, PIIMatch, etc.)
    pii_scanner.py      # Regex PII detection engine
    pipeline.py         # FastFilterPipeline orchestrator
    state_manager.py    # SQLite-backed delta tracker

  backend/              # Alternative AI parser package (older?)
    ai_parser/
      __init__.py
      ai_parser.py
      openrouter_client.py
      run_ai_parse.py
      schemas.py

  templates/            # Jinja2 HTML templates (web dashboard)
    admin_dashboard.html
    admin_database_explorer.html
    data_points.html
    employee_dashboard.html
    employee_directory.html
    gdpr_modal_snippet.html
    login.html
    user_details.html

  static/               # Frontend assets
    css/dashboard.css
    css/login.css
    js/dashboard.js

  tests/                # Test suite
    test_ai_queue.py
    test_benchmark.py
    test_cases/workflow_input_test_cases.json
    test_classifier.py
    test_contracts.py
    test_db_writer.py
    test_discovery_delta.py
    test_flag_system.py
    test_google_drive.py
    test_microsoft_graph.py
    test_pii_filter.py
    test_streaming_scanner.py

  data/                 # Demo data & scan state
    owner_hints.json
    sample_pdfs/        # Sample PDFs for demo
    state/              # Delta state snapshots

  demo_drive_rich/      # Rich demo directory (hundreds of files)
    owner_hints.json    # Owner hints for demo files
    [PDFs and docs...]

  scripts/              # Utility scripts
    __init__.py
    benchmark.py

  docs/                 # Documentation
    adr-001-scan-architecture.md

  [root-level clutter — see Agent 7's scope]
```

---

## 4. Main Entry Points

| Entry Point | Command | Description | Status |
|-------------|---------|-------------|--------|
| `main.py` | `uvicorn main:app` | Web dashboard with Jinja pages, login, admin/employee dashboards, plus mixed-in API routes | **Active** |
| `api.py` | `uvicorn api:app` | Dedicated scan API: trigger scans, query findings, review actions, job tracking | **Active** |
| `src/pipeline.py` | `python -m src.pipeline` | CLI scan pipeline: full-scan, ai-scan, delta-scan, review management | **Active** |
| `src/scanner.py` | (imported, not standalone) | Core scan engine called by api.py, main.py, and src/pipeline.py | **Active** |
| `src/extractor.py` | (imported by main.py) | Memory-safe extraction pipeline, called via `main.py` POST `/api/admin/trigger-extraction` | **Active** |
| `pii_filter/pipeline.py` | (imported) | Experimental fast-filtering pipeline (not wired into main apps) | **Experimental** |
| Root `scanner.py` | `python scanner.py` (standalone) | Legacy delta scan script — walks filesystem, hashes, writes to DB directly | **Legacy** |

---

## 5. Runtime Paths

### 5.1 `main.py` — Web Dashboard Flow

**Title:** "Bosch GDPR Scan Engine API"

**Startup sequence** (`@app.on_event("startup")`):
1. Opens SQLite session via `SessionLocal()`
2. Loads `demo_drive_rich/owner_hints.json`
3. Creates admin Employee if not exists (`admin@bosch.com` / `password123`)
4. Creates Employee records for each hint entry
5. Uses `src.connector.LocalSampleRepoConnector` to list files in `./demo_drive_rich`
6. Inserts `FileMetadata` rows for each file (skipping existing by path)
7. Cleans up deleted files (rows with file_path not starting with `[DELETED]` but missing on disk)

**Web routes (Jinja2 templates):**
- `GET /` — Login page (`login.html`)
- `POST /login` — Authenticate, set `session_emp_id` cookie, redirect
- `GET /admin-dashboard` — Admin dashboard (`admin_dashboard.html`)
- `GET /admin-database-explorer` — DB explorer (`admin_database_explorer.html`)
- `GET /employee-dashboard` — Employee dashboard (`employee_dashboard.html`)
- `GET /employee-directory` — Employee directory (`employee_directory.html`)
- `GET /data-points` — Data points view (`data_points.html`)
- `GET /user-details/{employee_id}` — User details page (`user_details.html`)

**API routes mixed into main.py:**
- `GET /api/user-details/{employee_id}` — Employee file/finding data (JSON)
- `GET /api/admin/kpis` — Admin KPIs
- `GET /api/admin/employees/search` — Employee search
- `POST /api/admin/extend-retention/{file_id}` — Extend retention (mock)
- `POST /api/admin/retain-document/{file_id}` — Retain document (logging only)
- `GET /api/employee/files/{employee_id}` — Employee's files with findings
- `POST /api/employee/action` — Process employee action (delete, keep, etc.)
- `POST /api/employee/files/{file_id}/delete-expired` — Delete expired file
- `POST /api/employee/files/{file_id}/extend-retention` — Extend retention
- `POST /api/admin/trigger-scan` — Trigger delta-aware scan (uses `src.scanner.run_ai_scan`, `src.delta`)
- `POST /api/admin/trigger-extraction` — Memory-safe extraction (uses `src.extractor.scan_directory`)
- `GET /api/admin/extraction-results` — Cached extraction results
- `POST /api/admin/seed-dummy-data` — Seed test data
- `GET /api/search` — Search findings
- `POST /api/admin/deletion-request` — Send deletion request notification
- `GET /api/employee/notifications/{employee_id}` — Get notifications
- `POST /api/employee/notifications/{notification_id}/read` — Mark notification read
- `GET /api/compliance-score/{employee_id}` — Compliance score
- `POST /api/scan/image` — OCR image upload scan
- `GET /api/scan/image/cache-stats` — OCR cache stats
- `POST /api/scan/image/clear-cache` — Clear OCR cache
- `GET /api/files/{file_id}/view` — View file content (owner-only)

**Key observation:** `main.py` contains *both* page-rendering routes and a large number of API routes. This is the primary source of confusion between `main.py` and `api.py` — they overlap in functionality.

### 5.2 `api.py` — Scan API Flow

**Title:** "GDPR Data Discovery API"
**Version:** 2.0.0

**Endpoints:**
- `POST /api/scan` — Trigger a scan on a folder (non-blocking, returns scan_id immediately)
- `GET /api/scan/{scan_id}` — Get scan job status
- `GET /api/scan/{scan_id}/stats` — Get detailed timing metrics
- `GET /api/scan/{scan_id}/errors` — Get file-level errors
- `GET /api/scans` — List recent scan jobs
- `POST /api/upload` — Upload files to scan
- `GET /api/findings` — Search/filter/paginate findings
- `POST /api/findings/{finding_id}/review` — Submit a human review action
- `GET /api/health` — Health check

**Background scan flow:**
1. Validates folder path, creates `ScanJob` record (status: "pending")
2. Launches background thread `_run_background_scan()`
3. Thread sets status to "running"
4. Uses `LocalSampleRepoConnector` to discover files
5. Persists `FileMetadata` via `BulkWriter`
6. Calls `run_ai_scan(connector, ai_parser, db_session)`
7. Persists findings via `BulkWriter`
8. Updates job status to "completed" with metrics

**Upload scan flow:**
1. Saves uploaded files to a temp directory
2. Runs same scan pipeline as `/api/scan`
3. Cleans up temp directory

**Key observation:** `api.py` has its *own* FastAPI app instance, separate from `main.py`. They share `database.py` and `src/` but run on their own port. This means they cannot be combined without an app factory refactor.

### 5.3 `src/scanner.py` — Scan Engine Flow

**Core functions:**
- `run_full_scan(connector, db_session)` — Batch scan:
  1. `connector.list_files()` → `list[FileMetadata]`
  2. For each file: `connector.download_file()` → `bytes`
  3. `parse_pdf(raw_bytes)` → `(pages, needs_ocr)`
  4. `_extract_fields(full_text)` → field dict
  5. `classify_context(full_text, fields)` → document type
  6. `extract_entities(full_text, pages)` → `list[Finding]`
  7. `assign_owners(findings, hints, ...)` — mutates findings in place
  8. Accumulates `ScanResult.parsed_documents` + `ScanResult.findings`

- `run_ai_scan(connector, ai_parser, db_session)` — Full scan + AI enrichment:
  1. Calls `run_full_scan()` first
  2. For each document, if AI parser available and document qualifies:
     - Calls `ai_parser.parse(text, fields, ...)`
     - Overrides document_type if AI confident (>0.6)
     - Merges AI findings into result
  3. Re-assigns owners (AI may have added findings)

- `run_layered_scan(...)` — Streaming + async AI:
  1. Runs `run_streaming_scan()` (regex only) via callbacks
  2. For each result, checks `AIGate.should_enrich()`
  3. If yes, enqueues in `AIQueue` for background processing
  4. Returns metrics immediately; AI results accessible later

**Call chain:** `api.py` → `run_ai_scan()` → `run_full_scan()` → `extract_entities()` / `classify_context()` / `assign_owners()`

### 5.4 `database.py` — Persistence Flow

**Engine:** SQLite (`sqlite:///./bosch_gdpr.db`)

**ORM Models:**
- `Employee` — `employees` table: employee_id, email, name, password (plaintext!), department, location
- `FileMetadata` — `files` table: file_path, owner_employee_id, size_bytes, last_modified, file_hash, retention_deadline
- `Finding` — `findings` table: 30+ columns covering both "legacy" fields (category, confidence_score, flagged_snippet, reasoning) and "extended" fields (type, value, context, risk_level, confidence, etc.) plus review state fields
- `ScanJob` — `scan_jobs` table: scan_id, status, options/metrics JSON, timing, counts
- `ScanError` — `scan_errors` table: per-file errors during scanning
- `Notification` — `notifications` table: admin-to-employee messages with file_ids JSON

**Session management:**
- `get_db()` — FastAPI dependency that yields a session, auto-closes on request end
- `Base.metadata.create_all(bind=engine)` — Auto-creates tables at import time

**Key observations:**
- The `Finding` model has **both** legacy columns (`category`, `confidence_score`, `flagged_snippet`, `reasoning`) and extended pipeline columns (`type`, `value`, `context`, `confidence`, `risk_level`, etc.). These overlap in purpose — the code mirrors data into both sets during persistence.
- Passwords are stored in plaintext (documented as "fine for a hackathon").
- The `FileMetadata` ORM class has the same name as the `src.models.FileMetadata` dataclass — see naming confusion table below.

---

## 6. Component Status Catalogue

### `ACTIVE` — Currently wired into the running application

| Component | Path | Notes |
|-----------|------|-------|
| Web dashboard | `main.py` | Primary user-facing app |
| Scan API | `api.py` | Secondary app sharing the same DB |
| Core scan engine | `src/scanner.py` | `run_full_scan`, `run_ai_scan`, `run_layered_scan` |
| Pipeline CLI | `src/pipeline.py` | CLI tool for ad-hoc scans |
| Entity extraction | `src/classifier.py` | Regex PII detection |
| PDF parsing | `src/pdf_parser.py` | pdfplumber-based |
| Owner assignment | `src/owner.py` | 3-tier resolution |
| Connector abstraction | `src/connector.py` | ABC + local filesystem implementation |
| Data contracts | `src/models.py` | Dataclasses used by all src/ modules |
| Delta scanning | `src/delta.py` | State comparison |
| AI parser | `src/ai_parser.py` | OpenRouter API integration |
| AI queue | `src/ai_queue.py` | Async enrichment queue |
| Streaming scanner | `src/streaming_scanner.py` | High-throughput parallel scanner |
| Bulk DB writer | `src/db_writer.py` | Batch SQLite writes |
| Memory-safe extractor | `src/extractor.py` | Generator-based file scanning |
| OCR scanner | `src/ocr_scanner.py` | Tesseract OCR for images |
| Review queue | `src/review.py` | Review item lifecycle |
| DB models & setup | `database.py` | SQLAlchemy ORM |
| Templates | `templates/` | Jinja2 HTML |
| Static assets | `static/` | CSS and JS |
| Google Drive connector | `src/google_drive.py` | Cloud connector |
| Microsoft Graph connector | `src/microsoft_graph.py` | Cloud connector |
| Discovery | `src/discovery.py` | File discovery |
| Delta planner | `src/delta_planner.py` | Delta planning |
| Fusion | `src/fusion.py` | Result fusion |

### `ACTIVE BUT SHOULD MOVE` — Works but is in the wrong place

| Component | Path | Target |
|-----------|------|--------|
| Benchmark | `src/benchmark.py` | Should move to `scripts/` |
| Benchmark CLI | `scripts/benchmark.py` | Already in scripts/ — duplicate? |
| Seed script | `seed_json_data.py` | Should move to `scripts/` or `scripts/demo/` |

### `LEGACY CANDIDATE` — Superseded, not wired into current flow

| Component | Path | Superseded By |
|-----------|------|---------------|
| Root `scanner.py` | `scanner.py` | `src/scanner.py` and `src/delta.py` |
| Old demo | `demo.py` | `main.py` startup seeding |
| Demo ingest | `demo_ingest.py` | `main.py` startup seeding |
| Old test | `test_pdf_pipeline.py` | Tests in `tests/` |

### `EXPERIMENTAL / PROTOTYPE` — Not wired into main apps

| Component | Path | Notes |
|-----------|------|-------|
| `pii_filter/` | `pii_filter/` | Standalone fast-filtering prototype with its own models, pipeline, and state manager. Not imported by `main.py` or `api.py`. Has its own test. |
| `backend/ai_parser/` | `backend/ai_parser/` | Alternative AI parser package (appears older than `src/ai_parser.py`). Not imported by any active route. |

### `GENERATED / TEMP CANDIDATE` — Created by tools, AI, or one-off runs

| Component | Path | Likely Origin |
|-----------|------|---------------|
| `clean_script.js` | root | AI-generated or manual fix script |
| `clean_script2.js` | root | AI-generated or manual fix script |
| `temp_script.js` | root | Temporary JS |
| `test_script2.js` | root | Temporary JS |
| `gemini-code-*.py` (2 files) | root | Gemini AI-generated code |
| `fix_main.py` | root | Repair/fix script |
| `fix_quotes.py` | root | Repair/fix script |
| `fix_zombies.py` | root | Repair/fix script |
| `repair.py` | root | Repair script |
| `replace_emojis.py` | root | Cleanup script |
| `generate_gdpr_pdf_test_set.py` | root | Test data generation |
| `seed_test_expired.py` | root | Seed script |
| `check_db.py` | root | Diagnostic |
| `test_script.py` | root | Test/diagnostic |
| `test_inject.py` | root | Test injection |
| `test_ai_gatekeeper.py` | root | Test/experiment |
| `test_audit_file.py` | root | Test/experiment |
| `classified_results.json` | root | Output data |
| `scan_results.json` | root | Output data |
| `diff.txt` | root | Diff output |
| `uvicorn.log` | root | Log file |
| `gdpr_loaders.html` | root | Standalone HTML |
| `gdpr_modal.html` | root | Standalone HTML |
| `html_guide.md` | root | Documentation fragment |
| `mock_drive/` | root | Temporary test data |

### `UNKNOWN`

| Component | Path | Reason |
|-----------|------|--------|
| `src/fusion.py` | not read | Purpose unclear from filename |
| `src/discovery.py` | not read in detail | Likely active but not verified |

---

## 7. Naming Confusion Table

### 7.1 Root `scanner.py` vs `src/scanner.py`

| Aspect | Root `scanner.py` | `src/scanner.py` |
|--------|-------------------|-------------------|
| Path | `./scanner.py` | `./src/scanner.py` |
| Purpose | Legacy delta scan: walks files, computes MD5, writes FileMetadata to DB directly | Orchestrates full scan pipeline: parse, classify, assign owners, AI enrichment |
| Used by | Standalone execution only | Imported by `api.py`, `main.py`, `src/pipeline.py` |
| Risk | `import scanner` would import the wrong one depending on `sys.path` | Imported via `from src.scanner import ...` — unambiguous |
| Status | **Legacy candidate** | **Active** |

### 7.2 `FileMetadata` Dataclass (src/models.py) vs `FileMetadata` ORM (database.py)

| Aspect | `src.models.FileMetadata` | `database.FileMetadata` |
|--------|---------------------------|-------------------------|
| Type | `@dataclass` | SQLAlchemy `Base` subclass |
| Table/Usage | Returned by `Connector.list_files()` | `files` table in SQLite |
| Fields | `file_id`, `file_name`, `path`, `size_bytes`, `last_modified`, `content_hash`, `mime_type` | `id`, `file_path`, `owner_employee_id`, `size_bytes`, `last_modified`, `file_hash`, `retention_deadline` |
| Import confusion | Both named `FileMetadata` — must be aliased on import | e.g. `from database import FileMetadata as FileMetadataORM` |
| Risk | Easy to mix up; api.py already aliases them (`FileMetadataORM`) | Aliasing is manual and inconsistent across files |
| Recommendation | Rename dataclass to `FileInfo` or `FileDocument` in a future refactor | Keep ORM name or rename to `FileRecord` |

### 7.3 `pipeline.py` CLI (src/pipeline.py) vs `pipeline.py` Orchestrator (pii_filter/pipeline.py)

| Aspect | `src/pipeline.py` | `pii_filter/pipeline.py` |
|--------|--------------------|--------------------------|
| Full path | `./src/pipeline.py` | `./pii_filter/pipeline.py` |
| Purpose | CLI entry point for scan commands (`full-scan`, `ai-scan`, `delta-scan`, etc.) | `FastFilterPipeline` orchestrator: delta-aware batch PII scanning |
| Entry | `python -m src.pipeline <subcommand>` | Imported by other `pii_filter` modules |
| Status | **Active** | **Experimental** |
| Risk | Module name collision if both packages are on `sys.path` | Low — namespaced under respective packages |

### 7.4 `api.py` vs `main.py`

| Aspect | `api.py` | `main.py` |
|--------|----------|-----------|
| App type | FastAPI app (title "GDPR Data Discovery API") | FastAPI app (title "Bosch GDPR Scan Engine API") |
| Primary function | Scan API — trigger scans, query findings, review | Web dashboard — login, dashboards, plus APIs |
| API routes | `/api/scan`, `/api/findings`, `/api/findings/{id}/review`, `/api/scans`, `/api/upload`, `/api/health` | `/api/admin/*`, `/api/employee/*`, `/api/search`, `/api/compliance-score/*`, `/api/files/*`, `/api/scan/image`, `/api/user-details/*` |
| Page routes | None | `/`, `/login`, `/admin-dashboard`, `/employee-dashboard`, etc. |
| DB writes via | `BulkWriter` + `_persist_finding()` | Direct session add/commit |
| Running mode | `uvicorn api:app` | `uvicorn main:app` |
| Risk | Routes are **split across two apps**. An operator must choose which port each runs on. They share the same SQLite DB. | API routes in `main.py` overlap with `api.py`'s purpose (e.g., both have scan-triggering endpoints). |
| Recommendation | Merge into a single application with route modules, or clearly separate responsibilities. See Agent 3. |

### 7.5 `pii_filter/` vs `src/classifier.py`

| Aspect | `pii_filter/` | `src/classifier.py` |
|--------|---------------|---------------------|
| Package | Full package (`models.py`, `pii_scanner.py`, `pipeline.py`, `file_ingestor.py`, `state_manager.py`) | Single module within `src/` package |
| Purpose | Standalone fast filtering layer with its own pipeline, state management, and I/O models | Entity extraction and context classification within the main scan engine |
| Models | Pydantic: `DocumentInput`, `PIIMatch`, `FlaggedDocument`, `PIIType` (enum) | Dataclasses: `Finding`, `PageContent` |
| Patterns | Similar regex categories (email, phone, name, etc.) in `pii_scanner.py` | Same regex categories in `classifier.py` (duplicated!) |
| Status | **Experimental** — not imported by `main.py` or `api.py` | **Active** |
| Risk | Regex patterns are duplicated across `pii_filter/pii_scanner.py` and `src/classifier.py` (and also `src/extractor.py`). Changes to detection logic must be made in three places. | Triple-maintenance problem. |

---

## 8. Duplicate / Overlapping Logic

### 8.1 Regex PII Patterns (Triple Maintenance)

The same (or very similar) PII detection regexes appear in three places:
1. `src/classifier.py` — `_PATTERNS` list (~16 patterns)
2. `src/extractor.py` — `_COMPILED_PATTERNS` list (~16 patterns, independently defined)
3. `pii_filter/pii_scanner.py` — `_EMAIL_RE`, `_PHONE_RE`, etc. (~8 patterns)

**Impact:** Any PII detection improvement (new pattern, false-positive fix, risk level change) must be applied in all three locations.

### 8.2 Scan-Triggering Endpoints

Two API endpoints trigger scans:
1. `main.py` `POST /api/admin/trigger-scan` — uses `src.scanner.run_ai_scan` + `src.delta`
2. `api.py` `POST /api/scan` — uses `src.scanner.run_ai_scan` + `BulkWriter` + ScanJob tracking

**Impact:** Inconsistent behavior — `api.py`'s version tracks scan jobs in the DB; `main.py`'s version does not.

### 8.3 Finding Persistence

Two mechanisms persist findings to the DB:
1. `main.py` — Direct `db.add(row)` + `db.commit()` (in `trigger_manual_scan` and `trigger_extraction`)
2. `api.py` — `BulkWriter` batch flushing (in `_run_background_scan`) + `_persist_finding()` standalone function (in upload flow)

### 8.4 Owner Hints / Employee Seeding

Employee seeding from `owner_hints.json` happens in:
1. `main.py` startup event (comprehensive — creates employees from hints)
2. `api.py` does not seed employees (relies on main.py having done so)

---

## 9. Do Not Delete Yet

The following files appear active but are candidates for refactoring. Do not delete them until the replacement is verified:

| File | Why Keep | Deletion Condition |
|------|----------|-------------------|
| `main.py` | Primary web app — must keep until routes are extracted | Routes migrated to `app/routes/` |
| `api.py` | Secondary scan API — must keep until merged with main.py or verified redundant | Integration verified |
| `database.py` | All ORM models — central to both apps | Models split into `data_access/` |
| `src/scanner.py` | Core scan engine — imported by all three entry points | Scan logic moved to `scan_engine/` |
| `src/classifier.py` | PII detection and document classification | Patterns unified, tests pass |
| `src/models.py` | Data contracts — imported by every src/ module | Models migrated, all imports updated |
| `src/connector.py` | Connector abstraction | Replaced with new connector interface |
| `src/owner.py` | Owner assignment | Replaced or confirmed working |
| `src/pdf_parser.py` | PDF text extraction | Confirmed superseded |
| `src/delta.py` | Delta state management | Confirmed superseded |
| `src/ai_parser.py` | AI enrichment | Confirmed superseded |
| `src/extractor.py` | Memory-safe extraction (used by main.py `/api/admin/trigger-extraction`) | Confirmed superseded |
| `src/ocr_scanner.py` | OCR image scanning (used by main.py `/api/scan/image`) | Confirmed superseded |
| `src/pipeline.py` | CLI entry point | Confirmed superseded |
| `templates/` (all) | Web UI — no alternative exists | UI migrated |
| `static/` (all) | CSS/JS for web UI | UI migrated |
| `demo_drive_rich/` | Demo data with owner_hints.json | Demo data migrated |
| `data/` | Demo data + delta state files | State management moved |

---

## 10. Proposed Rename / Move Plan

### High Priority (Naming Confusion Resolution)

| Current Name | Proposed Name | Reason |
|-------------|---------------|--------|
| `scanner.py` (root) | `legacy/root_scanner.py` | Eliminates ambiguity with `src/scanner.py` |
| `src/models.FileMetadata` (dataclass) | `src.models.FileInfo` or `src.models.FileDocument` | Distinguishes from `database.FileMetadata` ORM |
| `database.FileMetadata` (ORM) | `database.FileRecord` (if renamed) | Distinguishes from dataclass |

### Medium Priority (Structural)

| Component | Proposal | Notes |
|-----------|----------|-------|
| `main.py` API routes | Extract to `app/routes/admin.py`, `app/routes/employee.py` | Separate pages from APIs |
| `main.py` page routes | Extract to `app/routes/pages.py` | Keep `main.py` as app factory only |
| `api.py` routes | Extract to `app/routes/scan.py`, `app/routes/findings.py` | Merge into unified app |
| `src/` | Rename to `scan_engine/` | Clarifies purpose |
| `src/benchmark.py` | Move to `scripts/benchmark.py` | Aligns with existing `scripts/` dir |
| `seed_json_data.py` | Move to `scripts/seed_json_data.py` | Utility script |
| `demo.py`, `demo_ingest.py` | Move to `scripts/legacy/` | Not active, keep for reference |

### Low Priority (Cleanup)

| Component | Proposal |
|-----------|----------|
| `pii_filter/` | Keep in place; label as experimental. Can be resurrected or removed in Phase 2. |
| `backend/ai_parser/` | Investigate relationship to `src/ai_parser.py`; consolidate or remove. |
| `mock_drive/` | Move to `data/mock_drive/` or remove after demo data migration. |
| Root `*.js`, `*.json`, `*.html`, `*.md`, `*.txt` files | Move to `scripts/legacy/`, `data/`, or archive. See Agent 7. |

### Cross-Cutting Recommendations

1. **Create a shared pattern registry** — Extract the regex patterns from `src/classifier.py`, `src/extractor.py`, and `pii_filter/pii_scanner.py` into a single source of truth (`src/patterns.py` or `scan_engine/patterns.py`).
2. **Unify finding persistence** — Consolidate into a single `FindingRepository` class that both `main.py` and `api.py` use.
3. **Unify scan triggering** — Consolidate `main.py`'s `/api/admin/trigger-scan` and `api.py`'s `/api/scan` into a single scan service.
4. **App factory** — Create a single `app` factory in a new `app/__init__.py` that registers all routes, rather than two standalone FastAPI apps.
