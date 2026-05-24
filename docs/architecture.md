# Architecture — personal-library

## Overview

Two-tier web application: FastAPI backend (`api/`) and Next.js 15 frontend (`web/`). All business logic, data access, PDF generation, and export live in the backend. The frontend is a thin consumer of the API.

## Repository Layout

```
personal-library/
├── api/        # FastAPI + Python 3.12
└── web/        # Next.js 15 (App Router)
```

---

## Backend (`api/`) — Layer Model

Dependencies flow left to right. A layer may only import from layers to its left.

```
config → database → models → services → routers → main
```

| Layer | Path | Responsibility |
|-------|------|----------------|
| `config` | `app/config.py` | pydantic-settings; reads env vars; exposes `settings` singleton |
| `database` | `app/database.py` | SQLAlchemy async engine factory; `Base` declarative base |
| `models` | `app/models/` | ORM table definitions (Book, Tag, BookTag, Loan, LabelTemplate) |
| `services` | `app/services/` | Pure business logic — ISBN validation/lookup, PDF generation, BibTeX/CSV I/O |
| `routers` | `app/routers/` | FastAPI route handlers; orchestrate services + DB session; return HTTP responses |
| `main` | `app/main.py` | App factory, lifespan, CORS middleware, router registration |
| `deps` | `app/deps.py` | FastAPI dependency functions: `get_db`, `get_current_user` |
| `auth` | `app/auth.py` | JWT encode/decode, password hashing — no DB access |

### Forbidden dependencies (backend)

- `services` must not import from `routers` or `main`
- `models` must not import from `services` or `routers`
- `config` and `database` must not import from any other app layer
- Route handlers must not contain business rules that belong in `services`
- Direct external HTTP calls (`httpx`) are only allowed in `services/isbn_lookup.py`

---

## Frontend (`web/`) — Layer Model

```
lib/ → components/ → app/
```

| Layer | Path | Responsibility |
|-------|------|----------------|
| `lib` | `src/lib/` | `api.ts` — typed fetch wrapper; `auth.ts` — server actions for cookie management |
| `components` | `src/components/` | Shared UI components (book-form, isbn-scanner, book-card, loan-form, label-selector) |
| `app` | `src/app/` | Next.js App Router pages; orchestrate components and lib calls |
| `middleware` | `src/middleware.ts` | Auth guard — redirect unauthenticated requests to `/login` |

### Forbidden dependencies (frontend)

- `components` must not import from `app/` pages
- `lib/auth.ts` uses `"use server"` — must not be called from non-async server contexts
- No direct `fetch` to the API outside `lib/api.ts` (consistency, token attachment)

---

## Database

- **PostgreSQL 17** — single instance
- Dev: Docker (`docker run --name pg -e POSTGRES_PASSWORD=... -p 5432:5432 postgres:17`) or local install
- Production: native install on Ubuntu 24.04 VPS
- ORM: SQLAlchemy 2 async (`asyncpg` driver)
- Migrations: Alembic (`alembic upgrade head`)
- Test isolation: separate `personal_library_test` database; fixtures drop/create schema per session

### Tables

| Table | Description |
|-------|-------------|
| `books` | Core catalog — isbn, title, authors (jsonb), cover_url, dewey_code |
| `tags` | Color-coded labels; N:N with books via `book_tags` |
| `book_tags` | Join table — book_id + tag_id composite PK |
| `loans` | Borrower name, dates, returned_at (null = on loan) |
| `label_templates` | Dimensions (mm), font size, visible fields flags |

---

## Runtime Flow

### ISBN Scan → Book Save

1. Browser scans barcode via `@zxing/browser` (client-side)
2. Frontend calls `GET /books/lookup/{isbn}`
3. Router → `services/isbn_validate.py` (checksum) → `services/isbn_lookup.py`
4. Lookup tries Open Library; on miss, falls back to Google Books
5. Returns `BookData` dict; frontend pre-fills form
6. User confirms → `POST /books/` → book saved in PostgreSQL

### Label PDF

1. User selects books + template on `/labels`
2. Frontend calls `POST /labels/generate` with `{book_ids, template_id}`
3. Router fetches books + template from DB → `services/pdf_labels.py` (reportlab)
4. Returns `application/pdf` stream; browser triggers download

### Auth

1. `POST /auth/login` → verifies credentials against env vars → returns JWT
2. Frontend server action stores JWT in httpOnly cookie
3. Next.js middleware reads cookie; unauthenticated → redirect to `/login`
4. API routes require `Authorization: Bearer <token>`; `deps.get_current_user` validates

---

## Safety and Quality Guardrails

- Never store credentials, tokens, or secrets in code — env vars only
- JWT secret must be ≥ 32 random chars in production
- `reportlab` PDF generation is synchronous; run in thread pool if latency matters (post-MVP)
- Duplicate ISBNs allowed with warning — supports multiple physical copies
- Expired token → 401; frontend middleware redirects to `/login`
- `ruff`, `mypy`, `pytest` must all pass before marking a feature `done`
- ESLint + `npm run build` must pass before marking a frontend feature `done`

## Testing Strategy

- **Backend unit tests**: services layer (ISBN validation, lookup mocks via `respx`)
- **Backend integration tests**: route handlers via `httpx.AsyncClient` + `ASGITransport`; isolated test DB
- **Frontend**: manual testing during development; Playwright for critical flows post-MVP
- No structural dependency tests in initial phase — enforce by convention and code review
