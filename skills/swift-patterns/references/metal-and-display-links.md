# Metal hosting and display links

Checked on Xcode 27.0 / macOS SDK 27.0 — the actor annotations were read from `MTKView.h`,
`CAMetalDisplayLink.h` and `NSView.h`; the conformers compiled one per file (SKILL.md step 3). The trap
on a `CAMetalDisplayLink` delegate is inferred from SE-0423 and was not run.

## `MTKView`

- `MTKView` is `@MainActor`, and `MTKViewDelegate`'s `draw(in:)` and
  `mtkView(_:drawableSizeWillChange:)` are `NS_SWIFT_UI_ACTOR`, so the delegate is main-actor: a
  `@MainActor final class Renderer: NSObject, MTKViewDelegate` is the plain form, and its encoder
  work runs on main.
- Three drawing modes: timed (the default, `preferredFramesPerSecond`); draw-on-change —
  `isPaused = true` + `enableSetNeedsDisplay = true`, then `setNeedsDisplay()` when the content
  changed, right for a view that redraws on input rather than on a clock; and explicit `draw()`.
- Subclass `MTKView` or provide a delegate, never both.
- Xcode 27 exposes Metal validation options in the scheme's Diagnostics pane; turn them on for the
  run that reproduces a render bug.

## `CAMetalDisplayLink` and the render thread

- `CAMetalDisplayLink` (macOS 14) paces frames for a `CAMetalLayer` with `preferredFrameRateRange`
  and `preferredFrameLatency`, and is added to a run loop the caller chooses. Its delegate protocol
  carries **no** actor annotation, so a `@MainActor` conformer scheduled on a render-thread run
  loop is called off main — the SE-0423 trap in Swift 6 mode (`toolchain-and-modes.md` § Swift 5
  mode vs Swift 6 mode). Declare the delegate `nonisolated`, do the encoding there, and hop to the
  main actor only for state the UI owns.
- `NSView.displayLink(target:selector:)` (macOS 14) is the view-bound alternative: it follows the
  view's window and display, and its callback arrives on main.

## Review

| Pattern | Check |
| --- | --- |
| a `@MainActor` type conforming to `CAMetalDisplayLinkDelegate` | which run loop the link was added to — off main it traps |
| `MTKView` with a delegate and a `draw(_:)` override | one or the other |
| a timed `MTKView` in a view that only redraws on input | `isPaused` + `enableSetNeedsDisplay` |
| render-thread work reading `@Observable` state | copy the frame's inputs into a `Sendable` value on main first |
