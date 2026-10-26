# Observation

Checked on Xcode 27.0 / Swift 6.4 / macOS SDK 27.0.

## `@Observable` at the deployment target

- Own a model with `@State private var model = Model()`; pass it down plainly; `@Bindable` where a
  child needs bindings; `@Environment(Model.self)` for shared models. What the `@State` macro
  changed about that declaration is `swiftui-macos.md` § Views and state.
- UI models are `@MainActor @Observable final class`. Without
  `NonisolatedNonsendingByDefault`, a non-isolated `@Observable` whose `async` method is awaited
  from `.task` fails ("sending
  'self.viewModel' risks causing data races"); with it — Approachable Concurrency — the call stays on the main actor and compiles. The
  rule stands either way; only the failing diagnostic depends on the target's settings.
- The generated setter skips notification when an `Equatable` value is unchanged (`!=`) or an object
  reference is identical (`!==`). A type that is not `Equatable` notifies on every set.
- A write on a hot path assigns the whole new value, which reaches that comparison. An in-place
  mutation — `items.append(x)`, `table[key] = sameValue`, `model.selection?.state = …` — goes through the
  generated `_modify`, which notifies whatever the value (macro expansion and probe, Xcode 27).
- A read subscribes to the whole stored property: reading `model.user.name` subscribes to every
  field of `user`, and reading a computed property subscribes to every stored property its getter
  reads. A field that changes on its own is its own stored property; derived values:
  `swiftui-updates.md` § Observation that tracks one row.
- A property wrapper inside `@Observable` needs `@ObservationIgnored`: `@AppStorage` without it fails
  with "invalid redeclaration of synthesized property". Whether a view then updates when that stored
  value changes is unverified — test it before relying on it.
- Views re-render for the properties they read; what a child takes as input:
  `swiftui-updates.md` § A change re-runs one view.
- macOS 27 (SE-0506): `withObservationTracking(options: [.didSet]) { … } onChange: { event in … }`
  for non-coalesced did-set events (options `.willSet`, `.didSet`, `.deinit`; the event can cancel
  the observation), and `withContinuousObservation(options:apply:)` — keep the returned
  non-copyable `ObservationTracking.Token` alive — instead of a hand re-arming loop.
  `Observations { }` (macOS 26) for async iteration. It delivers after the write, can repeat an
  equal value, and lags a reader that needs the effect at once: that reader reads the stored
  property, and an `Equatable` stored property fed from the sequence swallows the repeats (probe,
  macOS 27).

## Outside SwiftUI

On macOS 26+, AppKit tracks `@Observable` properties read inside `draw(_:)`, `layout()`,
`updateConstraints()`, `updateLayer()` (and the `NSViewController` counterparts) and re-runs them
on change; on macOS 15 add `NSObservationTrackingEnabled = YES` to Info.plist. Read model state
there instead of pushing it from sinks. Outside those methods, or below macOS 15, observe with a
re-registering loop:

```swift
@MainActor func track(_ model: Model, _ apply: @escaping @MainActor () -> Void) {
    withObservationTracking { apply() } onChange: {
        Task { @MainActor in track(model, apply) }
    }
}
```

`onChange` fires once per registration, before the new value is stored, and not necessarily on the
main thread — hence the re-arm and the hop. The snippet compiles under
`sil-check.sh -swift-version 6`, with and without `NonisolatedNonsendingByDefault`.

## When `ObservableObject` stays

An existing codebase on `ObservableObject` + `@Published` + Combine, observed from AppKit through
sinks, is not migrated opportunistically: the AppKit observers are the expensive half, and
`@Observable` gives them nothing below macOS 15. At 15 or later, § Outside SwiftUI says what the
AppKit half costs at that target, and the migration is judged against that. `ObservableObject` compiles with only
`import SwiftUI`; `AnyCancellable` needs `import Combine`.
