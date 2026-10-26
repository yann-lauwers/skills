# Library mode — publishing a package

1. Emit types → `vite-plugin-dts`, or `tsc --emitDeclarationOnly` as a separate step; `build.lib` emits none.
2. Externalize every peer dependency explicitly → an unlisted peer is bundled into the library, and consumers hit duplicate-runtime errors: two Reacts, two stores, hooks that throw.

```typescript
// vite.config.ts
build: {
  lib: {
    entry: 'src/index.ts',
    formats: ['es', 'cjs'],
    fileName: (format) => `my-lib.${format}.js`,
  },
  rolldownOptions: {                                        // rollupOptions before Vite 8
    external: ['react', 'react-dom', 'react/jsx-runtime'],  // every peer dep
  },
}
```

- `react/jsx-runtime` is the entry most often missed: the automatic JSX transform imports it, so omitting it bundles a second React runtime even with `react` external.
