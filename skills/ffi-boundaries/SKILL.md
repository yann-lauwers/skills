---
name: ffi-boundaries
description: "Designs and reviews a boundary where two languages share memory through a C ABI — a Zig, Rust or C core exporting functions and callbacks to a Swift or C++ shell: allocation and free, pointer lifetime across a callback, teardown order, foreign-thread callbacks, layout, the header as contract. Use on 'add an export', 'change the C header', 'the callback crashes', 'use-after-free in the bridge', `Unmanaged`, `callconv(.c)`, `extern \"C\"`, `#[repr(C)]`, `#[no_mangle]`, `cbindgen`. Not for Swift actor isolation — /swift-patterns ; not for proving the launched app — /native-app-verification ."
---

# FFI Boundaries

## Before acting

1. Read the header and both sides of every symbol the change touches.
2. Answer § The contract for every symbol the change touches, before writing either side. Done when each answer sits in a name, a type or a test named for it.
3. Land the core side and the header first, then the caller. Rebuild whatever artifact carries the header — a module map, a bridging header or generated bindings (`cbindgen`, UniFFI) — and prove it fresh before judging the caller — /native-app-verification , `references/build-graph.md`.

## Routing table

| Intent | Read |
| --- | --- |
| IF deciding who allocates, frees or retains — buffers, strings, handles, userdata pointers | THEN `references/ownership.md` |
| IF a callback crosses threads, blocks, or reaches UI-isolated code | THEN `references/threads.md` |
| IF adding or changing a type in the header — an enum, a struct, a string, a version | THEN `references/abi-shape.md` |
| IF writing the export or import in Zig, Rust, Swift or C | THEN `references/languages.md` |
| IF the request matches none of the above | THEN `references/ownership.md`, say which row was closest |

## The contract

Every exported function and callback answers these in its names and types — ownership in the name (`_borrow`, `_take`, a paired `x_free`), the calling thread in the callback's typedef name — and in a test named for each answer the names cannot carry:

| Question | Example answer |
| --- | --- |
| Who owns each pointer argument and return value | "borrowed for the call", "caller frees with `x_free`" |
| How long a borrowed pointer stays valid | "only during the callback" |
| Which thread the function may be called on, and which thread a callback fires on | "any", "the IO read thread", "the main thread" |
| Whether the callee may call back into the library, and which locks are held | "may not re-enter", "no lock held" |
| What null means for each pointer | "null unregisters the callback" |
| How failure is reported | a return code, an out-parameter, never an exception or a panic |

A symbol missing any answer — in its name, its type or a test named for it — is unfinished.

## Proving it

- Test each side at the boundary: the core's own tests for the export, the caller's tests for its
  use, and one test for teardown order — register, destroy, fire, and assert nothing was written.
- Run the caller under Address Sanitizer and Thread Sanitizer — /swift-patterns carries the Xcode
  invocation — and the core with its runtime safety on (Zig Debug or ReleaseSafe, Rust debug
  assertions).
- A crash in the caller on a thread it never spawned is a boundary defect until the contract rules it
  out.
