# Modules and config

How imports are written and what a current tsconfig holds. Read when writing imports or editing a `tsconfig*.json`.

## Imports

- Imports at the top, bare names at the use site; values via `import { x }`; an import holding only types → `import type { T }`, never `import { type T }` alone, which still loads the module (`consistent-type-imports`, `no-import-type-side-effects`; `verbatimModuleSyntax` on).
- Never an inline `import("mod").T` annotation → a top-level `import type`.
- Dynamic `import()` only for real lazy loading: code-splitting, or breaking a load-order cycle.
- A relative import's extension follows the module mode: `nodenext` → `./x.js` · Node type stripping → `./x.ts` with `rewriteRelativeImportExtensions` · `bundler` or `preserve` → no extension.

## Erasable syntax

- Code run by Node type stripping, or a repo with `erasableSyntaxOnly` → no `enum`, no namespace holding values, no constructor parameter properties (`constructor(private readonly repo: Repo)`), no `import =`.

## tsconfig on TypeScript 6 and 7

- No `baseUrl` (the prefix goes inside `paths`), no `moduleResolution` `node`/`node10`/`classic`, no `target: es5`, no `downlevelIteration`, no `module` `amd`/`umd`/`system`/`none`, no `esModuleInterop: false` — 6.0 deprecates them and 7.0 errors on them.
- `types` defaults to none → list each ambient package the code relies on (`"types": ["node"]`).
- A new tsconfig → `noUncheckedIndexedAccess: true`; it is not part of `strict`.
