# HANDOFF.md — Session Memory

> Updated by the agent at the end of each session.
> This file is the context bridge between different sessions.

## Last update

- **Date:** 2026-05-28
- **Session:** front-001: Next.js scaffold
- **Branch / HEAD:** main

## Goals completed this session

### front-001: Next.js 15 scaffold (Next.js 16.2.6 installed)

**Scaffolded Next.js** (`web/`):
- `create-next-app` with App Router, TypeScript, Tailwind v4. Installed version is **Next.js 16.2.6** (latest at time of install).
- Moved `app/` into `src/app/`; updated `tsconfig.json` paths to `"@/*": ["./src/*"]`.
- Initialized **shadcn/ui** (v4.8.2) with Tailwind v4 — created `src/components/ui/button.tsx` and `src/lib/utils.ts`.
- Installed **@zxing/browser**.
- Added ESLint (flat config, `eslint-config-next`) with `lint` script.

**Breaking changes in Next.js 16** (noted in `web/AGENTS.md`):
- `middleware.ts` → **`proxy.ts`** (exported function must be `proxy`, not `middleware`).
- `next lint` CLI is removed; lint script runs `eslint src` directly.

**Files created in `web/src/`:**
- `proxy.ts` — auth guard: unauthenticated → redirect `/login`; authenticated on `/login` → redirect `/catalog`.
- `lib/api.ts` — typed `apiFetch<T>` wrapper against `NEXT_PUBLIC_API_URL`; `ApiError` class.
- `lib/auth.ts` — server functions: `login` (POST `/auth/login`, sets httpOnly JWT cookie), `logout` (deletes cookie), `getToken` (reads cookie).
- `app/login/page.tsx` — placeholder login page.
- `app/catalog/page.tsx` — placeholder catalog page.

**Other files:**
- `web/.env.local.example` — `NEXT_PUBLIC_API_URL=http://localhost:8000`.
- `web/eslint.config.mjs` — ESLint flat config.

## WIP (in-progress at handoff)

Nothing. `front-001` is complete.

## Setup gaps / known issues

- **No tracked local `.env`** — only `api/.env.example` and `web/.env.local.example` versioned.
- **Next.js 16 installed instead of 15** — `create-next-app` installed the latest (16.2.6). Key breaking changes: `proxy.ts` replaces `middleware.ts`; `next lint` CLI removed.
- **`src/middleware.ts` placeholder removed** — the harness had pre-created a `middleware.ts`; it was deleted because Next.js 16 conflicts when both files exist. Auth logic is in `src/proxy.ts`.
- **shadcn added `@base-ui/react` dependency** — included in `package.json` by shadcn init, not manually requested.
- **PostgreSQL 18 locally** — local dev uses Homebrew PostgreSQL 18.4 rather than spec's PostgreSQL 17.
- **ReportLab PDF generation is synchronous** — post-MVP, consider offloading to a thread pool.
- **bibtexparser is lenient** — `bibtexparser.loads()` returns 0 entries for malformed input instead of raising.
- Carry-forward from back-011: duplicate tag name → clean 409; loan double-return guard; tag delete missing-404 test; tag color validation; DELETE /books/{id} with active loans returns 500.

## Sensor results

| Sensor | Result |
|--------|--------|
| `npm run lint` | Passed (0 warnings, 0 errors) |
| `npm run build` | Passed — routes: /, /_not-found, /catalog, /login + Proxy |

## Gate results

| Gate | Result |
|------|--------|
| Builder | COMPLETE — sensors green |
| QA | APPROVED_WITH_RESERVATIONS — no blockers; 3 items deferred to front-002 (shared API_URL config, apiFetch in auth.ts, server-only env var) |
| Security | ADVISORY — postcss CVE (build-time only, no fix available without major downgrade); NEXT_PUBLIC_ in server context; ?from= redirect param needs validation in front-002 |

## Suggested next steps

1. **front-002**: Login page UI — form that calls `login()` server action, error display, redirect to `/catalog`.
2. **front-003**: Book catalog page — grid/list view with search and filters.
