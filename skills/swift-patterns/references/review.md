# Reviewing Swift

## Order

1. Read the target's settings (`toolchain-and-modes.md`) and state them at the top of the review —
   a finding true in Swift 6 mode may be moot in Swift 5 mode, and the reverse.
2. Grep the hotspots below, then read each hit in context.
3. Report per file, each finding as: line, the rule it breaks, a short before/after. End with a
   prioritised summary — correctness first, then structure.

## Hotspots

| Pattern | Check |
| --- | --- |
| `// swiftlint:disable` or `// swift-format-ignore` | is the config wrong for this shape? — `format-and-lint.md` § Suppressions |
| `MainActor.assumeIsolated` | is the code provably on main here? Inside a literal `DispatchQueue.main.async` or an `NSResponder` override it is redundant; anywhere unproven it traps in release |
| `Task.detached` | was shedding isolation and priority intended? `Task { @concurrent in }` or a task group usually says it better |
| `Task { }` inside a loop | a task group, so cancellation propagates |
| `@unchecked Sendable` | which lock guards which field — carried by a lock-typed field, or it is a race |
| `nonisolated(unsafe) var` | the synchronising type in its declaration; a never-reassigned one becomes `static let` |
| `withChecked(Throwing)Continuation` | resumed exactly once on every path, including errors and callbacks that never fire; at a macOS 27 floor, `withContinuation(of:)` checks single resume at compile time |
| `Task { try … }` whose value is never stored or awaited | the thrown error is lost — 6.4 warns (`NoUseUnstructuredThrowingTask`) |
| a warning-only hazard in a package (`ActorIsolatedCall` group) | the package escalates the group to an error (`sendable-and-escape-hatches.md` § Warnings that should be errors) |
| `AsyncStream { continuation in … }` | `makeStream(of:)`, `finish()` on every exit; several consumers → `isolation.md` § Keeping the main actor free |
| actor methods that read, `await`, then write | reentrancy — re-read after the `await` or dedupe in-flight work |
| `!` on actor state after an `await` | latent crash |
| `NSEvent.add…Monitor` | the token stored and removed in teardown |
| `activate(ignoringOtherApps:)` | `NSApp.activate()` |
| a C callback body | the body rules in /ffi-boundaries ; here, that it touches no main-actor state directly, which the compiler only warns about |
| `DispatchQueue.global()` calling `@MainActor` code | runs off main at runtime; the compiler only warns |
| a `@MainActor` conformer of `CAMetalDisplayLinkDelegate`, or a display link on a non-main run loop | the SE-0423 trap on the render thread — `metal-and-display-links.md` |
| an API newer than the deployment target | gated by `#available`, at the target the build settings name — not at 14 by habit |
| a SwiftUI view, row or list, or a model a view reads | `swiftui-updates.md` § Review |

Adapted from twostraws' Swift Concurrency skill (output format, hotspot list), extended with the macOS
and C-interop hotspots.
