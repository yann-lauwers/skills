---
name: typescript-patterns
description: "Writes and reviews TypeScript types, assertions, generics, imports and tsconfig to the house conventions — `satisfies`, discriminated unions, `as const` over `enum`, parsing at the boundary, exhaustive `never`, `NoInfer`, TypeScript 6/7 tsconfig and module rules. Use on 'type this', 'fix the types', 'tsconfig', 'generic', 'type guard', 'enum or union', 'branded type', `as`, `!`, `import type`, or any `.ts`, `.tsx`, `.mts`, `.cts` or `tsconfig*.json` edit. Not for components — /react-patterns ; not for NestJS — /nestjs-patterns ; not for Next.js — /nextjs-patterns ."
---

# TypeScript Patterns

House conventions and the patterns a strong model does not reach for unprompted. The repo's own tsconfig and lint config win: a line naming a lint rule is decided by that rule wherever the repo enables it, and holds by hand where it does not · a repo whose ESLint config lacks typescript-eslint's `strict-type-checked` and `stylistic-type-checked` → say so once in the reply.

## Routing table

| Intent | Read |
| --- | --- |
| IF declaring a type, interface, union, constant table or option set | THEN `references/modelling-types.md` |
| IF writing `as`, `!`, a type guard or a `catch`, indexing into an array or record, or handling data from outside the program | THEN `references/assertions-and-boundaries.md` |
| IF writing a generic function or type | THEN `references/generics.md` |
| IF writing a function signature, a condition, a default or a boolean name | THEN `references/functions-and-control-flow.md` |
| IF writing imports, or editing a `tsconfig*.json` | THEN `references/modules-and-config.md` |
| IF the request matches none of the above | THEN `references/modelling-types.md`, and say which row was closest |
