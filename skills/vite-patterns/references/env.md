# Env vars and what they leak

How Vite loads `.env` files, which vars reach client code, and the three ways a secret ends up inside the shipped bundle.

Vite loads `.env`, `.env.local`, `.env.[mode]` and `.env.[mode].local` in that order, later overriding earlier. The `*.local` files are gitignored and are where local secrets belong.

## Client-side access

Only `VITE_`-prefixed vars reach client code:

```typescript
import.meta.env.VITE_API_URL   // string
import.meta.env.MODE            // 'development' | 'production' | custom
import.meta.env.BASE_URL        // base config value
import.meta.env.DEV             // boolean
import.meta.env.PROD            // boolean
import.meta.env.SSR             // boolean
```

## Reading env inside the config

```typescript
// vite.config.ts
import { defineConfig, loadEnv } from 'vite'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd())          // VITE_ prefixed only (safe)
  return {
    define: {
      __API_URL__: JSON.stringify(env.VITE_API_URL),
    },
  }
})
```

## `VITE_` is not a security boundary

Every `VITE_` var is **statically inlined into the client bundle at build time**. Minification, base64 encoding and disabled source maps hide none of it — the value is extractable from the shipped JavaScript.

Public values only — API URLs, feature flags, publishable keys. API tokens, database URLs and private keys live server-side behind an API or a serverless function.

## The `loadEnv('')` trap

```typescript
// BAD: '' as the third arg loads ALL env vars — server secrets included —
// and makes them available to inline into client code via `define`.
const env = loadEnv(mode, process.cwd(), '')

// GOOD: explicit prefix list
const env = loadEnv(mode, process.cwd(), ['VITE_', 'APP_'])
```

`envPrefix: ''` in the config does the same damage from the other direction — it exposes every env var to client code.

## Source maps in production

Production source maps ship the original source. Keep them off unless they are uploaded to an error tracker and deleted locally afterwards:

```typescript
build: {
  sourcemap: false,                                  // default — keep it this way
}
```

## `.gitignore` checklist

- `.env.local`, `.env.*.local` — local secret overrides
