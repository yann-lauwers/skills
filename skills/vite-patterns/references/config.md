# Config — file shape and the keys that matter

What `vite.config.ts` looks like, how it branches on command and mode, and the six keys whose defaults are worth knowing before overriding one.

## Basic config

```typescript
// vite.config.ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: { '@': new URL('./src', import.meta.url).pathname },
  },
})
```

`defineConfig` always — it is what gives the object type inference. Hand-rolled `resolve.alias` entries that duplicate `tsconfig.json` `paths` go to `resolve.tsconfigPaths: true` on Vite 8, `vite-tsconfig-paths` on Vite 7 and below (`references/plugins.md`).

## Conditional config

The export takes a function when the config differs between `vite dev` and `vite build`:

```typescript
// vite.config.ts
import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig(({ command, mode }) => {
  const env = loadEnv(mode, process.cwd())   // VITE_ prefixed only (safe)

  return {
    plugins: [react()],
    server: command === 'serve' ? { port: 3000 } : undefined,
    define: {
      __API_URL__: JSON.stringify(env.VITE_API_URL),
    },
  }
})
```

`command` is `'serve'` or `'build'`; `mode` is the `--mode` value, defaulting to `development` on serve and `production` on build. The `loadEnv` third argument is a security boundary — `references/env.md § The loadEnv('') trap`.

## Key config options

| Key | Default | Description |
|-----|---------|-------------|
| `root` | `'.'` | Project root (where `index.html` lives) |
| `base` | `'/'` | Public base path for deployed assets |
| `envPrefix` | `'VITE_'` | Prefix for client-exposed env vars |
| `build.outDir` | `'dist'` | Output directory |
| `build.minify` | `'oxc'` (Vite 8+), `'esbuild'` (Vite 5–7) | Minifier (that default, `'terser'`, or `false`) |
| `build.sourcemap` | `false` | `true`, `'inline'`, or `'hidden'` |
