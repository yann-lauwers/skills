# Build — chunking, and what only breaks in production

Production output: how to group vendor chunks, why the built bundle can behave unlike the dev server, and what a deploy does to users holding an old chunk map.

## Manual chunks

```typescript
// vite.config.ts — build.rolldownOptions (Vite 8+; build.rollupOptions before)
build: {
  rolldownOptions: {
    output: {
      // Object form: group specific packages
      manualChunks: {
        'react-vendor': ['react', 'react-dom'],
        'ui-vendor': ['@radix-ui/react-dialog', '@radix-ui/react-popover'],
      },
    },
  },
}
```

The function form splits by heuristic instead:

```typescript
// Function form: split by heuristic
manualChunks(id) {
  if (id.includes('node_modules/react')) return 'react-vendor'
  if (id.includes('node_modules')) return 'vendor'
}
```

Group by intent — a vendor bundle, a UI bundle. One chunk per package produces hundreds of tiny files and a request waterfall, so a heuristic returning `id.split('node_modules/')[1].split('/')[0]` is the shape to avoid.

## Dev does not match build

Dev transforms per module with esbuild/Rolldown; build bundles with Rolldown on Vite 8+, Rollup before. CJS libraries in particular can behave differently between the two.

Verify with `vite build && vite preview` before deploying. `vite preview` is a smoke test for the built bundle and **not a production server** — `dist/` goes to a real static host (NGINX, Cloudflare Pages, a static Vercel deploy) or a multi-stage Dockerfile.

## Stale chunks after a deployment

New builds produce new chunk hashes, and a user mid-session requests filenames that no longer exist. Vite ships no answer for this. Two mitigations:

- Keep the previous `dist/assets/` files live for a deployment window.
- Catch dynamic-import errors in the router and force a page reload.

## Minifier

Vite 8+: `build.minify` defaults to `'oxc'` and `'esbuild'` is deprecated · Vite 5–7: `'esbuild'` is the default and `'oxc'` does not exist; `'terser'` is the alternative on both.

## Type checking

`vite build` transpiles only and does not type-check — `references/plugins.md` covers closing the gap.

## Legacy browser support

`@vitejs/plugin-legacy` costs roughly 40% bundle size and breaks source-map-based bundle analyzers. Add it against real analytics showing the browsers that need it, not by default.
