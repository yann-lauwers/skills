---
name: vite-patterns
description: "Configures and debugs Vite — `vite.config.ts`, dev server and proxy, HMR, env variables, dependency pre-bundling, plugins, library mode, a production build that behaves unlike dev. Use on 'the dev server is slow', 'works in dev, breaks in the build', 'proxy the api to the backend', 'the secret ended up in the bundle', `optimizeDeps`, `build.lib`, `manualChunks`, `import.meta.env`, `VITE_` variables, or any `vite.config.*` edit. Not for React bundle-size ranking — /react-performance ; not for Vitest React tests — /react-testing ."
paths:
  - "**/vite.config.ts"
  - "**/vite.config.js"
metadata:
  origin: ECC
  source: https://github.com/affaan-m/ECC/blob/main/skills/vite-patterns/SKILL.md
---

# Vite Patterns

Router over Vite's config, dev server, env handling, dependency interop and production build. Each intent pulls one reference; SKILL.md holds the mental model and nothing else.

## Scope

Editing `vite.config.ts` or `vite.config.js`; wiring env vars or a dev proxy; chunking or shrinking build output; publishing a library with `build.lib`; a dependency that resolves in Node and breaks under Vite; a dev server or HMR session behaving unlike the build.

## The model

Five mechanics explain nearly every Vite surprise:

| Mechanic | What it means |
| --- | --- |
| dev serves native ESM | Source is transformed on demand per module request, never bundled — hence the fast cold start and the precise HMR |
| build bundles | Rolldown with the Oxc minifier (v8+), or Rollup with esbuild (v5–v7), tree-shakes, code-splits and minifies — a different pipeline from dev, so the two can disagree |
| deps are pre-bundled | CJS/UMD converted to ESM once (Rolldown on v8+, esbuild before), cached in `node_modules/.vite` — a stale cache is a phantom error |
| plugins are unified | One plugin object serves the dev server's on-demand transforms and the production pipeline alike |
| env is inlined | `VITE_`-prefixed vars become literal constants in the bundle; everything else is invisible to client code, and nothing prefixed is private |

## Routing table

| Intent | Read |
| --- | --- |
| IF writing or reading `vite.config.ts` — structure, aliases, `command`/`mode` branching, a default being overridden | THEN `references/config.md` |
| IF choosing a plugin, filling the type-check gap, or authoring a custom plugin | THEN `references/plugins.md` |
| IF working with `.env` files, `import.meta.env`, `loadEnv`, or a value that must not reach the client | THEN `references/env.md` |
| IF the dev server is slow, unreachable from a container, proxying an API, or HMR is being driven by hand | THEN `references/dev-server.md` |
| IF chunking the output, or the built bundle behaves unlike dev — stale chunks, minifier, type errors that shipped | THEN `references/build.md` |
| IF publishing an npm package with `build.lib` | THEN `references/library-mode.md` |
| IF a dependency breaks — CJS interop, `optimizeDeps`, a stale pre-bundle cache, an SSR external | THEN `references/dependencies.md` |
| IF reviewing a config diff, or a shape looks wrong but builds clean | THEN `references/anti-patterns.md` |
| IF the knob's name is the whole question | THEN `references/quick-reference.md` |
| IF the request matches none of the above | THEN `references/quick-reference.md`, say which row was closest |
