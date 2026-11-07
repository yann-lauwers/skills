---
name: vite-patterns
description: "Configures and debugs Vite. Use on 'the dev server is slow', 'works in dev, breaks in the build', 'proxy the api to the backend', 'the secret ended up in the bundle', HMR, a plugin, `optimizeDeps`, `build.lib`, `manualChunks`, `import.meta.env`, `VITE_` variables, or any `vite.config.*` edit. Not for React bundle-size ranking — /react-performance ; not for Vitest React tests — /react-testing ."
paths:
  - "**/vite.config.ts"
  - "**/vite.config.js"
metadata:
  origin: ECC
  source: https://github.com/affaan-m/ECC/blob/main/skills/vite-patterns/SKILL.md
---

# Vite Patterns

## Routing

| Intent | Read |
| --- | --- |
| Writing or reading `vite.config.ts` — structure, aliases, `command`/`mode` branching, a default being overridden | `references/config.md` |
| Choosing a plugin, filling the type-check gap, or authoring a custom plugin | `references/plugins.md` |
| `.env` files, `import.meta.env`, `loadEnv`, or a value that must not reach the client | `references/env.md` |
| The dev server slow, unreachable from a container, proxying an API, or HMR driven by hand | `references/dev-server.md` |
| Chunking the output, or the built bundle behaving unlike dev — stale chunks, minifier, type errors that shipped | `references/build.md` |
| Publishing an npm package with `build.lib` | `references/library-mode.md` |
| A dependency breaking — CJS interop, `optimizeDeps`, a stale pre-bundle cache, an SSR external | `references/dependencies.md` |
| Reviewing a config diff, or a shape that looks wrong but builds clean | `references/anti-patterns.md` |
| The knob's name is the whole question | `references/quick-reference.md` |
| None of the above | `references/quick-reference.md`, naming the closest row |
