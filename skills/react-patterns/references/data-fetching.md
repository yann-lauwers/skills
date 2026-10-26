# Data fetching

Which fetching tool answers which need, and the one shape to keep out of application code. Read when wiring a component to server data, or when a fetch is racing, uncached, or invisible to Suspense.

| Need | Tool |
|---|---|
| Per-request data in Next.js App Router | RSC `await fetch()` |
| Client-side cache + mutations + invalidation | TanStack Query |
| Lightweight client cache + revalidation | SWR |
| Real-time subscriptions | Server-Sent Events, WebSockets, or the lib's subscription API |
| One-off fire-and-forget | `fetch()` in an event handler |
| None of these fits | Treat it as a design question, not a tooling one — settle where the data lives (`render-and-state.md § State location decision tree`) before picking a fetcher |

An API is a schema, a fetcher and a hook, colocated in the feature's `api/` folder; components call the hook, never the fetcher.

Keep `useEffect` + `fetch` out of application data: it races, caches nothing, retries nothing, and integrates with no Suspense boundary.
