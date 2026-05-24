# Design — personal-library

> UI/visual design direction for the personal library web app.
> Stack: Next.js 15, Tailwind CSS v4, shadcn/ui (default "Slate" base color + CSS variables).

---

## Design Principles

- **Utility-first, not minimal**: dense information display over generous whitespace — this is a personal tool used daily, not a marketing page
- **Single-user, no social affordances**: no avatars, no share buttons, no collaborative features in the UI
- **Print-aware**: the label generation flow is the primary print-adjacent feature; everything else is screen-only
- **Mobile-tolerated, desktop-primary**: the catalog and data entry are used from a laptop/desktop; mobile is acceptable for loan lookups but not the primary target

---

## Tokens (Tailwind v4 + shadcn/ui)

### Colors

shadcn/ui "Slate" base, CSS variables:

| Token | Usage |
|-------|-------|
| `background` / `foreground` | Page background + default text |
| `primary` | Action buttons, active states, links |
| `muted` / `muted-foreground` | Secondary text, empty-state labels |
| `border` | Table borders, card borders |
| `destructive` | Delete/remove actions, error states |
| `card` | Book cards, panels |

Accent usage:
- Tag colors are user-defined hex values stored in DB; rendered as colored badges with white text
- Loan "overdue" state: `destructive` text/border on the days-elapsed counter

### Typography

| Role | Family | Notes |
|------|--------|-------|
| Headings | System font stack (shadcn default) | `font-semibold` or `font-bold` |
| Body | System font stack | Regular weight |
| Code / ISBN | Monospace (`font-mono`) | ISBN display in book detail and catalog list |
| PDF labels | Helvetica (reportlab default) | Separate from web typography |

---

## Layout

### Shell

```
┌─────────────────────────────────────────┐
│  Nav: [Library logo] [Catalog] [Loans]  │
│       [Labels] [Export]         [User]  │
├─────────────────────────────────────────┤
│                                         │
│          Page content                   │
│                                         │
└─────────────────────────────────────────┘
```

- Sticky top nav bar with primary pages
- No sidebar — top nav only
- Max content width: `max-w-6xl` centered

### Catalog Page

Two view modes toggled by icon buttons:

**Grid view** (default):
```
┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐
│cover │ │cover │ │cover │ │cover │
│      │ │      │ │      │ │      │
│Title │ │Title │ │Title │ │Title │
│Author│ │Author│ │Author│ │Author│
└──────┘ └──────┘ └──────┘ └──────┘
```

**List view**:
```
┌─────────────────────────────────────────┐
│ ■ Title           Author       Year  tag│
│ ■ Title           Author       Year  tag│
└─────────────────────────────────────────┘
```

Search bar spans full width above the view toggle + filter chips.

### Book Registration

Vertical single-column form. ISBN field + camera scan button at top (prominent). On ISBN resolve, fields auto-populate; user scrolls to review and confirm. Manual entry: all fields except title are optional.

### Label Generation

Split layout:
- Left: book selection list with checkboxes (from catalog, or search)
- Right: template selector + preview (thumbnail mock of label layout)
- Bottom: "Generate PDF" button, disabled when no books selected

---

## Component Patterns

### Book Card (grid)

- `Card` with `aspect-[2/3]` cover image (or placeholder icon when `cover_url` is null)
- Title (2 lines max, ellipsis), author (1 line), year
- Active loan badge overlaid bottom-right when book is on loan

### Tag Badge

- `Badge` variant with `style={{ backgroundColor: tag.color, color: '#fff' }}`
- Used in book cards (grid only), book detail, and filter chips

### ISBN Scanner

- Camera trigger button with camera icon
- On activation: modal with live video + zxing scan overlay
- Auto-close on successful scan; fallback "Enter manually" link

### Empty States

- Catalog empty: illustration + "Add your first book" button
- Loans empty: "No open loans" with muted text
- Labels empty selection: "Select books to generate labels"

---

## Responsive Strategy

- **Desktop (≥1024px)**: primary target; full grid/list catalog, split label page
- **Tablet (768–1023px)**: reduced grid columns (2 instead of 4), nav collapses to hamburger
- **Mobile (<768px)**: single column, list view default, camera scan works natively

Breakpoints follow Tailwind defaults (`sm`, `md`, `lg`).

---

## PDF Labels (reportlab — not web UI)

- Font: Helvetica (bold for Dewey code, regular for title/author, oblique for author)
- Layout per label: Dewey code top-left, title below, author italic, Code128 barcode at bottom
- Long titles/authors truncated at 35 chars with ellipsis
- Label dimensions configurable via LabelTemplate (default 50×30mm)
