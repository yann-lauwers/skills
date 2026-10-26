# SwiftUI and AppKit together

## Choose the smallest bridge

1. Pure SwiftUI when a scene, toolbar, command, inspector or standard control already does it.
2. `NSViewRepresentable` for one AppKit view with light lifecycle needs.
3. `NSViewControllerRepresentable` for controller lifecycle, delegation or presentation.
4. Direct AppKit — `NSWindow`, `NSPanel`, the responder chain, menus, app-level behaviour — when
   the capability is window- or app-shaped.

Name the gap before bridging. SwiftUI owns value state and models; AppKit objects stay inside the
representable, its coordinator, or one bridge object. Expose bindings and small callbacks back, not
the AppKit object. Adapted from OpenAI's build-macos-apps `appkit-interop` skill.

## `NSViewRepresentable`, all of it

The protocol is `@MainActor @preconcurrency` and has four members that matter:

| Member | Job |
| --- | --- |
| `makeNSView(context:)` | create the view once per identity |
| `updateNSView(_:context:)` | push SwiftUI state into it; runs often — make it idempotent |
| `static dismantleNSView(_:coordinator:)` | teardown: remove monitors, observers, callbacks, timers |
| `sizeThatFits(_:nsView:context:)` | report a size (macOS 13) |

A coordinator holds delegate and target-action glue, never a second architecture. SwiftUI may
recreate the representable; state that must survive lives in the model.

Reading the hosting window: an `NSView` subclass overriding `viewDidMoveToWindow()` and reporting
`window` back asynchronously, off the layout pass.

## Windows and panels

- `NSPanel` for floating chrome: override `canBecomeKey` / `canBecomeMain` to decide whether it takes
  keyboard focus, and use `.nonactivatingPanel` so a click does not activate the app.
- Override `sendEvent(_:)` to see mouse events before the view hierarchy; it is already main-actor.
- Keep long-lived windows owned by a controller object, not stored globally without a reason.

## Activation and the Dock

- `NSApp.activate()` (macOS 14) replaces `activate(ignoringOtherApps:)`, which the header marks
  to-be-deprecated.
- Switch the activation policy at runtime to match what is open: `.regular` while a window shows,
  `.accessory` when the last one closes (no Dock tile, no menu bar), remembering the prior policy.
  A menu-bar-only app starts `.accessory` (`LSUIElement`).
- AppKit calls from nonisolated code are warnings, not errors (AppKit is imported main-actor via
  `NS_SWIFT_UI_ACTOR`); do not rely on the compiler to keep them on main.

## Menu bar

`NSStatusItem` when the menu is built or rebuilt imperatively — rebuild on a change in what it
shows, not on every model publish. `MenuBarExtra` (macOS 13) when the content is plain SwiftUI.

## Responder chain and menus

Commands reach the first responder; validate menu items with `validateMenuItem(_:)` /
`NSMenuItemValidation`. In SwiftUI, `.commands { }` and `FocusedValue` route menu actions to the
focused scene.
