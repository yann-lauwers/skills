# API currency — deprecated, current, and newer than the floor

Every row here was compiled one per file (SKILL.md step 3) at macOS 14, 15, 26 and 27 targets on
SDK 27.0 (Xcode 27.0) — the `isMainThread` behaviour row too. Compile an API no reference lists
before recommending it, and compile a row at the project's own
deployment target — a floor read from this table is a claim about the toolchain, not about the
target.

## Replace

| Written from older material | Current |
| --- | --- |
| `NSApp.activate(ignoringOtherApps: true)` | `NSApp.activate()` (macOS 14) — the old form still compiles without a warning and stays `API_TO_BE_DEPRECATED` in `NSApplication.h` |
| `foregroundColor` | `foregroundStyle` |
| `onChange(of:) { new in }` | `onChange(of:) { old, new in }` or `onChange(of:) { }` — the one-parameter form is deprecated at 14 and warns |
| a hand-written `EnvironmentKey` | `@Entry var x: T = default` (what the default may be: `swiftui-macos.md` § Views and state) |
| `ObservableObject` in new SwiftUI-only code | `@MainActor @Observable final class` |
| `Thread.isMainThread` in async code | `MainActor.assertIsolated()` or a synchronous helper |
| `withChecked(Throwing)Continuation` | `withContinuation(of:)` / `Continuation` at macOS 27 — non-copyable, single resume checked at compile time |
| a hand re-arming `withObservationTracking` loop | `withContinuousObservation(options:apply:)` at macOS 27 |
| `FileDocument` | `ReadableDocument` / `Document` (macOS 27) — deprecated by the macOS 27 release notes; the compiler emits no warning |
| `.textFieldStyle(.roundedBorder)` | `.textFieldStyle(.bordered)` with `.textInputBorderShape(.roundedRectangle)` (both macOS 27; soft-deprecated, no warning) |
| `.textFieldStyle(.squareBorder)` | `.textFieldStyle(.bordered)` (macOS 27; soft-deprecated, no warning) |

## Newer than the floor — gate it or avoid it

| API | Floor |
| --- | --- |
| `NSHostingMenu` | macOS 14.4 |
| `Mutex`, `Atomic` (Synchronization) | macOS 15 — `OSAllocatedUnfairLock` at 14 |
| `Tab`, `UtilityWindow`, window placement / restoration / minimize / level modifiers, `WindowDragGesture` | macOS 15 |
| `isolated deinit` on an `actor` | macOS 15.4 (a `@MainActor` class: see `isolation.md` § deinit) |
| `Task.immediate`, `withTaskPriorityEscalationHandler`, `Observations`, `NotificationCenter` main-actor messages | macOS 26 |
| `glassEffect`, SwiftUI `WebView`, `ForEach(x.enumerated())` | macOS 26 |
| `Span`, `InlineArray` | macOS 26 |
| `NSHostingSceneRepresentation`, `NSGestureRecognizerRepresentable` (use, not declaration) | macOS 26 |
| `ToolbarItem.visibilityPriority` | macOS 26.1 |
| `withTaskCancellationShield`, `withContinuation` / `Continuation` | macOS 27 |
| `withObservationTracking(options:)`, `withContinuousObservation` | macOS 27 |
| `NSMenuItem.preferredImageVisibility`, `NSSegmentedControl.role`, `.pickerStyle(.tabs)`, `NSScrollView.refreshController` | macOS 27 |

## Available at 14, often assumed newer

`Task(name:)`, `AsyncStream.makeStream(of:)`, `withObservationTracking`, `@Animatable`, `@Entry`,
`OSAllocatedUnfairLock`, `onGeometryChange`, `withAnimation { } completion:`, `OSSignposter`,
`#bundle`, `@Environment(\.appearsActive)`, `focusSection`, `defaultFocus`, `onMoveCommand`,
`focusedSceneValue`, `NSView.displayLink(target:selector:)`, `CAMetalDisplayLink`, `weak let`,
`~Sendable`, `@c`, `@inline(always)`, `@specialized` (the last five are language features: the
floor is the toolchain, not the OS).

## Does not exist

`CopyButton` — cited by one upstream pack as macOS 15; absent from the SDK.
`withContinuousObservationTracking` — the proposal's name; the shipped one is
`withContinuousObservation`. A cited API that fails to compile in a one-file probe does not ship in
an answer.

## Keeping this current

On each Xcode update, in order:

1. `sh ${CLAUDE_SKILL_DIR}/scripts/sync-apple-skills.sh` — Apple's skills for the new Xcode replace
   the old copy. A `not in this Xcode's pack` line → every row naming that skill moves in the same
   edit.
2. Each row's API compiled one per file at the project's deployment target (SKILL.md step 3); a row
   whose result changed moves in the same edit, in whichever reference states it.
3. `sh ${CLAUDE_SKILL_DIR}/scripts/apple-doc.sh updates/<framework>` for `swiftui`, `appkit` and
   `swift`, and `apple-doc.sh xcode-release-notes/xcode-<major>-release-notes`. A deprecation the
   compiler does not warn about reaches this table only from these pages; it gets a snippet before it
   gets a row.
4. /xcode-integration:swiftui-specialist , `references/soft-deprecated-apis.md` for SwiftUI renames —
   searched, not read whole.
