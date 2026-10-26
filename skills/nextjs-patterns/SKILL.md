---
name: nextjs-patterns
description: "Writes and reviews Next.js code to the house conventions and against the installed version's own docs. Use on 'next.js', 'app router', 'server action', 'route handler', 'revalidate', 'upgrade next', or editing `page.tsx`, `layout.tsx`, `next.config`, `proxy.ts`, `middleware.ts`, a file under `app/` or `pages/`, a server `fetch` or cache tag, or a `next dev` / `next build` error. Not for component shape or the server/client boundary — /react-patterns ; not for waterfalls or bundle size — /react-performance ."
---

# Next.js Patterns

Next's API moves every major and Next ships the docs for it; this skill holds the house conventions and where those docs are, never the API itself.

## The installed version decides

- Next.js → `next` in the nearest `package.json`; in a monorepo the app's own folder is the root.
- Installed version → `node_modules/next/package.json`; absent → the lockfile's resolved `next`.
- Read the relevant guide before writing, from the first source that exists: `node_modules/next/dist/docs/` (16.2+, after installing dependencies) · the web docs, finding the page in `https://nextjs.org/docs/<major>/llms.txt` and reading it with `.md` appended (`/docs/llms.txt` for the latest major; the Pages Router in the `pages/llms.txt` beside it).
- A web docs page describes the version its `version:` line names → an API its `Version History` table dates above the installed version is absent; a page reading "Page Not Found" is a wrong path, never an answer.
- A `next dev` or `next build` error naming a `/docs/messages/...` page → read that page before picking a fix.
- The `nextjs-agent-rules` block in a repo's `AGENTS.md` is Next's own → commit it with the work; never strip it from a diff.
- 16+ with a dev server running → check a change through `next-devtools-mcp` (`get_errors`, `compile_route`) before calling it done, where the repo's `.mcp.json` declares it · not declared → say so once in the reply.
- Work under `pages/` → this section, the proxy/middleware line, the invalidation line and the PR line bind; the rest binds the App Router.

## House conventions

- `page.tsx` composes feature slices and implements no logic.
- Route groups `(group)` name a business area or a shared layout, never a tech layer.
- Mutations — form submissions, UI writes → Server Actions · Route Handlers → webhooks, OAuth and third-party callbacks, proxies, non-UI responses, endpoints a non-React client calls.
- Reads never go through a Server Action, and a Server Component never `fetch`es its own Route Handler.
- `proxy.ts` or `middleware.ts` is no auth boundary; every Route Handler and API route authenticates itself · a Server Action → /react-performance , `references/server-side.md`.
- Every server `fetch` states its caching, in the form the installed version's docs give — the default flips between majors.
- A mutation invalidates what it changed — its cache tags, or under `pages/` its paths — with the invalidation API the installed version's docs give.
- Cache tags are stable names (`product:${id}`), built by one tag function per entity, never spelled inline at two sites.
- A PR that changes caching names the cached scope and its lifetime.
