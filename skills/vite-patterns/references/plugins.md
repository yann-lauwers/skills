# Plugins — what to install, and authoring one

## Reach for an installed plugin first

| Plugin | Purpose | When to use |
|--------|---------|-------------|
| `@vitejs/plugin-react` | React HMR + Fast Refresh, transformed by Oxc on Vite 8+ (plugin-react 6, or 5.2+), or by esbuild with Babel for Fast Refresh on Vite 7 and below | Default for React apps; a Babel plugin (emotion, MobX decorators) runs beside it through `@rolldown/plugin-babel` with plugin-react 6, through its `babel` option on plugin-react 5 and below |
| `@vitejs/plugin-react-swc` | React HMR + Fast Refresh via SWC | Only where an SWC plugin is needed |
| `vite-plugin-checker` | Runs `tsc` + ESLint in a worker thread with an HMR overlay | **Any TypeScript app** — `vite build` does not type-check |
| `vite-tsconfig-paths` | Honors `tsconfig.json` `paths` aliases | Vite 7 and below; from Vite 8, `resolve.tsconfigPaths: true` instead |
| `vite-plugin-dts` | Emits `.d.ts` files in library mode | Publishing TypeScript libraries |
| `vite-plugin-svgr` | Imports SVGs as React components | React apps using SVGs as components |
| `rollup-plugin-visualizer` | Bundle treemap / sunburst report | Periodic bundle-size audits; last in `plugins` |
| `vite-plugin-pwa` | Zero-config PWA + Workbox | Offline-capable apps |

- `vite build` transpiles and never type-checks → wire `vite-plugin-checker` in dev or `tsc --noEmit` in CI on every TypeScript app.

## Authoring a custom plugin

- No installed plugin fits → start inline in `vite.config.ts`; extract only once a second consumer exists.

```typescript
// vite.config.ts — minimal inline plugin
function myPlugin(): Plugin {
  return {
    name: 'my-plugin',                       // required, must be unique
    enforce: 'pre',                           // 'pre' | 'post' (optional)
    apply: 'build',                           // 'build' | 'serve' (optional)
    transform(code, id) {
      if (!id.endsWith('.custom')) return
      return { code: transformCustom(code), map: null }
    },
  }
}
```

- Key hooks → `transform` (modify source) · `resolveId` + `load` (virtual modules) · `transformIndexHtml` (inject into HTML) · `configureServer` (add dev middleware) · `handleHotUpdate` (custom HMR; `hotUpdate`, per environment since v6, is its planned successor, and Vite does not yet advise moving off `handleHotUpdate`).
- Virtual module → `resolveId` returns `'\0virtual:my-id'`, so other plugins skip it, while user code imports `'virtual:my-id'`.
- Full plugin API → https://vite.dev/guide/api-plugin ; `vite-plugin-inspect` shows the transform pipeline step by step while debugging one.
