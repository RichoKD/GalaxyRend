# GalaxyRend Frontend — One‑Page Summary

Purpose: a compact reference for developers — quick start, the reusable BaseLayout contract, dashboard routes, common UI patterns, and fast troubleshooting.

## Quick start

- Install dependencies: npm install
- Dev server: npm run dev (if port 3000 is occupied the dev server will pick the next free port)
- Build: npm run build
- Start production: npm run start

## Project layout (relevant parts)

- `src/components/BaseLayout.tsx` — reusable dashboard layout (background, gradients, header, content wrapper)

# GalaxyRend Frontend — One‑Page Summary

Purpose: a compact reference for developers — quick start, the reusable BaseLayout contract, dashboard routes, common UI patterns, and fast troubleshooting.

## Quick start

Install and run:

- Install dependencies: `npm install`
- Dev server: `npm run dev` (if port 3000 is occupied the dev server will pick the next free port)
- Build: `npm run build`
- Start production: `npm run start`

## Project layout (relevant parts)

- `src/components/BaseLayout.tsx` — reusable dashboard layout (background, gradients, header, content wrapper)
- `src/app/dashboard/page.tsx` — role selection (dashboard root)
- `src/app/dashboard/creators/page.tsx` — Creator dashboard (uses BaseLayout)
- `src/app/dashboard/nodes/page.tsx` — Node dashboard (uses BaseLayout)
- `src/app/dashboard/admin/page.tsx` — Admin dashboard (uses BaseLayout)
- `public/background-image.png` — hero/background asset used by BaseLayout

## BaseLayout — the contract (2‑minute read)

What it provides:

- Fixed background image + dark overlay
- Two cosmic gradient blur overlays (variantable)
- Sticky header with logo, title/subtitle and `headerActions` slot
- Main content wrapper for your page children

Props (essentials):

- `children: ReactNode` — required page content
- `title?: string` — page title shown in the header
- `subtitle?: string` — optional subtitle
- `headerActions?: ReactNode` — optional right-hand actions in header
- `showBackground?: boolean` — toggle background/gradients
- `gradientVariant?: 'blue' | 'cyan' | 'purple' | 'green'` — theme

Gradient mapping (pick by role):

- Creator → `blue` (blue → cyan)
- Node → `cyan` (cyan → purple)
- Admin → `purple` (purple → blue)
- Success → `green`

Quick usage:

```tsx
"use client";

import BaseLayout from "@/components/BaseLayout";

export default function Page() {
  return (
    <BaseLayout title="My Page" subtitle="Short desc" gradientVariant="blue">
      <div className="container mx-auto px-6 py-8">{/* your content */}</div>
    </BaseLayout>
  );
}
```

## Dashboard pages — routes and purpose

- `/dashboard` — role selection (Creator, Node, Admin)
- `/dashboard/creators` — Creator dashboard (stats, job mgmt)
- `/dashboard/nodes` — Node dashboard (jobs, status, earnings)
- `/dashboard/admin` — Admin dashboard (platform health, disputes)

Each dashboard page is intentionally minimal and uses `BaseLayout`. Add your cards, grids and forms inside the container.

## Common UI patterns (copy/paste)

Container example:

```tsx
<div className="container mx-auto px-6 py-8">{/* content */}</div>
```

Card example:

```tsx
<Card className="bg-zinc-900/80 border-zinc-800 p-6 backdrop-blur-sm">
  {/* content */}
</Card>
```

Stats grid:

```tsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
  {/* stats */}
</div>
```

Content grid:

```tsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
  {/* content */}
</div>
```

Action button (gradient):

```tsx
<Button className="bg-gradient-to-r from-blue-600 to-cyan-500">Action</Button>
```

## Routing flow (user experience)

1. User clicks Connect Wallet → lands on `/dashboard`
2. User selects a role → app routes to the respective dashboard path

Ensure Connect Wallet CTAs link to `/dashboard` so users pick role first.

## Troubleshooting — quick fixes

- Background image not visible: confirm `public/background-image.png` exists and `showBackground` is true.
- Module/alias issues importing `@/components/BaseLayout`: check `tsconfig.json` paths and restart the dev server or clear `.next` cache.
- Dev server port in use: `npm run dev` will pick an available port; to force 3000 stop the process using it or change your .env/dev script.
- `starknet-py` / Python issues (backend): use Python 3.11/3.12 if `starknet-py` requires <3.13.

## Quick checklist for new dashboard page

- [ ] Add `"use client"` at the top if you use client-side hooks
- [ ] Import `BaseLayout` and wrap your content
- [ ] Choose `gradientVariant` matching the page role
- [ ] Use the container and Card patterns above for consistent styling
- [ ] Test on mobile (sm), tablet (md) and desktop (lg)

## Next steps / suggestions

- Wire wallet connection to set and remember role (optional)
- Add route guards for admin-only pages
- Implement server-backed data for jobs, nodes and payments
- Add lightweight unit tests for new components/pages

---

File pointers: for details see the original docs in this folder (`BASELAYOUT_GUIDE.md`, `BASELAYOUT_ARCHITECTURE.md`, `DASHBOARD_PAGES.md`, `DASHBOARDS_READY.md`, `TECHNICAL_FLOW.md`).

Keep this file as the “first read” for new frontend contributors.

- [ ] Import `BaseLayout` and wrap your content
