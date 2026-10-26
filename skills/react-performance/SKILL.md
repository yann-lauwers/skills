---
name: react-performance
description: "Ranks React and Next.js performance work by payoff — request waterfalls and bundle size first, micro-optimisations last — and routes to the fix. Use on 'why is this page slow', 'too many re-renders', 'the bundle is huge', 'kill the waterfall', 'LCP regressed', or when `Promise.all`, a barrel import, `next/dynamic`, `React.memo`, `useMemo`, `React.cache`, list virtualisation or hydration cost is weighed. Not for where state lives — /react-patterns ; not for Vite config — /vite-patterns ."
metadata:
  origin: ECC
  source: https://github.com/affaan-m/ECC/blob/main/skills/react-performance/SKILL.md
---

# React Performance

Router over a ranked catalog of React 18/19 and Next.js performance rules, adapted from Vercel Labs `react-best-practices`. Each category lives in its own reference; this file decides which one answers the question in hand.

The ranking is the point. Categories 1-2 change what a user feels on a cold load; 7-8 change a profile flame graph. A pass that starts at the bottom optimises code nobody waits on — `references/triage.md` carries the order, the Core Web Vitals mapping, and which rules the toolchain already enforces.

## Scope

Writing or reviewing React/Next code for speed; diagnosing a slow load, a slow interaction, or high client CPU; auditing first-load JS or a Web Vitals regression; removing waterfalls in Server Components and API routes; cutting re-renders; making long lists, animations or hydration cheap.

## Routing table

| Intent | Read |
| --- | --- |
| IF the complaint is "it's slow" with no cause named, or the priority order is the question | THEN `references/triage.md` |
| IF an `await` is followed by an independent `await`, or a Server Component tree renders in sequence | THEN `references/waterfalls.md` |
| IF first-load JS, barrel imports, dynamic imports or third-party scripts are the subject | THEN `references/bundle-size.md` |
| IF the cost is on the server — RSC caching, Server Action auth, serialization, module-scope state | THEN `references/server-side.md` |
| IF the client fetches, subscribes to a global event, or writes `localStorage` | THEN `references/client-fetching.md` |
| IF a component renders more often than its inputs change, or memoization is being weighed | THEN `references/re-renders.md` |
| IF the subject is a long list, an animation, hydration, or a resource hint | THEN `references/rendering.md` |
| IF a profile names one hot function or loop | THEN `references/javascript-hot-paths.md` |
| IF a callback identity has to stay stable, or something must init once per app load | THEN `references/stable-refs.md` |
| IF the request matches none of the above | THEN `references/triage.md`, say which row was closest |

## Related

- [react-patterns](../react-patterns/SKILL.md) — component and hook design, ahead of any perf question
- [react-testing](../react-testing/SKILL.md) — proving a perf change did not break behaviour

## Attribution

Adapted from Vercel Labs `react-best-practices` (MIT, copyright Vercel Engineering, v1.0.0). Source: https://github.com/vercel-labs/agent-skills/tree/main/skills/react-best-practices — the upstream repo carries the original 70-rule catalog with extended examples.
