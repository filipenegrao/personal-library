# HANDOFF.md — Session Memory

> Updated by the agent at the end of each session.
> This file is the context bridge between different sessions.

## Last update

- **Date:** 2026-05-28
- **Session:** front-002: Login page UI
- **Branch / HEAD:** main

## Goals completed this session

### front-002: Login page UI

**QA/Security items from front-001 addressed:**
1. Extracted `API_URL` constant to `src/lib/config.ts` (server-only, `process.env.API_URL`) — imported in both `api.ts` and `auth.ts`.
2. Refactored `auth.ts` `login()` to use `apiFetch` from `api.ts` instead of raw `fetch`.
3. Renamed `NEXT_PUBLIC_API_URL` → `API_URL` in `.env.local.example`.
4. Fixed open-redirect in `proxy.ts` — `?from=` param validated as safe relative path (starts with `/`, not `//`).

**Login page implemented (`src/app/login/page.tsx`):**
- Client component with username + password form
- shadcn/ui `Input`, `Label`, `Button` components
- Calls `login()` server action; on success `router.push('/catalog')`
- Inline error display with `role="alert"`

**New files:**
- `web/src/lib/config.ts` — shared `API_URL` constant
- `web/src/components/ui/input.tsx` — shadcn-style Input (no new packages)
- `web/src/components/ui/label.tsx` — shadcn-style Label (no new packages)

**Modified files:**
- `web/src/lib/api.ts` — imports `API_URL` from `./config`
- `web/src/lib/auth.ts` — uses `apiFetch` + config; `login()` no longer calls `redirect()`
- `web/src/proxy.ts` — safe relative-path guard on `?from=`
- `web/.env.local.example` — `NEXT_PUBLIC_API_URL` → `API_URL`
- `web/src/app/login/page.tsx` — full implementation

## WIP (in-progress at handoff)

Nothing. `front-002` is complete.

## Setup gaps / known issues

- **No tracked local `.env`** — only `api/.env.example` and `web/.env.local.example` versioned.
- **Next.js 16 installed instead of 15** — Key breaking changes: `proxy.ts` replaces `middleware.ts`; `next lint` CLI removed.
- **API_URL is server-only** — `apiFetch` is intended for Server Components / Server Actions only. Client components that need data should use Server Actions or pass data as props.
- **shadcn added `@base-ui/react` dependency** — included by shadcn init.
- **PostgreSQL 18 locally** — local dev uses Homebrew PostgreSQL 18.4 rather than spec's PostgreSQL 17.
- **ReportLab PDF generation is synchronous** — post-MVP, consider offloading to a thread pool.
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
| QA | APPROVED_WITH_RESERVATIONS — no blockers; 4 items deferred to front-003: (1) wire ?from= redirect after login, (2) add `import 'server-only'` to config.ts, (3) fix aria-invalid to target only the failing field, (4) add frontend test runner |
| Security | ADVISORY — same postcss CVE (carry-forward, no fix); config.ts needs server-only guard |

## Suggested next steps

1. **front-003**: Book catalog page — grid/list view with search and filters.
2. **front-004**: Book detail page.
