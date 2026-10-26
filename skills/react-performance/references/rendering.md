# Rendering — lists, animation, hydration

What the browser does with what React produced: paint and compositing, offscreen rows, hydration mismatches, and the resource hints that start work earlier.

## Animate the wrapper, not the SVG

Transforming a `<div>` wrapper around an SVG is GPU-accelerated; transforming the SVG itself triggers paint.

## `content-visibility: auto` for long lists

```css
.row { content-visibility: auto; contain-intrinsic-size: auto 80px; }
```

Browser skips offscreen rendering — major win for lists with hundreds of rows.

## Hoist static JSX

```tsx
const STATIC_HEADER = <h1>Title</h1>;
function Page() {
  return <>{STATIC_HEADER}<Body /></>;
}
```

## SVG: reduce coordinate precision

`d="M10.123456,20.654321"` → `d="M10.12,20.65"`. Each digit costs bytes; the visual difference is sub-pixel.

## Hydration no-flicker via inline script

For values needed before hydration (theme, locale), inline a `<script>` that sets `document.documentElement.dataset.*` before React mounts.

## Suppress expected hydration mismatches narrowly

```tsx
<time suppressHydrationWarning>{new Date().toLocaleString()}</time>
```

Use ONLY for known-divergent leaf nodes — never on a tree containing other children.

## `<Activity>` for show/hide instead of mount/unmount

React 19 `<Activity mode="visible|hidden">` keeps tree state and effects mounted but hides — cheaper than unmount/remount for tabs and accordions.

## Ternary over `&&` for conditional render

```tsx
// INCORRECT — `0` renders as text node
{count && <Badge>{count}</Badge>}

// CORRECT
{count > 0 ? <Badge>{count}</Badge> : null}
```

## React DOM resource hints

```tsx
import { preload, preconnect } from "react-dom";
preload("/api/critical", { as: "fetch" });
preconnect("https://api.example.com");
```

## `defer` / `async` on `<script>` tags

`defer` for ordered execution after DOMContentLoaded; `async` for fire-and-forget.
