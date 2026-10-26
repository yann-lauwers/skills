# Code arriving on another thread

C libraries, GCD queues, sockets, `NSEvent` monitors and Combine all call Swift from threads the
compiler knows nothing about. The checks below are what Swift 6.4 actually enforces — several are
warnings, not errors, so a clean build proves less than it looks.

## C callbacks

- A C function pointer cannot capture context: "a C function pointer cannot be formed from a closure
  that captures context". State arrives through `userdata` and `Unmanaged`; who owns it and the
  teardown order are /ffi-boundaries ' contract.
- A callback whose type is **imported from a C header** is `@preconcurrency`: touching main-actor
  state inside it is only a **warning** in Swift 6 mode. A callback type declared in Swift with
  `@convention(c)` gets errors. A non-Sendable object round-tripped through `userdata` draws no
  diagnostic at all.
- The body's own rules — copy what it needs, never block, hop asynchronously at a bounded rate —
  are /ffi-boundaries ', with the worked example.
- **Memory-safe imports.** A C parameter annotated `__counted_by(n)` and `__noescape` imports as
  `Span` / `MutableSpan` (macOS 26) instead of a pointer plus a length; Xcode 27 needs no
  `SafeInteropWrappers` flag for that case, while a `__lifetimebound` return still does.
  `-strict-memory-safety` (SE-0458) flags every unsafe construct on the Swift side and
  `-fbounds-safety` on the C side. Annotate the header before writing a wrapper around a bare
  `UnsafePointer`. Not compiled against a real vendored header here. The ownership annotations in
  the header, and the spelling of a Swift function exported to C, are /ffi-boundaries ' —
  its languages reference.

## Hopping to the main actor

| Form | Treated as main-actor by the compiler |
| --- | --- |
| a closure passed literally to `DispatchQueue.main.async` / `.asyncAfter` / `.sync` | **yes** — `MainActor.assumeIsolated` inside it is a redundant runtime check |
| `let q = DispatchQueue.main; q.async { }` | no |
| `OperationQueue.main.addOperation { }`, `RunLoop.main.perform { }` | no |
| Combine `.receive(on: RunLoop.main).sink { }` | no — `assumeIsolated` inside is the right tool |
| `Task { @MainActor in }` | yes, asynchronously |

## The isolation assertions

`MainActor.assumeIsolated { }` asserts; it never hops. `assumeIsolated`, `assertIsolated()` and
`preconditionIsolated()` all **trap off the main thread in `-Onone` and `-O` builds** on this
runtime — none is compiled out of release. Use `assumeIsolated` only where the code is already on the
main thread and the compiler cannot see it (a Combine sink on `RunLoop.main`, an ObjC delegate
documented as main-thread). Inside an `NSResponder` subclass override (`NSView`, `NSWindow`,
`NSPanel.sendEvent`) the method is already `@MainActor`.

## GCD

Calling a `@MainActor` function from a `DispatchQueue.global()` closure is a **warning**, and at
runtime the function simply runs off the main thread — no trap in Swift 5 or Swift 6 mode. GCD stays
the right tool for C interop, socket servers and synchronous critical sections; flag it only where an
async API would do.

## `NSEvent` monitors

`addLocalMonitorForEvents` / `addGlobalMonitorForEvents` handler closures are not main-actor in
Swift. Installed from `@MainActor` code the closure inherits that isolation, and Swift 6 mode checks
it at runtime. The returned token is `Any?`: store it, and remove it in teardown — from a
`@MainActor` method or an `isolated deinit` (its macOS 14 status: `isolation.md` § deinit), since a
nonisolated `deinit` cannot read it. Global
monitors for key events need the Accessibility grant.

## Socket and file-descriptor servers

`DispatchSource.makeReadSource` on a private queue, accept and parse there (nonisolated), then hop
to the main actor to act on the app's state. Keep the parse off main; keep the state mutation on it.

## Swift 6 mode runtime traps (SE-0423)

A delegate callback AppKit or a C library delivers off the main thread **crashes** in Swift 6 mode
where Swift 5 mode ran it silently — the largest risk in moving an app target to Swift 6. The
mechanism, the mode comparison, and the audit steps are `toolchain-and-modes.md` § Moving a target.
