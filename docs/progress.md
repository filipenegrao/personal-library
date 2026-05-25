# Progress

> Human-readable backlog. **Canonical task state is `STATUS.json`.**
> Align checkboxes with `STATUS.json` when features move.

Updated: 2026-05-24 (backend-core auth/foundation complete)

---

## Foundation

- [x] docs/specs: approved product spec (`docs/superpowers/specs/2026-05-23-personal-library-design.md`)
- [x] docs/plans: implementation plan (`docs/superpowers/plans/2026-05-24-personal-library.md`)
- [x] repo-001: Repository state reconciliation (done — 2026-05-24, correction pass same day)
- [x] repo-002: Project scaffold — `.gitignore`, `api/`, `web/` (done — 2026-05-24)

## Backend — Core

- [x] back-001: FastAPI setup — config, database, main, deps (done — 2026-05-24)
- [x] back-002: JWT auth — login endpoint, token verification (done — 2026-05-24)
- [x] back-003: SQLAlchemy models + initial Alembic migration (done — 2026-05-25, corrective pass 2026-05-25: typed authors list[str], JSONB alignment, FK ondelete policies)
- [x] back-004: pytest async fixtures with isolated test database (done — 2026-05-24)

## Backend — Books

- [ ] back-005: ISBN EAN-13 validation and normalization
- [ ] back-006: ISBN lookup — Open Library + Google Books fallback
- [ ] back-007: Books CRUD with ISBN lookup endpoint

## Backend — Catalog Features

- [ ] back-008: Tags and loans CRUD
- [ ] back-009: Label templates and PDF generation (reportlab)
- [ ] back-010: BibTeX and CSV export
- [ ] back-011: CSV and BibTeX import (MVP scope per approved spec, Module 6)

## Frontend — Core

- [ ] front-001: Next.js 15 scaffold — Tailwind v4, shadcn/ui, auth middleware
- [ ] front-002: Login page

## Frontend — Catalog

- [ ] front-003: Book catalog page — grid/list view, search, filters
- [ ] front-004: Book detail page
- [ ] front-005: Book registration with ISBN scanner (@zxing/browser)
- [ ] front-006: Loans page
- [ ] front-007: Label generation page

## Done

- [x] docs/specs: approved product spec (2026-05-23)
- [x] docs/plans: implementation plan (2026-05-24)
- [x] repo-001: Repository state reconciliation (2026-05-24)
- [x] repo-002: Project scaffold (2026-05-24)
- [x] back-001: FastAPI setup — config, database, main, deps (2026-05-24)
- [x] back-002: JWT auth — login endpoint, token verification (2026-05-24)
- [x] back-004: pytest async fixtures with isolated test database (2026-05-24)
