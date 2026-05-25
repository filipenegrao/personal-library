# HANDOFF.md — Session Memory

> Updated by the agent at the end of each session.
> This file is the context bridge between different sessions.

## Last update

- **Date:** 2026-05-25
- **Session:** back-005 corrective pass (QA)
- **Branch / HEAD:** main

## Goals completed this session

### back-005 corrective pass

QA rejected `back-005` for one bug:

- `normalize_isbn()` used `digits[:12].isdigit()` to validate the normalized string, which only checked the first 12 characters. A 13-character input like `"978030640615X"` passed the check because the `X` was in position 13 (outside the slice), and the function returned the non-digit string instead of `None`.

**Fix applied:**

- Changed `digits[:12].isdigit()` to `digits.isdigit()` — validates the entire normalized string.
- Added regression test `test_normalize_isbn_nondigit_last_char` asserting `normalize_isbn("978030640615X") is None`.

**Design note:** ISBN-10 values ending in `X` (which is a valid checksum digit in ISBN-10) are intentionally rejected by `normalize_isbn` because this function's contract is *digits-only* normalization. ISBN-10 `X` handling is not in scope for this slice.

### Prior sessions (carried forward)

**back-001, back-002, back-003 (with corrective pass), back-004, back-005** — complete. See `docs/session-log.md` for full history.

## WIP (in-progress at handoff)

Nothing. `back-001` through `back-005` are complete.

## Setup gaps / known issues

- **No tracked local `.env`** — only `api/.env.example` is versioned. Tests self-seed required env vars in `conftest.py`.
- **Runtime startup still needs real config** — requires `DATABASE_URL`, `LIBRARY_USERNAME`, `LIBRARY_PASSWORD`, `JWT_SECRET` via environment or local `.env`.
- **PostgreSQL 18 locally** — local dev uses Homebrew PostgreSQL 18.4 rather than spec's PostgreSQL 17.
- **Frontend not yet scaffolded beyond directories** — `web/` still lacks `package.json` and installed dependencies.
- **`loans.book_id` delete policy is unresolved** — open decision for `back-008`.

## Sensor results

| Sensor | Result |
|--------|--------|
| `source .venv/bin/activate && ruff check .` | All checks passed |
| `source .venv/bin/activate && mypy .` | Success: no issues found in 40 source files |
| `source .venv/bin/activate && pytest` | 11 passed, exit code 0 |

## Suggested next steps

1. **back-006**: ISBN lookup — Open Library + Google Books fallback (`services/isbn_lookup.py`).
2. **back-007**: Books CRUD with ISBN lookup endpoint (`schemas/book.py`, `routers/books.py`).
3. **back-008**: Tags and loans CRUD — must resolve `loans.book_id` delete policy.
4. **front-001**: Next.js scaffold (can run in parallel at any point).
