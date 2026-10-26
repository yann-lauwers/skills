# Export and import spellings

Read the repo's pinned toolchain version and its existing exports before writing a new one; match them.

| Language | Export a function | Callback type | Layout | Checked on |
| --- | --- | --- | --- | --- |
| Zig | `export fn lib_thing_new(...) ?*Thing` | `*const fn (...) callconv(.c) void` | `extern struct`, `enum(c_int)` | the repo's own exports; the repo's Zig skill for the pinned version |
| Rust (2024 edition) | `#[unsafe(no_mangle)] pub extern "C" fn lib_thing_new(...)` | `extern "C" fn(...)` | `#[repr(C)]` | rustc 1.97.1: a bare `#[no_mangle]` fails with "unsafe attribute used without unsafe" |
| Swift (caller) | imports the header through a module map or bridging header; a Swift function exported to C is `@c func lib_thing(...)` (SE-0495, Swift 6.3), and `@c @implementation` implements one the header declares | `@convention(c)` closure, no captures | imported C types | Swift 6.4: `@c func` compiles (one-file probe); `@c @implementation` not compiled |
| C | declared in the header, defined in `.c` | `typedef void (*lib_cb)(void *userdata, ...)` | the header | — |

## Rust specifics

- Hand a Rust object out as a handle with `Box::into_raw`, take it back exactly once with
  `Box::from_raw` in the free function.
- A panic reaching an `extern "C"` function aborts the process, and `catch_unwind` around the call
  does not catch it (rustc 1.97.1: `thread caused non-unwinding panic. aborting.`) → catch inside
  the export with `std::panic::catch_unwind` and return an error code.
- Generate the header with `cbindgen` rather than hand-writing it, and commit the generated file so a
  header diff shows in review.

## Swift specifics

- A header states ownership to the importer with `SWIFT_SHARED_REFERENCE`, `SWIFT_RETURNS_RETAINED` /
  `_UNRETAINED` and `SWIFT_NONESCAPABLE` — not compiled against a real header.
- Wrap a C handle in a Swift class whose `deinit` unregisters callbacks first and frees the handle
  last.
