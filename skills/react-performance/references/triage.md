# Triage — where to start on a slow surface

The order the categories are worked in, what each Core Web Vital points at, and which rules the toolchain already enforces. Read this when the complaint is "it's slow" and no cause is named yet.

Work the categories top-down. A re-render fix on a page that ships a 900KB bundle behind a waterfall moves nothing a user can feel.

## Priority index

| Priority | Category | Prefix | When it matters | Read |
|---|---|---|---|---|
| 1 — CRITICAL | Eliminating Waterfalls | `async-` | Anytime `await` is followed by independent `await` | `waterfalls.md` |
| 2 — CRITICAL | Bundle Size Optimization | `bundle-` | First-load JS, route-level imports, third-party libs | `bundle-size.md` |
| 3 — HIGH | Server-Side Performance | `server-` | RSC, Server Actions, API routes, SSR | `server-side.md` |
| 4 — MEDIUM-HIGH | Client-Side Data Fetching | `client-` | SWR / TanStack Query / raw `fetch` in hooks | `client-fetching.md` |
| 5 — MEDIUM | Re-render Optimization | `rerender-` | High-frequency state updates, parent-child fan-out | `re-renders.md` |
| 6 — MEDIUM | Rendering Performance | `rendering-` | Long lists, animations, hydration | `rendering.md` |
| 7 — LOW-MEDIUM | JavaScript Performance | `js-` | Hot loops, frequent allocations | `javascript-hot-paths.md` |
| 8 — LOW | Advanced Patterns | `advanced-` | Effect-event integration, stable refs | `stable-refs.md` |

## Lighthouse / Web Vitals mapping

| Metric | Most relevant categories |
|---|---|
| **LCP** (Largest Contentful Paint) | Waterfalls, Bundle Size, Resource Hints |
| **INP** (Interaction to Next Paint) | Re-render, Rendering, JavaScript |
| **CLS** (Cumulative Layout Shift) | Rendering (Suspense placement, image dimensions) |
| **TBT** (Total Blocking Time) | Bundle Size, JavaScript, Defer Third-Party |
| **FID** (legacy) | Bundle Size, Hydration |

## What the toolchain already does

- **React Compiler** — auto-memoization
- **Turbopack** — faster builds, better tree-shaking
- **Bundle Analyzer** (`@next/bundle-analyzer`) — visualize first-load JS

Project ships React Compiler → demote every `re-renders.md` manual-memoization rule to review-only. The compiler handles them, and hand-written `useMemo` / `useCallback` becomes noise a reviewer has to read past.
