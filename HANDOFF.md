# HANDOFF.md — Session Memory

> Updated by the agent at the end of each session.
> This file is the context bridge between different sessions.

## Last update

- **Date:** 2026-05-28
- **Session:** harness CLI loop hardening
- **Branch / HEAD:** main

## Goals completed this session

### Harness CLI loop hardening

**Agent loop** (`harness/prompts/scripts/agent-loop.py`):
- Reads prompt templates directly from `harness/prompts/{builder,qa,security}.md` instead of a missing `templates/` directory.
- Falls back to an internal safe config if no config file exists.
- Supports `--diff-path` to scope the diff sent to QA/Security and avoid unrelated dirty worktree changes.
- Supports command placeholders `{root}`, `{prompt_file}`, and `{prompt}` for CLIs like `opencode` and `copilot`.
- Stops the loop when Builder, QA, or Security commands exit nonzero instead of continuing with invalid output.

**Config and docs**:
- Added `harness/prompts/agent-harness.config.example.json` with `opencode` backend Builder and `copilot` QA/Security examples.
- Updated `harness/prompts/README.md` with active-file inventory, future-orchestrator instructions, correct repo-relative commands, and scoped-diff usage.
- Removed unused duplicate prompt variants: `harness/prompts/builder 2.md`, `harness/prompts/orchestrator 2.md`, and `harness/prompts/qa 2.md`.
- Removed generated `harness/prompts/scripts/__pycache__/` bytecode.
- Updated `.gitignore` to ignore `.harness/` run artifacts and local `harness/prompts/agent-harness.config.json`.

**Verification**:
- `python3 -m py_compile harness/prompts/scripts/agent-loop.py` passed.
- `python3 -m json.tool harness/prompts/agent-harness.config.example.json` passed.
- `harness/prompts/scripts/agent-loop.sh --help` passed.
- Manual smoke run passed: generated `.harness/runs/20260528-134153/` with Builder/QA/Security prompt files and final report.
- `git check-ignore -v .harness/runs/20260528-134153/final-report.md` confirmed generated run artifacts are ignored by `.gitignore`.

### back-010: BibTeX and CSV export

**CSV service** (`api/app/services/csv_io.py`):
- `generate_csv(books: list[Book]) -> str` — formats books as CSV using `csv.writer` + `io.StringIO`.
- 14 columns: id, isbn_13, isbn_10, title, subtitle, authors, publisher, published_year, language, pages, cover_url, dewey_code, notes, created_at.
- Multiple authors joined with `"; "` separator.
- Empty list → valid CSV with headers only, no data rows.

**BibTeX service** (`api/app/services/bibtex_io.py`):
- `generate_bibtex(books: list[Book]) -> str` — formats books as BibTeX using `bibtexparser` 1.4 API (`BibDatabase` + `dumps`).
- `_make_cite_key(book)` — first author surname + year; falls back to UUID prefix (16 hex chars) if no author/year.
- Deduplication: appends incrementing suffix (`author2020`, `author20201`, ...) when cite keys collide.
- Fields: title (+ subtitle with `": "` separator), author (`" and "` joined), publisher, year, isbn, language, note.
- Empty list → empty string (valid empty BibTeX body, not an error).

**Export router** (`api/app/routers/export.py`):
- `GET /export/csv` — auth required, fetches all books ordered by title, returns `text/csv` with `Content-Disposition: attachment; filename=library_export.csv`.
- `GET /export/bibtex` — auth required, fetches all books ordered by title, returns `application/x-bibtex` with `Content-Disposition: attachment; filename=library_export.bib`.

**Tests** (`api/tests/test_export.py`):
- 6 HTTP tests: CSV with books (verify fields, Media-Type, Content-Disposition), CSV empty (headers only, 0 rows), BibTeX with books (verify entry structure, fields), BibTeX empty (empty body, 200), auth required for both endpoints (401).

### back-009: Label templates and PDF generation

**Schemas** (`api/app/schemas/label_template.py`):
- `LabelTemplateCreate` — name (required), width_mm (default 50.0), height_mm (default 30.0), font_size (default 8), show_dewey/show_title/show_barcode (default True).
- `LabelTemplateOut` — id, name, width_mm, height_mm, font_size, show_dewey, show_title, show_barcode, created_at with `from_attributes=True`.
- `LabelGenerateRequest` — book_ids (list[uuid.UUID]), template_id (uuid.UUID).

**PDF service** (`api/app/services/pdf_labels.py`):
- `generate_labels_pdf(books, template) -> bytes` — uses ReportLab Canvas with Code128 barcodes.
- Page size from template `width_mm`/`height_mm`.
- One label per page.
- Optional sections: dewey (bold, slightly larger), title (wrapped to max 3 lines), barcode (Code128 from `book.isbn_13`).
- Returns raw PDF bytes via `BytesIO`.

**Labels router** (`api/app/routers/labels.py`):
- `POST /labels/templates/` — create template (201).
- `GET /labels/templates/` — list templates ordered by name.
- `DELETE /labels/templates/{template_id}` — delete template (204), 404 on missing.
- `POST /labels/generate` — generate PDF. Fetches template (404 if missing), fetches books by `book_ids` (404 if none found), renders PDF, returns `application/pdf`.
- All endpoints require auth (`get_current_user`).

**Tests** (`api/tests/test_labels.py`):
- 8 HTTP tests: create template (201 + verify defaults), list templates, delete template (204 + verify absent), template not found → 404 (via DELETE), generate PDF (200 + Content-Type: application/pdf + non-trivial body length), template not found → 404 (via generate), no books → 404 (empty book_ids), bogus book_ids → 404.

### Carry-forward notes (not addressed in this slice)

- Duplicate tag name should become clean `409`.
- Loan double-return needs a guard or idempotent behavior.
- Tag delete missing-404 test should be added.
- Tag color should be validated.
- `DELETE /books/{id}` with active loans still returns `500`.
- QA approved `back-010`; minor reservation: generated BibTeX cite keys can still collide if a natural key equals a suffixed duplicate key (for example `smith20241`).
- Security verdict: ADVISORY. Non-blocking follow-ups: add CSV formula-injection sanitization before multi-user/shared export scenarios, consider `Cache-Control: private, no-store` on export responses, and revisit unbounded/synchronous export if catalog size grows.

### Prior sessions (carried forward)

**back-001 through back-009** — complete. See `docs/session-log.md` for full history.

## WIP (in-progress at handoff)

Nothing. `back-001` through `back-010` are complete.

## Setup gaps / known issues

- **No tracked local `.env`** — only `api/.env.example` is versioned. Tests self-seed required env vars in `conftest.py`.
- **Runtime startup still needs real config** — requires `DATABASE_URL`, `LIBRARY_USERNAME`, `LIBRARY_PASSWORD`, `JWT_SECRET`.
- **PostgreSQL 18 locally** — local dev uses Homebrew PostgreSQL 18.4 rather than spec's PostgreSQL 17.
- **Frontend not yet scaffolded beyond directories** — `web/` still lacks `package.json` and installed dependencies.
- **Google Books API key is optional** — without it, requests may hit anonymous rate limits.
- **`test_engine` is function-scoped** — drops/creates schema per test (slower but avoids event-loop mismatch with asyncpg).
- **ReportLab PDF generation is synchronous** — post-MVP, consider offloading to a thread pool if latency matters.

## Sensor results

| Sensor | Result |
|--------|--------|
| `source .venv/bin/activate && ruff check .` | All checks passed |
| `source .venv/bin/activate && mypy .` | Success: no issues found in 40 source files |
| `source .venv/bin/activate && pytest` | 52 passed, exit code 0 |

## Suggested next steps

1. **back-011**: CSV and BibTeX import.
2. **front-001**: Next.js scaffold (can run in parallel at any point).
