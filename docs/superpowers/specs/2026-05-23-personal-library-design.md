# Personal Library — Design Spec

**Date:** 2026-05-23
**Status:** Approved

---

## Overview

A personal library management web application for cataloging books, generating physical labels, tracking loans, and exporting/importing bibliography data. Designed for single-user personal use, with architecture that supports future multi-user expansion.

---

## Architecture

### Repository Structure

```
personal-library/
├── web/    # Next.js 15 (App Router)
└── api/    # FastAPI + Python 3.12
```

### Frontend (`web/`)

- **Framework:** Next.js 15, App Router
- **UI:** Tailwind CSS v4 + shadcn/ui (latest)
- **ISBN scan:** `@zxing/browser` (camera barcode detection, client-side)
- **Auth:** JWT token stored in httpOnly cookie
- Calls FastAPI directly via fetch in Server Components and Client Components

### Backend (`api/`)

- **Framework:** FastAPI 0.115
- **Python:** 3.12
- **ORM:** SQLAlchemy 2
- **Migrations:** Alembic
- **PDF generation:** reportlab
- **HTTP client:** httpx (async, for ISBN lookup)
- **Auth:** JWT via `python-jose`

### Database

- **PostgreSQL 17** — direct instance on Ubuntu 24.04 VPS (no Supabase)
- Local dev: PostgreSQL via Docker or local install

### Infrastructure

- Dev: FastAPI on `localhost:8000`, Next.js on `localhost:3000`
- Production: both on VPS, nginx as reverse proxy
- Single user — credentials configured via environment variables, no registration flow

---

## Data Model

### `books`

| Column | Type | Notes |
|---|---|---|
| id | uuid PK | |
| isbn_13 | varchar(13) | nullable |
| isbn_10 | varchar(10) | nullable |
| title | text | required |
| subtitle | text | nullable |
| authors | jsonb | array of strings |
| publisher | text | nullable |
| published_year | int | nullable |
| language | varchar(10) | nullable |
| pages | int | nullable |
| cover_url | text | external URL (Open Library / Google Books) |
| dewey_code | varchar(50) | nullable, manual or auto-suggested |
| notes | text | nullable |
| created_at | timestamptz | auto |

### `tags`

| Column | Type | Notes |
|---|---|---|
| id | uuid PK | |
| name | text | unique |
| color | varchar(7) | hex color |

### `book_tags`

| Column | Type |
|---|---|
| book_id | uuid FK → books |
| tag_id | uuid FK → tags |

### `loans`

| Column | Type | Notes |
|---|---|---|
| id | uuid PK | |
| book_id | uuid FK → books | |
| borrower_name | text | |
| loaned_at | timestamptz | |
| due_date | timestamptz | nullable |
| returned_at | timestamptz | nullable, null = still on loan |
| notes | text | nullable |

### `label_templates`

| Column | Type | Notes |
|---|---|---|
| id | uuid PK | |
| name | text | |
| width_mm | float | |
| height_mm | float | |
| font_size | int | |
| show_dewey | bool | |
| show_title | bool | |
| show_barcode | bool | |
| created_at | timestamptz | |

**Design decisions:**
- `authors` as jsonb avoids an unnecessary join table for personal use
- A book without ISBN is allowed (nullable fields) — for rare books, handouts, etc.
- `cover_url` stores the external URL; local download is optional
- Duplicate ISBNs are allowed with a warning (multiple physical copies)

---

## Modules

### 1. Book Catalog

- Full-text search by title, author, ISBN
- Filters: tag, language, year, loan status
- Views: grid (covers) and list
- Sort: title, author, year, date added

### 2. Book Registration

- ISBN input field + camera button (`@zxing/browser`)
- On ISBN detection/entry: FastAPI → Open Library → fallback Google Books → pre-fills form
- Editable form before saving
- Manual entry supported (all fields optional except title)

### 3. Physical Labels (PDF)

- Select one or more books from catalog
- Choose label template (dimensions, visible fields)
- FastAPI generates PDF via reportlab: Dewey code, abbreviated title, author, ISBN as Code 128 barcode
- Direct PDF download

### 4. Loans

- Register: borrower name, loan date, optional due date
- List of open loans with days elapsed
- Mark as returned
- Loan history per book

### 5. Export

- **BibTeX (.bib):** full catalog or selection, compatible with Zotero and Mendeley
- **CSV:** all fields, for backup or spreadsheet import

### 6. Import

- CSV upload with column mapping
- BibTeX upload to import existing catalog (e.g., from Zotero)

---

## Error Handling

### ISBN Lookup
- Open Library fails → auto-retry with Google Books
- Both fail → blank form with clear message, manual entry
- Invalid ISBN (EAN-13 checksum fails) → frontend validation before API call

### Camera Scan
- Permission denied → fallback to manual input with explanatory message
- Non-ISBN barcode detected → validation error with message

### Duplicates
- ISBN already registered → warning with link to existing book; does not block (supports multiple copies)

### PDF Generation
- Title too long for label → truncated with ellipsis (reportlab handles layout)
- No books selected → button disabled

### Export
- Empty catalog → valid empty file with correct headers (no error)
- Missing optional fields → omitted from BibTeX/CSV without breaking format

### Auth
- Expired token → auto-redirect to login
- Invalid credentials → generic error message

---

## Classification

- **Dewey Decimal (simplified):** 3-digit class auto-suggested from Open Library subject data when available; user can override
- **Free tags:** color-coded, N:N relationship with books
- Label displays: Dewey code + abbreviated title + barcode

---

## Testing

### Backend (pytest)
- Smoke tests for all main endpoints
- Integration tests for Open Library → Google Books fallback (mocked with `respx`)
- ISBN EAN-13 checksum validation unit test
- Test fixtures with a separate PostgreSQL test database (`pytest-asyncio`)

### Frontend
- Manual testing during development (personal-use app, fast feedback cycle)
- Playwright for critical flows if the app expands to multiple users

---

## Stack Summary

| Layer | Technology | Version |
|---|---|---|
| Frontend framework | Next.js | 15 (stable) |
| UI | Tailwind CSS | v4 (stable) |
| UI components | shadcn/ui | latest |
| ISBN scan | @zxing/browser | latest stable |
| Backend framework | FastAPI | 0.115 |
| Language | Python | 3.12 |
| ORM | SQLAlchemy | 2.x |
| Migrations | Alembic | latest stable |
| PDF | reportlab | latest stable |
| HTTP client | httpx | latest stable |
| Auth (backend) | python-jose | latest stable |
| Database | PostgreSQL | 17 |
| Proxy | nginx | latest stable |
