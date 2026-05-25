# HANDOFF.md — Session Memory

> Updated by the agent at the end of each session.
> This file is the context bridge between different sessions.

## Last update

- **Date:** 2026-05-25
- **Session:** back-003 corrective pass (QA)
- **Branch / HEAD:** main

## Goals completed this session

### back-003 corrective pass

Three items addressed from QA review:

1. **Type annotation fix**: `authors` changed from `Mapped[list]` to `Mapped[list[str]]` in `api/app/models/book.py`.

2. **JSONB alignment**: Switched `authors` column from generic `sqlalchemy.JSON` to `sqlalchemy.dialects.postgresql.JSONB` in both the model and the migration. The architecture doc explicitly says `authors (jsonb)`. Since no production DB exists, the initial migration was amended directly.

3. **Delete policy documented and implemented**:

| FK | Policy | Rationale |
|----|--------|-----------|
| `book_tags.book_id → books.id` | `ON DELETE CASCADE` | Matches ORM `cascade="all, delete-orphan"` on `Book.book_tags`. Deleting a book also deletes its tag associations — DB-level and ORM-level are now aligned. Added `ondelete="CASCADE"` to both model FK and migration FK. |
| `book_tags.tag_id → tags.id` | `ON DELETE RESTRICT` | Made explicit (was implicit NO ACTION). Prevents deleting a tag that is still associated with books — the user must disassociate or delete the books first. |
| `loans.book_id → books.id` | Implicit RESTRICT (NO ACTION) | **Open decision for `back-008`** — should deleting a book preserve its loan history or fail? Default PostgreSQL behavior (`NO ACTION` / `RESTRICT`) means the delete will be rejected if loans exist. No `ondelete` clause added; behavior is documented as-is for now. |

### Files changed in this pass

- `api/app/models/book.py` — `Mapped[list[str]]`, `JSONB`, import cleanup
- `api/app/models/tag.py` — added `ondelete="CASCADE"` / `ondelete="RESTRICT"` to BookTag FKs
- `api/alembic/versions/0001_initial_schema.py` — `sa.JSON()` → `sa.dialects.postgresql.JSONB()`, added `ondelete` to book_tags FKs

### Prior sessions (carried forward)

**back-001, back-002, back-004** — complete. See previous HANDOFF.md entries or `docs/session-log.md`.

**back-003** — SQLAlchemy models (`Book`, `Tag`, `BookTag`, `Loan`, `LabelTemplate`) + Alembic (`alembic.ini`, `env.py`, `0001_initial_schema.py`). Complete with corrective pass applied.

## WIP (in-progress at handoff)

Nothing. `back-001` through `back-004` are complete.

## Setup gaps / known issues

- **No tracked local `.env`** — only `api/.env.example` is versioned. Tests self-seed required env vars in `conftest.py`.
- **Runtime startup still needs real config** — requires `DATABASE_URL`, `LIBRARY_USERNAME`, `LIBRARY_PASSWORD`, `JWT_SECRET` via environment or local `.env`.
- **PostgreSQL 18 locally** — local dev uses Homebrew PostgreSQL 18.4 rather than spec's PostgreSQL 17. SQLAlchemy + asyncpg compatible with both.
- **Frontend not yet scaffolded beyond directories** — `web/` still lacks `package.json` and installed dependencies.
- **No model-level tests yet** — existing 4 tests (app smoke + 3 auth) don't exercise model CRUD. Model-level tests belong in `back-007` (books CRUD) and `back-008` (tags/loans CRUD).
- **`loans.book_id` delete policy is unresolved** — open decision for `back-008`. Currently: deleting a book with active loans will fail at the DB level. Back-008 implementer must decide whether to keep RESTRICT, switch to CASCADE (lose loan history), or SET NULL (disassociate without deleting).

## Sensor results

| Sensor | Result |
|--------|--------|
| `source .venv/bin/activate && ruff check .` | All checks passed |
| `source .venv/bin/activate && mypy .` | Success: no issues found in 40 source files |
| `source .venv/bin/activate && pytest` | 4 passed, exit code 0 |

## Suggested next steps

1. **back-005**: ISBN EAN-13 validation and normalization.
2. **back-006**: ISBN lookup — Open Library + Google Books fallback.
3. **back-007**: Books CRUD with ISBN lookup endpoint (will also add model-level integration tests).
4. **back-008**: Tags and loans CRUD — must resolve `loans.book_id` delete policy.
5. **front-001**: Next.js scaffold (can run in parallel at any point).
