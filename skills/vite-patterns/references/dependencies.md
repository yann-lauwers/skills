# Dependencies — pre-bundling, CJS interop, SSR externals

Why a dependency that resolves in Node breaks under Vite, and the three knobs that fix it: `optimizeDeps`, the pre-bundle cache, and the SSR externals list.

Vite pre-bundles dependencies once — with Rolldown on Vite 8+, esbuild before — converting CJS/UMD to ESM and collapsing a package's many files into one request — and caches the result under `node_modules/.vite`.

## `optimizeDeps`

```typescript
// vite.config.ts — optimizeDeps
optimizeDeps: {
  include: [
    'lodash-es',                              // force pre-bundle known heavy deps
    'cjs-package',                            // CJS deps that cause interop issues
    'deep-lib/components/**',                 // glob for deep imports
  ],
  exclude: ['local-esm-package'],             // must be valid ESM if excluded
  force: true,                                // ignore cache, re-optimize (temporary debugging)
}
```

`include` is the fix for a CJS dependency whose named exports come back undefined. `exclude` only holds for packages that are already valid ESM. `force: true` is a debugging flag, not a committed setting.

Clear `node_modules/.vite` after switching branches, patching a dependency, or changing a lockfile. A stale pre-bundle cache produces phantom errors that survive a dev-server restart and match nothing in the source.

## SSR externals

Standing up `createServer({ middlewareMode: true })` by hand is framework-author territory — an app wants Remix, TanStack Start, Astro, SvelteKit or Nuxt. What a framework user does tune is the externals list, when a dependency breaks under SSR.

```typescript
// vite.config.ts — ssr options
ssr: {
  external: ['node-native-package'],           // keep as require() in SSR bundle
  noExternal: ['esm-only-package'],            // force-bundle into SSR output (fixes most SSR errors)
  target: 'node',                              // 'node' or 'webworker'
}
```

`noExternal` is the first thing to try — most SSR dependency errors are an ESM-only package being left as a runtime `require()`.
