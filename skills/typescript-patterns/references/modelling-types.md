# Modelling types

How a shape, a union or a constant table is declared so the compiler keeps the information. Read when declaring a type, an interface, a union, a constant table or an option set.

- `readonly` properties and `ReadonlyArray` unless mutation is explicit.
- `type` for unions, mapped, conditional and function types; `interface` for extensible object shapes · a shape built from others → `interface X extends A, B`, never `A & B & {…}`, which the compiler checks slower and reports worse.
- A finite option set → an `as const` object or array and a derived union; never `enum` · no magic strings or numbers.
- A union also iterated at runtime → one `as const` array and `type X = (typeof xs)[number]`; never a union and a separate list.
- A config or lookup table → `satisfies T` (or `as const satisfies T`), so the value keeps its literal keys · a table keyed by a union → `satisfies Record<Union, V>`; never `: Record<string, V>`, which accepts a misspelt key.
- State whose fields depend on a status → a discriminated union (`{ status: 'ok'; data } | { status: 'error'; error }`); never one object of optional fields.
- A `switch` over a union → its `default` assigns the value to `never` (or `satisfies never`); never a silent fallback.
- Function members of an `interface` or `type` → property syntax `fn: (x: T) => R`; never method shorthand `fn(x: T): R`, whose parameters escape strict checking (`method-signature-style`).
- Ids or validated strings that must not mix (`UserId`, `OrgId`, `Email`) → a branded type only the parser creates.
