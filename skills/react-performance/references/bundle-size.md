# Bundle size — first-load JS

What lands in the client bundle and when it loads. Second in payoff after waterfalls, and the category that moves LCP and TBT on a cold visit.

## Direct imports, not barrels

Barrel `index.ts` files force the bundler to walk the entire module graph even when tree-shaking removes most of it. Direct imports save 200-800ms of first-load JS in many real-world apps.

```ts
// INCORRECT
import { Button, Card, Modal } from "@/components";

// CORRECT
import { Button } from "@/components/button";
import { Card } from "@/components/card";
import { Modal } from "@/components/modal";
```

Next.js 13.5+ has `optimizePackageImports`, which automates this for listed packages — use it in the form the installed version's docs give, found through /nextjs-patterns ; manual direct imports are still required for non-listed libs.

## Statically analyzable paths

```ts
// INCORRECT — defeats bundler/trace analysis
const mod = await import(`./pages/${name}`);

// CORRECT — explicit per branch
const mod = name === "home" ? await import("./pages/home") : await import("./pages/about");
```

## Dynamic imports for heavy components

```tsx
import dynamic from "next/dynamic";

const HeavyChart = dynamic(() => import("./heavy-chart"), {
  loading: () => <Skeleton />,
});
```

`ssr: false` → inside a Client Component only, in the form the installed version's docs give.

## Defer third-party scripts

Load analytics, logging, support widgets AFTER hydration. Use `next/script` with `strategy="afterInteractive"` (default) or `"lazyOnload"`.

## Conditional module loading

```tsx
if (user.role === "admin") {
  const { AdminPanel } = await import("./admin/admin-panel");
  // ...
}
```

## Preload on hover/focus

Trigger `<link rel="preload">` or `import()` on hover so the bundle is in cache by the time the user clicks.
