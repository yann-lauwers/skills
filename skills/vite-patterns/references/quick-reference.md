# Quick reference — which knob covers which job

One row per pattern, for picking the knob before opening the file that explains it.

| Pattern | When to Use |
|---------|-------------|
| `defineConfig` | Always |
| `loadEnv(mode, root, ['VITE_'])` | Access env vars in config (explicit prefix) |
| `vite-plugin-checker` | Any TypeScript app |
| `resolve.tsconfigPaths: true` (Vite 8) · `vite-tsconfig-paths` (Vite 7 and below) | Instead of hand-rolled `resolve.alias` |
| `optimizeDeps.include` | CJS deps causing interop issues |
| `server.proxy` | Route API requests to a backend in dev |
| `server.host: true` | Docker, containers, remote access |
| `server.warmup.clientFiles` | Pre-transform hot-path routes |
| `build.lib` + `external` | Publishing npm packages |
| `manualChunks` (object) | Vendor bundle splitting |
| `vite --profile` | Debug a slow dev server |
| `vite build && vite preview` | Smoke-test the prod bundle locally |

Each row's depth: config keys in `config.md`, plugins in `plugins.md`, env and `loadEnv` in `env.md`, proxy / host / warmup / profile in `dev-server.md`, chunking in `build.md`, `optimizeDeps` in `dependencies.md`, `build.lib` in `library-mode.md`.
