# SwiftUI that re-runs only what changed

Measured on Xcode 27.0 / macOS SDK 27.0, `-O` builds, a 120 Hz display, in a SwiftUI and AppKit
Mac app whose 120-row list took 1.2 s of main-thread time per streamed update before these
rules, and in probes beside it; a number below names what it was measured on. Floors of the
macOS 15 scroll and time APIs: `swiftui-macos.md` § Views and state. Apple's worked examples for
identity, data flow, the environment and view structure: /xcode-integration:swiftui-specialist ,
`references/foreach.md`, `dataflow.md`, `environment.md`, `structure.md`.

## A change re-runs one view

- A view type is the boundary a change re-runs: each section of a screen is its own `View` struct
  with narrow inputs, and the parent only composes them. A computed property or `@ViewBuilder`
  helper is inlined into its parent's body. One screen body owning sidebar, header, list, input
  and settings re-ran every one of them on each streamed row and keystroke.
- A child's inputs are values plus the model reference it acts on: `Row(title:isOpen:model:)`, and
  its buttons call `model` inside its own body. A closure input defeats the comparison: a child
  taking a closure that captured its parent re-ran on 2 of 3 parent runs at `-O` and 1 of 3 at
  `-Onone`. `.equatable()` with the closure left out of `==` skips the row and keeps a stale
  capture.
- A value input carries only the fields the view reads; a struct input compares field by field on
  every parent run.
- `init` copies its inputs; parsing and grouping arrive already done, and `body` formats through
  `Text(_:format:)`, with no formatter of its own.
- State one row owns — hover, a pressed flag — is that row's `@State`. A table-wide `hoveredRow`
  re-ran the whole table on every mouse move.
- A value read only for `onChange` lives in its own `ViewModifier`, whose body the change re-runs
  in place of the host's.
- Every key-path `@Environment` a view declares is one its body reads: the declaration alone
  subscribes.
- Two looks of one view are a ternary inside the modifier — `.opacity(dim ? 0.4 : 1)`,
  `AnyShapeStyle` when the branches' types differ; an `if`/`else` swaps the view's identity and
  resets its state.

## Observation that tracks one row

- Each row reads its own persisted `@Observable` box, created when its data first arrives and kept
  in the parent's store; the list reads only the ordered ids. The store observes `rowOrder: [ID]`,
  keeps the boxes in an `@ObservationIgnored` dictionary, and writes a box only when that row's
  version moved. Measured: a counter tick re-ran only the status cell, a moved row one cell, the same
  version re-applied nothing, an append only the column.
- A cache is keyed by the revision of what it covers — one row, one group. One global revision
  counter discarded every cache on every entry, and a per-row lookup that refolded its whole group
  cost 713 ms at 60 rows and 1.19 s at 120.
- A derived value is a stored property, recomputed in the `didSet` or method that changes its
  inputs, and read in `body` as that one property. A computed `groups` on a model regrouped on
  every body run of every reader. What a read subscribes to: `observation.md` § `@Observable` at
  the deployment target.
- Many views reading one small slice of a large model → that slice is its own `@Observable`.
- A row's open state, selection or choice → one object or `@State` per row, bound through a key
  path: `$model[isOpen: id]`. A `Binding(get:set:)` over one shared dictionary re-ran every row on
  any write, an equal write and a key no row shows included.

## The environment holds what rarely changes

- The environment carries constants and models, injected once at the scene root; an `@Observable`
  passed by type compares by identity. A `Bool` written to the environment at the root cost every
  environment reader a check: 16.6 ms per change with 1 500 readers against 3.9 ms through an
  `@Observable`, with no reader's body run in either.
- A fast-changing value — scroll offset, size, pointer, a modifier key held, focus-ring
  visibility, a tick — lives on an `@Observable` injected once, and views read a coarse stored
  result the model computes (`isWide`, `hasReachedEnd`). A comparison written in `body` still
  subscribes the view to every raw change.
- Behaviour in the environment is a struct of stored values with `callAsFunction`, or an
  `@Observable` model with methods. A closure compares unequal on every write: an array of closure
  structs rebuilt in a parent's body re-ran every reader on every parent run. What an `@Entry`
  default may be: `swiftui-macos.md` § Views and state.

## Lists

- An element's id is small, immutable and created when the element is stored: a server id, a URL,
  a `UUID` kept in the model. Position (`indices`, `\.offset`), an editable field and a whole
  hashed struct (`id: \.self`) each move or rehash as the data changes; a run's steps keyed by
  offset spent 31.8 s in `ForEachChild` under the SwiftUI instrument.
- Each `ForEach` element yields one root view: a `switch` or `if` sits inside a `VStack`, and an
  element that draws nothing is filtered out before the `ForEach`.
- A filtered, sorted or grouped collection is stored where its inputs change; the `ForEach` reads
  the prepared array.
- A long scrolling list is one `LazyVStack` with one cell per row: `ScrollView { LazyVStack(spacing:
  0) { ForEach(rowOrder, id: \.self) { RowCell(box: store[$0]) } }.scrollTargetLayout() }`, nested
  groups flattened into rows, spacing carried by each row's own padding.
- A row is final when first placed: its look derives from its inputs at first placement, closed
  content is absent, and no `onAppear` or `onGeometryChange` sets state that changes its height
  afterwards. A lazy stack estimates unplaced rows from the average of
  placed ones and moves offset and content together, so a −15 326 pt estimate correction cost about
  9 ms and displaced nothing; what shows on screen is a row whose height changes after placement.
- Opening a long list prepares what fills the screen first — rows from the newest until about twice
  the viewport's lines — then the rest off the main actor, inserted as one change. Sized by groups
  instead of rows, the first pass still cost 33–92 ms when one group held 400 rows.
- A list that stays at its end while it grows binds `ScrollPosition(idType:edge: .bottom)` through
  `.scrollPosition` with `.defaultScrollAnchor(.bottom, for: .initialOffset)`, and a small state
  machine releases on `onScrollPhaseChange` reporting `.tracking` or `.interacting`, on
  `onScrollGeometryChange` seeing an upward move more than 1 pt from the end, and on a row opening;
  it re-engages at the end or on submit. Without it, a scroll AppKit started — a scroller drag, Page
  Up — was undone by the next growth.

## Collapsed content

Collapsed content is built only while open; the content is a builder the fold calls only then:

```swift
VStack(alignment: .leading, spacing: 0) {
    if isOpen { content().transition(.opacity) }
}
.fixedSize(horizontal: false, vertical: true)
.frame(maxWidth: .infinity, alignment: .topLeading)
.clipped()
.accessibilityHidden(!isOpen)
```

- The fold's owner animates with `.animation(_:value: isOpen)`; the removal transition keeps the
  content until the animation ends.
- Measured on 120 rows of folds: closed content built nothing (it had cost 1 body and 1 text measure
  per closed fold, 17.6 % of a 2.95 s hang); median scroll step 2.3–3.7 ms → 0.5–1.0 ms; runs with a
  step over 100 ms 5 of 12 → 0 of 12. Opening measured once with `.fixedSize`, 8 times without it.
- A row's menu, popover and trailing controls are built the same way, when revealed.
- Measured against the alternatives: a presence gate observed per animation tick ran its body
  9 118 times in one 400 ms open; `DisclosureGroup` drops its content at 0 ms on close, with no
  closing animation.

## Geometry

- Geometry reaches state as a small value that changes rarely: `onGeometryChange(for: Bool.self)`
  or `onScrollGeometryChange(for:)` transforming to the threshold a view needs, so the action runs
  only when that value flips. A per-frame `minY` written to `@State` redrew 13 text views on every
  scroll frame.
- A position another view needs travels as an anchor: rows write `anchorPreference(key:value:
  .bounds)`, and the reader resolves the anchors inside `overlayPreferenceValue` with a
  `GeometryReader`. Over 60 scroll steps: 0 parent body runs, against 60 for frames stored in
  `@State` through `onPreferenceChange`.
- A look driven by scroll position — opacity, scale, offset — is `scrollTransition` or
  `visualEffect`, which the renderer applies without running a body.
- Pixel alignment lives in the scroll container: SwiftUI already places hosted views on the pixel
  grid (0 of 18 off it), and only a fractional scroll offset moves them off (18 of 18 after a scroll
  to y = 10.3). Heights round up to a pixel at layout; a `ScrollTargetBehavior` rounds the target.
- With scroll bars set to show always (`NSScroller.preferredScrollerStyle == .legacy`), a horizontal
  scroll view whose content overflows gains the scroller's height once in a window: two wide blocks
  grew a row by 34 pt after it was placed. Its height is the content plus
  `NSScroller.scrollerWidth(for: .regular, scrollerStyle: .legacy)` while the style is legacy and
  the content overflows, re-measured on `NSScroller.preferredScrollerStyleDidChangeNotification`;
  the person's scroll-bar setting stands.

## Time words

- A time phrase ("2 min ago") is a `DiscreteFormatStyle` holding its date, drawn by
  `Text(.currentDate, format:)`; SwiftUI asks the style for its next change and formats once at
  each. Over 40 rows: a one-minute style used 0.0 % of the main thread and formatted each row once
  a minute; a list-wrapping `TimelineView(.periodic(by: 1))` ran 360 row bodies in 8.5 s; a
  one-second custom style used 14–15 %; `Text(_:style: .relative)` 21.6 %.
- A time read into an accessibility label → `TimelineView(.everyMinute)` around that one row.
- A per-second counter → a `TimelineView` around the number alone.

## Continuous motion

- Motion that loops while something is going on — a spinner, a shimmer, a pulsing mark, a progress
  sweep — is described once and played by the system's render server: Core Animation animations on
  the layer of a platform view the SwiftUI view hosts. The app's own code runs when the motion
  starts, stops or changes look, and never once per frame.
- The hosted view, on either platform:

  | Concern | AppKit | UIKit |
  | --- | --- | --- |
  | host | layer-backed `NSView` through `NSViewRepresentable` | `UIView` through `UIViewRepresentable` |
  | start, stop | add the `CAAnimation`s in `viewDidMoveToWindow` once `window` is set; remove them when it is `nil` | the same in `didMoveToWindow` |
  | display scale | rebuild in `viewDidChangeBackingProperties` | rebuild on a `displayScale` trait change |
  | Reduce Motion | a still pose, from `context.environment.accessibilityReduceMotion` | same |
  | accessibility | not an element; the SwiftUI wrapper carries the name | same |

- A parent's redraw reaches `update…View` with equal inputs and changes nothing there, so the motion
  never restarts; a change of tint or size updates the layers in place.
- Layers are drawn once and moved: a blur, a glow or a gradient is drawn into a cached image, and the
  animation moves its transform and opacity. An animated filter radius re-renders in the render
  server every frame.
- Measured on macOS 27 with 1 and 24 copies: 0.0 % of the main thread and 0 view evaluations, shown
  or hidden, and still moving while the main thread was blocked for 4 s. Each SwiftUI route cost
  main-thread time every frame: a `TimelineView(.animation)` mark 8.6–9.1 % for one and 21–55 % for
  24, still ticking at 51.6 % in a window ordered out; `keyframeAnimator` ran its content 2 922 times
  a second; `phaseAnimator` 7.2 %; `repeatForever` on built-in effects 3.9–28 %, frozen while the
  main thread was busy; an SF Symbol `.rotate` effect 2.7–5.7 %. The UIKit column follows the same
  mechanism and was not measured.
- A one-off transition — a view appearing, a fold opening — stays a SwiftUI animation: it runs for a
  fraction of a second and ends.

## Review

| Pattern | Check |
| --- | --- |
| a screen `body` reading many models, sections as computed properties | § A change re-runs one view |
| a closure parameter on a child or row, `Binding(get:set:)`, a closure in an `@Entry` | values plus the model reference; key-path bindings; § The environment holds what rarely changes |
| a list keyed on one global revision, a computed collection on a model | § Observation that tracks one row |
| `ForEach(x.indices…)`, `id: \.offset`, `id: \.self` on a struct, a top-level `switch` or `if` in a row, an `AnyView` row | § Lists |
| `.filter` or `.sorted` in a `ForEach` argument | stored where the inputs change |
| collapsed content hidden by `.opacity(0)`, `.frame(height: 0)` or `.hidden()` | § Collapsed content |
| `onGeometryChange` or `GeometryReader` writing `@State` per frame, frames through `onPreferenceChange` | § Geometry |
| a `TimelineView` around a list | § Time words |
| `TimelineView(.animation)`, `repeatForever`, `keyframeAnimator` on looping chrome | § Continuous motion |
| a formatter built in `body` or `init` | `Text(_:format:)` — § A change re-runs one view |
| a parse or `AttributedString(markdown:)` in `body` or `init` | `isolation.md` § Keeping the main actor free; `performance.md` § Costs in Foundation and the standard library |
| an in-place write on a hot `@Observable` path | `observation.md` |
