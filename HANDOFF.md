# HANDOFF.md — Session Memory

> Updated by the agent at the end of each session.
> This file is the context bridge between different sessions.

## Last update

- **Date:** 2026-05-28
- **Session:** front-003: Book catalog page
- **Branch / HEAD:** main

## Goals completed this session

### front-003: Book catalog page

**Deferred items from front-002 addressed:**
1. `src/lib/config.ts` — `import 'server-only'` added as first line.
2. `src/app/login/page.tsx` — aria-invalid removed from both Inputs; form-level `aria-describedby="login-error"` + `id="login-error"` on error `<p>`.
3. `src/app/login/page.tsx` — `?from=` redirect wired: inner `LoginForm` uses `useSearchParams`; wrapped in `<Suspense>` by outer `LoginPage`; after login validates path and `router.push(dest ?? '/catalog')`.

**New catalog page:**
- `web/src/app/catalog/page.tsx` — async Server Component; awaits `searchParams` prop; fetches `GET /books/` with `Authorization: Bearer` header; renders responsive grid.
- `web/src/components/catalog-filters.tsx` — Client Component (no `useSearchParams` needed — gets `q`/`lang` as props from Server Component); search bar (Enter to submit) + language select (immediate update); `useRouter` + `usePathname` to update URL.
- `web/src/components/ui/card.tsx` — NEW: `Card` + `CardContent`.
- `web/src/components/ui/select.tsx` — NEW: styled native `<select>`.

**Notes:**
- API filter params are `search` and `language`; URL params are `?q=` and `?lang=` — the catalog page maps between them.
- Book cover images use `<img>` (with `eslint-disable-next-line @next/next/no-img-element`) since cover URLs are user-sourced/external and configuring `next/image` remotePatterns for arbitrary domains was out of scope.

## WIP (in-progress at handoff)

Nothing. `front-003` is complete.

## Setup gaps / known issues

- **No tracked local `.env`** — only `api/.env.example` and `web/.env.local.example` versioned.
- **Next.js 16 installed instead of 15** — Key breaking changes: `proxy.ts` replaces `middleware.ts`; `next lint` CLI removed; `searchParams` on pages is a `Promise` and must be awaited.
- **API_URL is server-only** — `apiFetch` is intended for Server Components / Server Actions only. Client components that need data should use Server Actions or pass data as props.
- **shadcn added `@base-ui/react` dependency** — included by shadcn init.
- **PostgreSQL 18 locally** — local dev uses Homebrew PostgreSQL 18.4 rather than spec's PostgreSQL 17.
- **ReportLab PDF generation is synchronous** — post-MVP, consider offloading to a thread pool.
- Carry-forward from back-011: duplicate tag name → clean 409; loan double-return guard; tag delete missing-404 test; tag color validation; DELETE /books/{id} with active loans returns 500.
- **No frontend test runner** — deferred again; no `npm run test` script exists.

## Sensor results

| Sensor | Result |
|--------|--------|
| `npm run lint` | Passed (0 warnings, 0 errors) |
| `npm run build` | Passed — /catalog is ƒ (dynamic), /login is ○ (static) |

## Gate results

| Gate | Result |
|------|--------|
| Builder | COMPLETE — sensors green |
| QA | APPROVED_WITH_RESERVATIONS — see QA report |
| Security | ADVISORY — proceed to final_check |

## Suggested next steps

1. **front-004**: Book detail page — `app/catalog/[id]/page.tsx` with all fields, tags, loan history, edit/delete actions.
2. **front-005**: Book registration with ISBN scanner.
3. Add `next/image` remote patterns if cover image optimization is desired.

## Security review — front-003

**Date:** 2026-05-28
**Verdict:** ADVISORY

### Tools ran
- `npm audit` — 2 moderate findings (postcss transitive dep via Next.js)

### Tools unavailable
- `pip-audit` — not installed in venv
- `semgrep` — not installed
- `gitleaks` — not installed as binary

### Tool-based findings
- **(tool: npm audit)** `postcss@8.4.31` (Next.js transitive dep) — GHSA-qx2v-qp2m-jg93: XSS via unescaped `</style>` in CSS Stringify Output. Severity: **moderate** (CVSS < 9.0). Build-time tool only; not exploitable at runtime. Suggested fix (`npm audit fix --force`) would downgrade Next.js to 9.3.3 — **do not apply**. Resolution: wait for Next.js to ship an internal postcss update.

### Manual review findings
- **(manual)** `?from=` redirect validation in `LoginForm` is correct: `from.startsWith("/") && !from.startsWith("//")` blocks protocol-relative and external URLs. `javascript:` scheme is also blocked since it does not start with `/`. No open-redirect risk.
- **(manual)** `q` and `lang` search params are encoded via `URLSearchParams` before being forwarded to the API — no injection risk.
- **(manual)** `book.cover_url` rendered as `<img src>` — values originate from the API (server-controlled). Backend CSV import validates https-only, but direct `POST /books/` schema (`BookCreate.cover_url: str | None`) has no scheme validation. `javascript:` URLs in `<img src>` do not execute in modern browsers, so XSS risk is low. Pre-existing gap in the backend — not introduced by this diff. Document as carry-forward for back-007 hardening.
- **(manual)** `import "server-only"` added to `config.ts` — prevents accidental client-side import of `API_URL`. Correct.
- **(manual)** No hardcoded secrets, credentials, or tokens in the diff.
- **(manual)** No unsafe deserialization, eval, or pickle usage.
- **(manual)** `(manual) No automated SAST tools available` — semgrep/gitleaks unavailable; review is partially manual.

### Next action
Proceed to final_check. Advisory items do not block merge:
1. postcss moderate CVE — monitor for Next.js update; do not `npm audit fix --force`.
2. `BookCreate.cover_url` scheme validation — carry forward as backend hardening item for back-007.
