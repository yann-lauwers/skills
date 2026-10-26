# Accessibility — VoiceOver, keyboard reach, and proving both

Checked on Xcode 27.0 / Swift 6.4 / macOS SDK 27.0: every API row read from Apple's documentation
and compiled alone with `scripts/sil-check.sh --target 14.0 -swift-version 6` (SKILL.md step 3).
**Measured** rows come from a probe built at a macOS 14
target and read from outside its process on a macOS 26.6 host; on a macOS 14 host they are
unverified. Rows marked **measured**, macOS 27 come from in-process probes on macOS 27.0, built at
the SDK's own target; below 27 they are unverified. SwiftUI rows hold on iOS at the matching floor
(iOS 17 where macOS says 14); AppKit rows are macOS only.

## The model

- A standard control is an element already; a plain `NSView` is not, and a view drawing its
  controls in `draw(_:)` is absent from the tree (**measured**).
- A reader walks children in the order the parent lists them — declaration order in a stack
  (**measured**); `accessibilitySortPriority` sorts higher first, default 0; a `.contain` container
  reads all its children before the next one.
- A label names the thing ("Play"), never its role ("Play button"); neither a role description nor
  `accessibilityIdentifier`, which exists for tests, is a label.

## SwiftUI

| Need | API | At 14 |
| --- | --- | --- |
| name, state, outcome | `accessibilityLabel`, `accessibilityValue` (only when it differs from the label), `accessibilityHint` ("Downloads the attachment") | ✓ |
| behaviour | `accessibilityAddTraits(.isButton / .isHeader / .isToggle …)`, `accessibilityRemoveTraits`, `accessibilityHeading` | ✓ |
| merge, nest, or replace children | `accessibilityElement(children: .combine / .contain / .ignore)` | ✓ |
| a custom control as a standard one | `accessibilityRepresentation { Slider(…) }` — the closure is hidden and inert | ✓ (12) |
| children for drawn content | `accessibilityChildren { … }` | ✓ (12) |
| actions | `accessibilityAction(named:)`, `accessibilityAction { }`, `accessibilityAdjustableAction`, `accessibilityActions { }` | ✓ — `accessibilityActions(category:)` is macOS 15 |
| move VoiceOver's cursor, not keyboard focus | `@AccessibilityFocusState` + `accessibilityFocused` | ✓ (12) |
| jump lists (the VoiceOver rotor) | `accessibilityRotor(_:entries:)` | ✓ |
| decoration, label beside its control | `accessibilityHidden(true)`, `accessibilityLabeledPair(role:id:in:)` | ✓ |
| announce a change | `AccessibilityNotification.Announcement("Saved").post()`; `.LayoutChanged`, `.ScreenChanged`, `.PageScrolled` | ✓ (14) |
| a segmented control read as tabs | `.pickerStyle(.tabs)` (SwiftUI); `NSSegmentedControl.role = .tabs`, `NSToolbarItemGroup.role` (AppKit) | ✗ — macOS 27 |

- `AccessibilityNotification` — the Accessibility framework's, visible through `import SwiftUI`
  alone; posted from an AppKit app, it reaches an outside observer as `AXAnnouncementRequested`
  (**measured**).
- An announcement's priority rides on its `AttributedString`:
  `s.accessibilitySpeechAnnouncementPriority = .high`.

**Measured** — what each form publishes:

| Written | Tree |
| --- | --- |
| `Text("x").onTapGesture { }` | `AXStaticText`, no `AXPress`, not focusable — a reader can neither press nor reach it |
| the same + `.accessibilityAddTraits(.isButton).accessibilityAction { }` | `AXButton` with `AXPress` |
| `HStack { Image(…); Text("Favorites"); Text("12") }.accessibilityElement(children: .combine)` | one `AXStaticText`, value "Favorites, 12" |
| `.accessibilityElement(children: .ignore)`, no label | `AXUnknown`, nameless |
| `.accessibilityElement(children: .contain).accessibilityLabel("Stats")` | `AXGroup` "Stats" holding the children |
| `Capsule().accessibilityRepresentation { Toggle("Wi-Fi", isOn: $on) }` | `AXCheckBox`/`AXToggle` "Wi-Fi", value 1, `AXPress` |
| `Button { } label: { Image(systemName: "trash") }` | `AXButton` "Trash" — named from the symbol; check it says the action |

## AppKit

- Customise a standard control through its setters (`setAccessibilityLabel(_:)`) or by overriding a
  getter; a getter alone is read-only to the reader, an overridden setter makes it writable.
- A custom `NSView` control returns true from `isAccessibilityElement()` and adopts a role protocol,
  implementing every method it declares — `NSAccessibilityButton`: `accessibilityLabel()` and
  `accessibilityPerformPress()`; a view reporting `.button` without `accessibilityPerformPress()`
  publishes no `AXPress` (**measured**).
- Swift 6 → write the conformance `@MainActor NSAccessibilityButton`; plain is an error, and a
  warning in Swift 5 at `complete`.
- Parts drawn inside one view → one `NSAccessibilityElement` each: `element(withRole:frame:label:parent:)`,
  `setAccessibilityFrameInParentSpace(_:)` so it moves with the view, then the parent's
  `accessibilityChildren` or `accessibilityAddChildElement(_:)`; two such elements read as
  `AXButton`s at their frames, and `AXPress` reached them (**measured**).
- An `NSAccessibilityElement` subclass adopting a role protocol overrides
  `accessibilityIdentifier() -> String`, or it fails to compile in both language modes.
- Post a change through `NSAccessibility.post(element:notification:)`, never `NotificationCenter`;
  standard controls post their own, a custom one posts `.valueChanged`, `.layoutChanged` with
  `[.uiElements: [...]]`, `.titleChanged`, `.focusedUIElementChanged`, `.selectedChildrenChanged`,
  `.uiElementDestroyed`.
- Announcement → `.announcementRequested` through `post(element:notification:userInfo:)`, with
  `[.announcement: text, .priority: NSAccessibilityPriorityLevel.high.rawValue]`.
- Every accessor and action a reader invokes runs on main (**measured**).
- Post from main: `NSAccessibility.post` and `NSAccessibilityElement` carry no main-actor
  annotation, so a nonisolated post compiles in Swift 6, but the element it names is an `NSView`,
  which AppKit allows on the main thread only; an off-main post was delivered once, and that it is
  safe is unverified.

## Keyboard

- `NSApp.isFullKeyboardAccessEnabled` is the value-2 bit of the global default
  `AppleKeyboardUIMode`, which the Keyboard pane's navigation setting writes; key-value observing
  never fires for it → read it at the point of use.
- AppKit caches it per process from the global domain alone — any application, current user, any
  host — through HIToolbox's `_IsFullTabbingEnabled`, until HIToolbox's own change listener clears
  the cache; a launch argument, `register(defaults:)` and the app's own domain never reach it
  (**measured**, macOS 27).
- AppKit's and SwiftUI's Tab decisions ask the window's private `_allowsAnyValidResponder`, never the
  `NSApplication` getter, so swizzling the getter moves no focus (**measured**, macOS 27).
- One process with it on, the person's setting untouched → a library interposing
  `CFPreferencesCopyValue` for `AppleKeyboardUIMode` in the any-application domain, loaded through
  `DYLD_INSERT_LIBRARIES` (`open --env` for an app), unsetting that variable once loaded so child
  processes don't inherit it; read `NSApp.isFullKeyboardAccessEnabled` inside the process before
  relying on it — false → the library never loaded, or this host reads it another way
  (**measured**, macOS 27, on ad-hoc builds
  carrying `get-task-allow` and `disable-library-validation`, with and without the hardened
  runtime).
- A view is a Tab stop when it is in a window, not hidden, and `acceptsFirstResponder`, and either
  keyboard navigation is on or its own `needsPanelToBecomeKey` is true (**measured**, macOS 27).
- A control answers `needsPanelToBecomeKey` from `cell.isSelectable`: with keyboard navigation off,
  `NSTextField` is a Tab stop and `NSButton` is not (**measured**).
- A plain `NSView` answers `needsPanelToBecomeKey` from `acceptsFirstResponder`, so a custom view
  accepting first responder stays a Tab stop with keyboard navigation off (**measured**, macOS 27).
- Proving "every control reachable" → with keyboard navigation on, through that library, on every
  host: macOS 27 fixes a loop that traversed the wrong fields and controls with it off, and hosts
  below 27 keep the old loop.
- The assistive technology named Full Keyboard Access drives elements through the tree, like Switch
  Control; whether turning it on writes `AppleKeyboardUIMode` is unverified.
- A Tab `CGEvent` with Shift (key code 48, `.maskShift`) becomes an `NSEvent` whose `characters` and
  `charactersIgnoringModifiers` are both `NSBackTabCharacter` (U+0019); a synthetic
  `NSEvent.keyEvent` with `"\t"` and `.shift` moves focus forward → build it with `"\u{19}"`
  (**measured**, macOS 27).
- A view that calls `interpretKeyEvents` receives `insertTab:` and `insertBacktab:`; implementing
  neither keeps focus on Tab and Shift-Tab (**measured**, macOS 27).
- The window orders the loop geometrically (`recalculateKeyViewLoop()`,
  `autorecalculatesKeyViewLoop`); a hand-built loop sets `nextKeyView` and `initialFirstResponder`.
- A custom focusable view draws its ring by overriding `drawFocusRingMask()` and
  `focusRingMaskBounds`, which defaults to `NSZeroRect`.
- SwiftUI built with the macOS 14 SDK or later makes custom `focusable()` views focusable always;
  `.focusable(interactions: .edit)` for a view that edits, `.activate` for one that acts — an
  `.activate` view takes no focus on click and, like `Button`, is a Tab stop only with keyboard
  navigation on; `.edit` and plain `focusable()` views are Tab stops either way (**measured**,
  macOS 27).
- The SwiftUI focus system on macOS, every row compiled at 14 (SKILL.md step 3):

  | Need | API |
  | --- | --- |
  | programmatic focus | `@FocusState var f: Field?` + `.focused($f, equals: .name)`; `.defaultFocus($f, .name)` for the window's first focus |
  | group Tab stops | `.focusSection()` — Tab visits every focusable descendant before moving on; with none it does nothing; that arrow keys reach it only when its frame is larger than its contents is unverified |
  | keys | `.onKeyPress(.return) { .handled }`, `.onKeyPress(characters:phases:)`; return `.ignored` to keep dispatching up the chain |
  | arrow keys | `.onMoveCommand { direction in }`, honouring `layoutDirection` |
  | the ring | `.contentShape(.focusEffect, …)` sets its outline; `.focusEffectDisabled()` removes it |
  | menu commands to the key window's content | `.focusedSceneValue(\.doc, value)` + `@FocusedValue(\.doc)` in the command; an `@Entry` in `FocusedValues` |
- A view handles keyboard input only once its window is key; a window whose style mask lacks
  `.titled` returns false from `canBecomeKey` unless overridden (`appkit-hybrid.md` § Windows and
  panels).
- A `.nonactivatingPanel` with `becomesKeyOnlyIfNeeded` turns key only when the clicked view's
  `needsPanelToBecomeKey` is true; whether such a panel, once key, takes keystrokes from the
  frontmost app is unverified — measuring it would take the owner's.

## Hybrid seams — measured

| Seam | Shows up as | Fix |
| --- | --- | --- |
| `NSViewRepresentable` around a drawn `NSView` | absent; `.accessibilityLabel` and `.accessibilityIdentifier` on it vanish too | `.accessibilityElement(children: .combine)` or `.ignore`, plus a label and a trait — no trait read `AXUnknown`; `.isImage` read `AXImage`; `.isButton` + `.accessibilityAction` a pressable `AXButton`. Or make the `NSView` an element |
| representable around an AppKit element | passes through (`NSButton` → `AXButton`); a SwiftUI `.accessibilityLabel` replaced the view's own | none needed |
| AppKit container that is an element, hosting SwiftUI text | `AXButton` "Open settings" → `AXHostingView` group → `AXStaticText` "Open settings": the name twice | container returns `[]` from `accessibilityChildren()` and implements its press — one pressable `AXButton` — or stops being an element |
| `NSHostingView` | an unnamed `AXGroup`, subrole `AXHostingView` | where it is a region, wrap its root in `.accessibilityElement(children: .contain).accessibilityLabel(…)` |

## Proving it

- Accessibility Inspector (Xcode › Open Developer Tool) → the element under the pointer, and an
  Audits pane checking, on macOS, element description, hit region, contrast, element detection,
  parent/child and action.
- UI test → `try app.performAccessibilityAudit(for: [.sufficientElementDescription, .action,
  .parentChild]) { issue in … }` (macOS 14; return true to handle an issue yourself); `.dynamicType`,
  `.textClipped` and `.trait` do not exist in a macOS target.
- `launch()` terminates a running instance of the target app.
- Spoken output → `XCUIVoiceOverService` (Xcode 27, macOS 27), which drives VoiceOver from the test
  and asserts on what it focused and spoke; what a reader is *offered* is still read outside the
  process.
- Outside the process → `AXUIElementCreateApplication(pid)` + `AXUIElementCopyAttributeValue`; a
  tree dump, `AXPress` on AppKit and SwiftUI elements, a focus read and an `AXObserver` on
  announcements all ran with the app neither active nor key (**measured**).
- Launching the app, the reader's grant, a tree of one element, a blind reader, a locked screen →
  /native-app-verification .

## Review list

| Look for | Why |
| --- | --- |
| `.onTapGesture` on `Text` / `Image` | not a control — `Button`, or a trait plus `accessibilityAction` |
| `.accessibilityElement(children: .ignore)` | nameless `AXUnknown` unless labelled; try `.combine` first |
| a modifier on a representable wrapping a drawn view | dropped — make it an element first |
| a role with no action, or clickable drawing with no element | inert or invisible to every reader |
| `NotificationCenter` for an accessibility change | reaches no reader |
| `accessibilityActions(category:)`, anything newer | macOS 15 — gate it |
| `focusable()` on a view with no action | a Tab stop that does nothing |
| a keyboard claim checked with keyboard navigation off | buttons were never in the loop (§ Keyboard) |
