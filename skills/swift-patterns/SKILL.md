---
name: swift-patterns
description: "Writes, reviews and migrates Swift for Apple-platform apps (macOS first, SwiftUI and AppKit) — language modes, actor isolation, Sendable, callbacks from C or other threads, AppKit windows and panels, SwiftUI scenes, @Observable, availability, Swift Testing. Use on '@MainActor', 'Sendable', 'data race', 'Swift 6 migration', 'assumeIsolated', 'NSPanel', 'MenuBarExtra', 'the view hitches', 'swiftlint', '.swift-format', any .swift, Package.swift or .xcodeproj change, or a Swift concurrency diagnostic. Not for a C ABI contract — /ffi-boundaries ; not for proving the launched app — /native-app-verification ."
metadata:
  sources: >-
    Apple's agent skills and documentation; AvdLee's and twostraws' Swift agent skills; openai
    build-macos-apps. Re-checked on Xcode 27.0 / Swift 6.4 / macOS SDK 27.0.
---

# Swift on Apple platforms

## Before acting

1. Read each target's `SWIFT_VERSION`, `SWIFT_STRICT_CONCURRENCY`, `SWIFT_DEFAULT_ACTOR_ISOLATION`, `SWIFT_APPROACHABLE_CONCURRENCY`, `SWIFT_UPCOMING_FEATURE_*` and deployment target from `project.pbxproj` or `Package.swift`; targets differ. State them before concurrency advice.
2. Prove a concurrency claim with SIL, never `-typecheck`: `sh ${CLAUDE_SKILL_DIR}/scripts/sil-check.sh <file.swift> [--target <floor>] [swiftc flags]`.
3. Gate every API at that deployment target: one API per file through `sh ${CLAUDE_SKILL_DIR}/scripts/sil-check.sh <file> --target <floor> -swift-version 6 -parse-as-library`; a protocol's file uses the conformance, never only declares it.
4. An API's promise, Apple's recommended pattern, this year's changes → Apple's skill in the table, then `sh ${CLAUDE_SKILL_DIR}/scripts/apple-doc.sh <page>`; `references/sources-of-truth.md` names where Apple is wrong on macOS.

## Routing table

| Intent | Read |
| --- | --- |
| language mode, strict checking, default isolation, upcoming features, Swift 5 → 6, a setting's flag | `references/toolchain-and-modes.md` |
| `.swift-format`, `.swiftlint.yml`, `swift format` and SwiftLint disagree, a format or lint finding, an inline `swiftlint:disable` | `references/format-and-lint.md` |
| a source to trust, Apple's docs or skills; `xcode-integration:*` missing → `scripts/sync-apple-skills.sh` | `references/sources-of-truth.md` |
| `@MainActor`, actors, `nonisolated`, `@concurrent`, `Task` vs `Task.detached`, reentrancy, deinit, work kept off the main actor | `references/isolation.md` |
| a `Sendable` diagnostic, `sending`, `@unchecked Sendable`, `nonisolated(unsafe)`, a lock | `references/sendable-and-escape-hatches.md` |
| a callback from C, GCD, a socket, `NSEvent` monitors, Combine sinks, `assumeIsolated`, `__counted_by`, `Span` | `references/foreign-threads.md` |
| `NSViewRepresentable`, `NSWindow`, `NSPanel`, activation policy, `NSStatusItem`, the responder chain | `references/appkit-hybrid.md` |
| writing or reviewing a SwiftUI view, row or list, or a model a view reads — what each change re-runs, `ForEach` identity, the environment, motion, time text, geometry | `references/swiftui-updates.md` |
| SwiftUI modifiers, localization, soft-deprecated APIs, a custom `Animatable`; Apple's worked examples behind `references/swiftui-updates.md` | /xcode-integration:swiftui-specialist , then `references/swiftui-macos.md` for macOS floors |
| SwiftUI scenes, windows, settings, commands, a macOS 27 behaviour change | `references/swiftui-macos.md`; new APIs → the `xcode-integration:swiftui-whats-new-*` skill |
| `@Observable`, `ObservableObject`, `withObservationTracking` | `references/observation.md` |
| an API that may be deprecated or newer than the floor | `references/api-currency.md` |
| tests — Swift Testing, async tests, test-target isolation | `references/testing.md`; migrating from XCTest → /xcode-integration:modernize-tests |
| VoiceOver, keyboard reach, focus, an accessibility audit | `references/accessibility.md`, then the `xcode-integration:accessibility-*` audits |
| C code adopting `-fbounds-safety` | /xcode-integration:adopt-c-bounds-safety |
| `MTKView`, `CAMetalDisplayLink`, a render thread | `references/metal-and-display-links.md` |
| local packages, `defaultIsolation` per target, `package` access, `#bundle` in a package | `references/modular-packages.md` |
| finding what costs main-thread time — a hitch, a slow scroll, open or update; `OSSignposter`, Instruments, `xctrace`, `sample`; a slow parse or decode; `@inline(always)`, `@specialized` | `references/performance.md` |
| reviewing Swift | `references/review.md` |
| none of the above | `references/isolation.md`, name the closest row |

## Non-negotiables

1. `@MainActor` is justified by the code being UI-bound, never added to silence a diagnostic.
2. `@unchecked Sendable`, `nonisolated(unsafe)` and `@preconcurrency` each have the lock or invariant that makes them true carried in code: a lock-typed field naming what it guards, or a tracker ticket for an import awaiting annotation.
3. Every API newer than the deployment target sits behind `if #available` or `@available`.
