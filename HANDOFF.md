# HANDOFF.md — Session Memory

> Updated by the agent at the end of each session.
> This file is the context bridge between different sessions.

## Last update

- **Date:** 2026-05-28
- **Session:** back-011: CSV and BibTeX import
- **Branch / HEAD:** main

## Goals completed this session

### back-011: CSV and BibTeX import

**CSV service** (`api/app/services/csv_io.py`):
- `parse_csv(content)` — parses CSV using `csv.DictReader`, returns list of field dicts, skips blank rows, raises `ValueError` if missing/empty header.
- `map_csv_row_to_book_data(row)` — maps CSV columns to book fields: `authors` split by `"; "`, `published_year`/`pages` as optional ints via `_to_optional_int`, `id` and `created_at` ignored.
- Imported `cover_url` values are accepted only for `https` scheme.
- Imported ISBN-10/ISBN-13 values are normalized only when they match expected length/shape; invalid values are dropped before persistence.
- `generate_csv` now sanitizes spreadsheet formula prefixes (`=`, `+`, `-`, `@`, `|`, tab/newline) by prefixing cells with `'`.

**BibTeX service** (`api/app/services/bibtex_io.py`):
- `parse_bibtex(content)` — parses using `bibtexparser.loads` (1.4 API), filters to `@book` entries only. `bibtexparser` is lenient; malformed content may parse to 0 entries.
- `map_bibtex_entry_to_book_data(entry)` — maps BibTeX fields: `author` split by `" and "`, `year` as optional int, `isbn` disambiguated into `isbn_13` (13-digit) or `isbn_10`, publisher/language/note carried through.
- Hyphenated/space-separated ISBN values are normalized before storage (for example `978-0-306-40615-7` → `9780306406157`); invalid ISBN values are dropped.
- Exported `generate_bibtex` unchanged.

**Import result schema** (`api/app/schemas/import_result.py`):
- `ImportResult` — `total` (rows/entries processed), `created` (books created), `errors` (list of error strings), `books` (list of `BookOut`).

**Import router** (`api/app/routers/import_.py`):
- `POST /import/csv` — auth required, multipart `.csv` file upload, UTF-8-sig decoding. Parses CSV, maps rows, creates books. Rows missing `title` skipped with error message. Returns `ImportResult`.
- `POST /import/bibtex` — auth required, multipart `.bib` file upload, UTF-8-sig decoding. Parses BibTeX (only `@book` entries), maps entries, creates books. Entries missing `title` skipped with error message. Returns `ImportResult`.
- Uploads are stream-read in 64 KiB chunks and rejected above 1 MB with 413.
- Parsed imports above 5,000 rows/entries are rejected with 413.

**Main** (`api/app/main.py`):
- Registered `import_.router` at `/import` prefix.

**Tests** (`api/tests/test_import.py`):
- 21 HTTP tests: CSV import with books (verify all fields), missing title skipped, empty CSV (headers only, 0 created), empty header rejected, auth required (401), wrong extension (400), extra columns ignored, oversized upload rejected (413), too many rows rejected (413), non-UTF-8 rejected (400), cover_url https-only filtering, invalid ISBN values dropped, BibTeX import with books (verify all fields), normalizes hyphenated ISBN-13, invalid ISBN values dropped, filters @article entries, empty BibTeX (0 entries), auth required (401), wrong extension (400), malformed returns empty (bibtexparser lenient), missing title entry skipped.

### Harness CLI loop hardening (carried from prior session)

See full details in prior session log.

### back-010: BibTeX and CSV export (carried from prior session)

- Export responses now include `Cache-Control: private, no-store`.
- CSV export now sanitizes formula-prefixed cells to reduce spreadsheet injection risk.
- See prior session log for original export implementation details.

### back-009: Label templates and PDF generation (carried from prior session)

See full details in prior session log.

**Tests** (`api/tests/test_labels.py`):
- 8 HTTP tests: create template (201 + verify defaults), list templates, delete template (204 + verify absent), template not found → 404 (via DELETE), generate PDF (200 + Content-Type: application/pdf + non-trivial body length), template not found → 404 (via generate), no books → 404 (empty book_ids), bogus book_ids → 404.

### Carry-forward notes (not addressed in this slice)

- Duplicate tag name should become clean `409`.
- Loan double-return needs a guard or idempotent behavior.
- Tag delete missing-404 test should be added.
- Tag color should be validated.
- `DELETE /books/{id}` with active loans still returns `500`.
- QA approved `back-010`; minor reservation: generated BibTeX cite keys can still collide if a natural key equals a suffixed duplicate key (for example `smith20241`).
- Remaining export risk: revisit unbounded/synchronous export if catalog size grows.

### Prior sessions (carried forward)

**back-001 through back-010** — complete. See `docs/session-log.md` for full history.

## WIP (in-progress at handoff)

Nothing. `back-001` through `back-011` are complete. Backend is fully implemented.

## Setup gaps / known issues

- **No tracked local `.env`** — only `api/.env.example` is versioned. Tests self-seed required env vars in `conftest.py`.
- **Runtime startup still needs real config** — requires `DATABASE_URL`, `LIBRARY_USERNAME`, `LIBRARY_PASSWORD`, `JWT_SECRET`.
- **PostgreSQL 18 locally** — local dev uses Homebrew PostgreSQL 18.4 rather than spec's PostgreSQL 17.
- **Frontend not yet scaffolded beyond directories** — `web/` still lacks `package.json` and installed dependencies.
- **Google Books API key is optional** — without it, requests may hit anonymous rate limits.
- **`test_engine` is function-scoped** — drops/creates schema per test (slower but avoids event-loop mismatch with asyncpg).
- **ReportLab PDF generation is synchronous** — post-MVP, consider offloading to a thread pool if latency matters.
- **bibtexparser is lenient** — `bibtexparser.loads()` returns 0 entries for malformed input instead of raising an error. Import endpoints treat this as no-op (200 OK with 0 books).

## Sensor results

| Sensor | Result |
|--------|--------|
| `source .venv/bin/activate && ruff check .` | All checks passed |
| `source .venv/bin/activate && mypy .` | Success: no issues found in 43 source files |
| `source .venv/bin/activate && pytest` | 74 passed, 1 existing warning, exit code 0 |

## Gate results

| Gate | Result |
|------|--------|
| QA | APPROVED after scoped rerun |
| Security | CLEAN after actionable advisories were fixed |

## Suggested next steps

1. **front-001**: Next.js scaffold — Tailwind v4, shadcn/ui, auth middleware (next logical step; backend is complete).
2. Post-MVP: revisit unbounded/synchronous export if catalog size grows.
