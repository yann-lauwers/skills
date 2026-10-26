# ABI shape

## Enums

- A C enum before C23 → force int sizing with a last sentinel valued `INT_MAX` —
  `LIB_THING_MAX_VALUE = LIB_ENUM_MAX_VALUE` where `#define LIB_ENUM_MAX_VALUE INT_MAX`.
- Append values; never reorder or renumber a shipped one.
- The core's own enum declared elsewhere → give each header value an explicit number, and assert the
  two agree at compile time on the core side.

## Structs

- The core declares C layout explicitly on every struct crossing the seam; a default Zig or Rust
  `struct` has none — the spelling is in `languages.md`.
- `bool` crossing the seam is C `_Bool` on both sides, spelled out, never a language's native boolean
  passed through a typedef.
- Never grow a struct passed by value: pass it by pointer with a leading `size` field the callee
  checks, or add a new function beside the old one.

## Functions

- A parameter added → a new symbol, never an edit; keep the old one until every caller has moved.
- Out-parameters are written only on success, and a test named for that pins it.
- Error codes are an enum with a success value, never a mix of negative integers and null returns.
