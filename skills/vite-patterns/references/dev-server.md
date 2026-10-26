# Dev server — proxy, HMR, reachability, speed

Everything about `vite dev`: routing API calls to a backend, the manual HMR API, binding inside a container or a monorepo, and the four things that make a cold dev server slow.

## Proxying an API backend

```typescript
// vite.config.ts — server.proxy
server: {
  proxy: {
    '/foo': 'http://localhost:4567',                    // string shorthand

    '/api': {
      target: 'http://localhost:8080',
      changeOrigin: true,                               // needed for virtual-hosted backends
      rewrite: (path) => path.replace(/^\/api/, ''),
    },
  },
}
```

WebSocket routes add `ws: true` to the route config.

## Containers and reverse proxies

Vite binds to `localhost`, which is unreachable from outside a container:

```typescript
// vite.config.ts — Docker/container setup
server: {
  host: true,                                  // bind 0.0.0.0
  hmr: { clientPort: 3000 },                   // if behind a reverse proxy
}
```

## Monorepo file access

File serving is restricted to the project root, so a workspace package outside it is blocked:

```typescript
// vite.config.ts — monorepo file access
server: {
  fs: {
    allow: ['..'],                             // allow parent directory (workspace root)
  },
}
```

## The HMR API

Framework plugins handle HMR on their own. `import.meta.hot` is for custom state stores, dev tools, and framework-agnostic utilities that have to survive an update.

```typescript
// src/store.ts — manual HMR for a vanilla module
if (import.meta.hot) {
  // Persist state across updates (must MUTATE, never reassign .data)
  import.meta.hot.data.count = import.meta.hot.data.count ?? 0

  // Cleanup side effects before module is replaced
  import.meta.hot.dispose((data) => clearInterval(data.intervalId))

  // Accept this module's own updates
  import.meta.hot.accept()
}
```

Mutate `import.meta.hot.data` properties; reassigning the object drops the persisted state. Every `import.meta.hot` block is tree-shaken out of production, so no guard removal is needed.

## Barrel files are the top dev-server slowdown

A barrel (`index.ts` re-exporting a directory) forces Vite to load every re-exported file for a single imported symbol — the slowdown the official docs flag first.

```typescript
// BAD — importing one util forces Vite to load the whole barrel
import { slash } from '@/utils'

// GOOD — direct import, only the one file is loaded
import { slash } from '@/utils/slash'
```

## Explicit import extensions

Each implicit extension costs up to six filesystem checks via `resolve.extensions`, which compounds in a large codebase.

```typescript
// BAD
import Component from './Component'

// GOOD
import Component from './Component.tsx'
```

Narrow `tsconfig.json` `allowImportingTsExtensions` and `resolve.extensions` to the extensions actually in use.

## Warm up the hot paths

`server.warmup.clientFiles` pre-transforms known entries before the browser asks for them, which removes the cold-load request waterfall on a large app.

```typescript
// vite.config.ts
server: {
  warmup: {
    clientFiles: ['./src/main.tsx', './src/routes/**/*.tsx'],
  },
}
```

## Profiling a slow dev server

Start with `vite --profile`, interact with the app, then press `p+enter` to write a `.cpuprofile`. Load it in https://www.speedscope.app — the time usually sits in a community plugin's `buildStart`, `config` or `configResolved` hook.
