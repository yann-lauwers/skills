# Assertions and boundaries

Where a value's type is trusted, and what replaces an assertion. Read when writing `as`, `!`, a type guard or a `catch`, indexing into an array or record, or handling data from outside the program.

## Assertions

- Never a non-null `!` (`no-non-null-assertion`); a class field's definite-assignment `!:` is not one: narrow with an `if`, a `const` rebinding or an early return.
- A narrowing assertion — `as T` from a wider type, `as unknown as T`, `as { foo }` to read a property → fix the source type, or parse the value · a cast that cannot be avoided → once, at the boundary, in the narrowest branch, never at each use site.
- An object literal → annotate it (`const x: T = {…}`) or use `satisfies`; never `{…} as T`, which hides missing fields.
- No runtime guard on a value the compiler already types; delete a dead `typeof`/`instanceof` check (`no-unnecessary-condition`). Data crossing a trust boundary is `unknown` until parsed, so its guards are not dead.

## Boundaries

- Data the program does not control, whose shape the code relies on (a request body, `JSON.parse`, `res.json()`, a queue message, an error payload) → parse it at the boundary with the repo's schema library (`safeParse`) and take the type from the schema · no schema library → a type guard over `unknown`; never a structural `as`.
- A type parameter that appears only in the return type (`get<T>(url): Promise<T>`) is a disguised assertion → return `unknown` and parse at the caller (`no-unnecessary-type-parameters`).
- `catch (e)` → `e` is `unknown`: narrow with `instanceof Error`; never `(e as Error).message`.
- `noUncheckedIndexedAccess` on → an index read is `T | undefined`: narrow it, or iterate with `for…of`; never `arr[0]!`, and never turn the flag off to pass.
- Dropping `null`/`undefined` from an array → `.filter((x) => x != null)`, which TypeScript 5.5+ narrows itself; no hand-written `x is T` predicate.
