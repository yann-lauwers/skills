# Toolchain, language modes and concurrency settings

Checked on Xcode 27.0 / Swift 6.4 / macOS SDK 27.0. Re-check with `scripts/sil-check.sh` when
the toolchain moves.

## The settings that change the answers

| Behaviour | Xcode build setting | `swiftc` flag | SwiftPM |
| --- | --- | --- | --- |
| Language mode | `SWIFT_VERSION` (5.0 / 6.0) | `-swift-version 5` / `6` | `swiftLanguageModes` / `.swiftLanguageMode(_:)` — tools-version ≥ 6.0 defaults every target to Swift 6 mode unless one of these overrides it; read both |
| Strict checking in Swift 5 mode | `SWIFT_STRICT_CONCURRENCY` (minimal / targeted / complete) | `-strict-concurrency=` | `.enableExperimentalFeature("StrictConcurrency=complete")` |
| Default isolation | `SWIFT_DEFAULT_ACTOR_ISOLATION` (default `nonisolated`) | `-default-isolation MainActor` | `.defaultIsolation(MainActor.self)` — tools-version 6.2 |
| Nonisolated async runs on the caller | `SWIFT_UPCOMING_FEATURE_NONISOLATED_NONSENDING_BY_DEFAULT` | `-enable-upcoming-feature NonisolatedNonsendingByDefault` | `.enableUpcomingFeature("NonisolatedNonsendingByDefault")` |
| Approachable Concurrency | `SWIFT_APPROACHABLE_CONCURRENCY` | `-enable-upcoming-feature ApproachableConcurrency` — an umbrella over `DisableOutwardActorInference`, `GlobalActorIsolatedTypesUsability`, `InferIsolatedConformances`, `InferSendableFromCaptures`, `NonisolatedNonsendingByDefault` | `.enableUpcomingFeature("ApproachableConcurrency")` — the Swift 6.4 package template writes it on every target |

- Read them **per target**: app, extension and test targets routinely differ, and a finding on one is
  not a finding on another.
- `swiftc` does not warn on an unrecognised upcoming-feature name — `-enable-upcoming-feature
  BogusFeature` compiles in silence. Prove a feature is on with a probe whose result flips
  (`scripts/sil-check.sh`).
- Approachable Concurrency turns on `NonisolatedNonsendingByDefault` in Swift 6 mode too. The
  `Swift.xcspec` conditions `SWIFT_APPROACHABLE_CONCURRENCY` on `EFFECTIVE_SWIFT_VERSION == '5'`,
  but the per-feature settings it feeds (`SWIFT_UPCOMING_FEATURE_NONISOLATED_NONSENDING_BY_DEFAULT`,
  `…_INFER_ISOLATED_CONFORMANCES`) default to `$(SWIFT_APPROACHABLE_CONCURRENCY)` with no
  condition. Measured: an xcodebuild of a Swift 6 package failed with `sending 'self.loader' risks
  causing data races` with it off and built with it on, the log showing
  `-enable-upcoming-feature NonisolatedNonsendingByDefault` beside `-swift-version 6`. Trust the
  build log over the spec's condition text.
- Xcode 26 and 27's new-app template ships Swift 5 mode with Approachable Concurrency on,
  MemberImportVisibility on, and default isolation `MainActor` for app targets. A project created
  earlier may have none of these.
- Language mode 7 will turn on `ExistentialAny`, `InternalImportsByDefault`,
  `MemberImportVisibility`, `InferIsolatedConformances`, `NonisolatedNonsendingByDefault` and
  `ImmutableWeakCaptures` (`xcrun swiftc -frontend -print-supported-features`, each `enabled_in:
  "7"`) — adopting them now is adopting Swift 7 semantics early.

## Default isolation per module

Main-actor default isolation belongs to the app module and to modules that exist for UI. A
general-purpose library stays `nonisolated`: called from the main actor it stays on the main actor,
and it can still be used off it. Start single-threaded, add `async`, then `@concurrent`, then actors
only where the main actor is measured as the bottleneck (WWDC25 268). In a package-per-layer layout:
UI adapter targets take `.defaultIsolation(MainActor.self)`; domain, port and non-UI adapter targets
stay nonisolated; every target takes `.enableUpcomingFeature("ApproachableConcurrency")`. With it on,
a `nonisolated async` function in a non-UI target runs on its caller's actor, so an entry point the
main actor calls that must leave it is marked `@concurrent`. SwiftPM
applies no default isolation on its own — the 6.4 template's `swift build -v` shows no
`-default-isolation`. The package layout itself is `modular-packages.md`.

## Swift 5 mode vs Swift 6 mode

| | Swift 5 mode | Swift 6 mode |
| --- | --- | --- |
| Data-race diagnostics | none at `minimal`; warnings at `complete` ("this is an error in the Swift 6 language mode") | errors |
| Property-wrapper actor inference (`@StateObject` making a type `@MainActor`) | still on | off (SE-0401) |
| `Thread.current` / `Thread.isMainThread` from async code | warning | error |
| Runtime isolation checks (SE-0423) in `@objc` thunks and closures handed to unannotated APIs | off | on — a `@MainActor @objc` method called off the main thread **traps**; in Swift 5 mode it runs silently |

## Proving a claim

Match the target's real settings with flags (`-swift-version 5 -strict-concurrency=complete`,
`-enable-upcoming-feature …`, `-default-isolation MainActor`) before compiling to SIL, or the
probe answers a different question:

```sh
sh ${CLAUDE_SKILL_DIR}/scripts/sil-check.sh probe.swift --target <deployment target> -swift-version 6
```

## Moving a target from Swift 5 to Swift 6

1. Turn on `SWIFT_STRICT_CONCURRENCY = complete` in Swift 5 mode; fix warnings module by module.
2. Decide default isolation and Approachable Concurrency for the target deliberately — each changes
   what existing code means, not only what the compiler says.
3. Audit every AppKit/ObjC delegate, notification and callback that can arrive off the main thread:
   Swift 6 mode turns each one reaching `@MainActor` code into a runtime trap (SE-0423). Find them
   before flipping the mode, not from crash reports after.
4. `-disable-dynamic-actor-isolation` switches the runtime checks off per module — a migration
   crutch with a removal plan, never a destination.
5. Flip `SWIFT_VERSION` last, per target.
