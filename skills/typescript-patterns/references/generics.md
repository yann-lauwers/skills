# Generics

What a type parameter is for and how it infers. Read when writing a generic function or type.

- A type parameter earns its place by relating two positions — an argument to the return, or two arguments; one used only in the return type is an assertion (`references/assertions-and-boundaries.md`).
- Several arguments could infer `T`, and one must not decide it (a default, an initial value) → wrap that parameter in `NoInfer<T>` (5.4+).
- A generic that must keep the caller's literals → `<const T extends readonly unknown[]>` (5.0+), so callers never write `as const`; a mutable constraint (`T extends string[]`) cancels `const`.
