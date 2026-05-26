# HANDOFF.md — Session Memory

> Updated by the agent at the end of each session.
> This file is the context bridge between different sessions.

## Last update

- **Date:** 2026-05-25
- **Session:** back-007 — Books CRUD with ISBN lookup endpoint
- **Branch / HEAD:** main

## Goals completed this session

### back-007: Books CRUD with ISBN lookup endpoint

**Schemas** (`api/app/schemas/book.py`):
- `TagOut` — id, name, color with `from_attributes=True`.
- `BookCreate` — all book fields + `tag_ids` for tag association during creation.
- `BookUpdate` — same shape as BookCreate but all fields optional, `tag_ids` defaults to `None` (meaning "don't change tags").
- `BookOut` — all persisted fields + `created_at` + `tags: list[TagOut]`.

**Router** (`api/app/routers/books.py`):
- `GET /books/lookup/{isbn}` — normalizes ISBN via `normalize_isbn`, validates EAN-13 checksum, calls `lookup_isbn`. Returns 422 for invalid ISBN, 404 if not found. Fills `isbn_13` from the validated input if the service result omits it (Open Library quirk).
- `POST /books/` — creates a book and optionally attaches tags via `BookTag` join table. Returns 201.
- `GET /books/` — lists books with optional `search`, `language`, `tag_id` filters. Ordered by `created_at` desc.
- `GET /books/{book_id}` — fetches single book with tags, or 404.
- `PATCH /books/{book_id}` — partial update. When `tag_ids` is explicitly provided (not `None`), replaces all tag associations.
- `DELETE /books/{book_id}` — deletes and returns 204.
- Helpers: `_book_to_out`, `_get_book_or_404`, `_sync_tags`.

**Tests** (`api/tests/test_books.py`):
- 9 ORM-level tests using `db_session`: create, list, get, get 404, update, delete, create with tags, filter by tag, search.
- 3 HTTP-level lookup tests using `auth_client` + mocked `lookup_isbn`: invalid ISBN → 422, success → 200 with identifiers, not found → 404.

**Infrastructure fix** (`api/tests/conftest.py`):
- Changed `test_engine` from session-scoped to function-scoped. Session-scoped async fixtures in pytest-asyncio + asyncpg cause `Task got Future attached to a different loop` errors because the engine's connection pool is created in one event loop but used in another. Function scoping ensures each test gets its own engine within its own event loop.

### Prior sessions (carried forward)

**back-001 through back-006 (with corrective passes)** — complete. See `docs/session-log.md` for full history.

## WIP (in-progress at handoff)

Nothing. `back-001` through `back-007` are complete.

## Setup gaps / known issues

- **No tracked local `.env`** — only `api/.env.example` is versioned. Tests self-seed required env vars in `conftest.py`.
- **Runtime startup still needs real config** — requires `DATABASE_URL`, `LIBRARY_USERNAME`, `LIBRARY_PASSWORD`, `JWT_SECRET`.
- **PostgreSQL 18 locally** — local dev uses Homebrew PostgreSQL 18.4 rather than spec's PostgreSQL 17.
- **Frontend not yet scaffolded beyond directories** — `web/` still lacks `package.json` and installed dependencies.
- **`loans.book_id` delete policy is unresolved** — open decision for `back-008`.
- **Google Books API key is optional** — without it, requests may hit anonymous rate limits.
- **`test_engine` is function-scoped** — drops/creates schema per test (slower but avoids event-loop mismatch with asyncpg). If perf becomes a concern, investigate session loop scope config in future pytest-asyncio releases.

## Sensor results

| Sensor | Result |
|--------|--------|
| `source .venv/bin/activate && ruff check .` | All checks passed |
| `source .venv/bin/activate && mypy .` | Success: no issues found in 40 source files |
| `source .venv/bin/activate && pytest` | 26 passed, exit code 0 |

## Suggested next steps

1. **back-008**: Tags and loans CRUD — must resolve `loans.book_id` delete policy.
2. **back-009**: Label templates and PDF generation.
3. **front-001**: Next.js scaffold (can run in parallel at any point).
