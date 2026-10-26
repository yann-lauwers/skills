# Ownership across the boundary

Every pointer crossing the seam has exactly one owner, and the contract names it.

## Buffers and strings

- A pointer and length handed to a callback → valid only until the callback returns: copy what must
  outlive it before returning, never store the pointer.
- Memory returned to the caller → the side that allocated it exports the matching free —
  `lib_string_free`, `lib_rows_free` — and the caller frees through it, never through another
  allocator's `free()`.
- A sequence — a slice, a Swift array, a Rust `Vec` — crosses as pointer + length.
- A string crossing the seam states whether it is NUL-terminated, and its encoding.

## Opaque handles

- Opaque handle — `typedef struct lib_thing *lib_thing_t;` with a `lib_thing_new` / `lib_thing_free`
  pair.
- Every function that invalidates a handle, the free and any other, has a test named for it.

## Userdata pointers

Userdata — the `void *` a callback registration takes and the core hands back on every call; in
Swift, an `Unmanaged` reference:

| Registration | Meaning | Teardown |
| --- | --- | --- |
| `Unmanaged.passUnretained(obj).toOpaque()` | the core holds the object without owning it; some Swift reference must outlive every callback | **unregister first, then drop the owning reference** — reversed, the core's thread writes into a freed object |
| `Unmanaged.passRetained(obj).toOpaque()` | the core owns one retain | unregister, then `release()` exactly once |

## Keys derived from addresses

- A map keyed by a C pointer's address → remove the entry when the object is destroyed, or key by an
  id the core never reuses.

## Lifetimes that span threads

- An object a callback on another thread can reach → unregister, wait for any in-flight callback
  where the core does not guarantee none remains, then free.
- A test named for that guarantee states which one the core gives.
