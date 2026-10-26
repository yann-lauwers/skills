# Functions and control flow

Signatures, conditions, defaults and names. Read when writing a function signature, a condition, a default or a boolean name.

- More than 2 parameters → one typed options object (`@typescript-eslint/max-params`) · a boolean that switches behaviour → two functions.
- Defaults through parameter defaults or `??`, never `||`, which treats `0`, `""` and `false` as missing (`prefer-nullish-coalescing`).
- A nullable number or string in a condition → compare explicitly (`!== undefined`, `!== ''`); never `if (count)` or `.filter(Boolean)` on numbers, which drops `0` (`strict-boolean-expressions`).
- An `if` condition with ≥2 boolean operands or spanning ≥3 lines → a named predicate.
- Max 3 nesting levels → extract or return early (`max-depth`).
- Booleans start with `is`, `has`, `can`, `should`, `did` or `will` (`naming-convention`).
