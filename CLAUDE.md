@AGENTS.md

# personal-library

## Overview

A personal library management web application for cataloging books, generating physical labels (PDF), tracking loans, and exporting/importing bibliography data (BibTeX, CSV). Single-user, self-hosted on a VPS. FastAPI handles all business logic; Next.js 15 consumes the API via fetch.

## Stack

- **Backend**: Python 3.12 + FastAPI 0.115, SQLAlchemy 2 (async), Alembic, python-jose, reportlab, httpx, bibtexparser
- **Frontend**: Next.js 15 (App Router), TypeScript, Tailwind CSS v4, shadcn/ui, @zxing/browser
- **Database**: PostgreSQL 17 (direct instance, no Supabase)
- **Auth**: JWT in httpOnly cookie; single user via env vars (no registration flow)
- **External APIs**: Open Library (ISBN lookup), Google Books (fallback)
- **Proxy**: nginx (production only)

## Repository Structure

```text
personal-library/
├── CLAUDE.md
├── AGENTS.md
├── HANDOFF.md
├── STATUS.json
├── .gitignore
├── api/                          # FastAPI backend
│   ├── pyproject.toml
│   ├── .env.example
│   ├── alembic.ini
│   ├── alembic/
│   │   └── versions/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── auth.py
│   │   ├── deps.py
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── routers/
│   │   └── services/
│   └── tests/
├── web/                          # Next.js 15 frontend
│   ├── package.json
│   ├── next.config.ts
│   ├── tsconfig.json
│   ├── .env.local.example
│   └── src/
│       ├── middleware.ts
│       ├── app/
│       ├── components/
│       └── lib/
└── docs/
    ├── architecture.md
    ├── design.md
    ├── progress.md
    ├── session-log.md
    └── superpowers/
        ├── specs/
        └── plans/
```

## Docs and State Model

- `docs/architecture.md` — stable design intent, layers, dependency rules.
- `docs/progress.md` — human checklist aligned with `STATUS.json`.
- `docs/session-log.md` — append-only history; `HANDOFF.md` is the current snapshot.
- `STATUS.json` — canonical feature tracker.

## Common Commands

```bash
# Backend (from api/)
source .venv/bin/activate
uvicorn app.main:app --reload        # dev server on :8000
ruff check .                          # lint
mypy .                                # type check
pytest                                # run all tests

# Database migrations (from api/)
alembic upgrade head
alembic revision --autogenerate -m "description"

# Frontend (from web/)
npm run dev                           # dev server on :3000
npm run lint
npm run build
```

## Conventions

- Commits: Conventional Commits (`feat:`, `fix:`, `docs:`, `refactor:`, `chore:`).
- After completing a feature: update `HANDOFF.md`, `STATUS.json`, and `docs/progress.md`.
- Append session notes to `docs/session-log.md`.
- Never commit `.env`, `.env.local`, `.venv/`, `node_modules/`, `.next/`.

## References

- [`AGENTS.md`](AGENTS.md) — operational contract (read first)
- [`HANDOFF.md`](HANDOFF.md) — current session snapshot
- [`STATUS.json`](STATUS.json) — machine-readable feature tracker
- [`docs/architecture.md`](docs/architecture.md) — layers and dependency rules
- [`docs/progress.md`](docs/progress.md) — human-readable backlog
- [`docs/superpowers/specs/2026-05-23-personal-library-design.md`](docs/superpowers/specs/2026-05-23-personal-library-design.md) — approved product spec
- [`docs/superpowers/plans/2026-05-24-personal-library.md`](docs/superpowers/plans/2026-05-24-personal-library.md) — implementation plan
