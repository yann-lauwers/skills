# SwiftUI on macOS

Every API below was compiled one per file (SKILL.md step 3) at macOS 14, 15, 26 and
27 targets on the macOS SDK 27.0 (Xcode 27.0). The floor column is the lowest target where the
API compiled. Compile it at the project's own deployment target before relying on a row.

## Scenes and windows

| API | Floor |
| --- | --- |
| `WindowGroup(id:)`, `Window`, `Settings`, `MenuBarExtra` (+ `isInserted:`, `.menuBarExtraStyle(.window)`) | 14 |
| `openWindow`, `dismissWindow`, `openSettings`, `SettingsLink` | 14 |
| `.windowResizability`, `.windowStyle(.hiddenTitleBar)` | 14 |
| `UtilityWindow`, `.defaultLaunchBehavior`, `.restorationBehavior`, `.defaultWindowPlacement`, `.windowIdealPlacement` | 15 |
| `.windowStyle(.plain)`, `.windowLevel`, `WindowDragGesture`, `.windowMinimizeBehavior` (a View modifier, not a Scene one) | 15 |
| `.toolbar(removing: .title)`, `.toolbarBackgroundVisibility`, `.containerBackground(for: .window)` | 15 |
| `TabView { Tab(…) }` | 15 — `.tabItem` is soft-deprecated; only a floor of 14 writes it, behind `#available` |
| `.glassEffect`, SwiftUI `WebView` | 26 |
| `NSHostingSceneRepresentation` + `NSApplication.addSceneRepresentation(_:)` — SwiftUI `Settings` / `MenuBarExtra` scenes in an AppKit-lifecycle app; `scenes.environment.openSettings()` opens them | 26 |
| `NSGestureRecognizerRepresentable` — AppKit gestures inside SwiftUI | 26 (a conformance alone compiles at 14; only its use is gated) |
| `NSHostingMenu` — an `NSMenu` built from SwiftUI | 14.4 |
| `.pickerStyle(.tabs)` — VoiceOver reads it as tabs | 27 |

- `Window` is single-instance, `WindowGroup` multi-instance. In a menu-bar app, give every scene an
  id and open it explicitly with `openWindow(id:)`.
- A `Settings` scene gets the standard Settings menu item and shortcut for free.
- Hiding the toolbar or title bar leaves the window without a drag region unless one is provided.

## Views and state

| API | Floor |
| --- | --- |
| `@Entry` for environment keys, `@Animatable` | 14 |
| `onChange(of:) { old, new in }`, `onGeometryChange(for:)`, `withAnimation { } completion: { }` | 14 |
| `draggable`, `dropDestination(for:)` | 14 |
| `@Environment(\.appearsActive)` — styling for an inactive window | 14 |
| `scrollTransition`, `visualEffect`, `anchorPreference` + `overlayPreferenceValue`, `defaultScrollAnchor(_:)` | 14 |
| `Text(.currentDate, format:)` with a `DiscreteFormatStyle`; `ScrollPosition(idType:edge:)`, `defaultScrollAnchor(_:for:)`, `onScrollGeometryChange`, `onScrollPhaseChange`, `onScrollTargetVisibilityChange` | 15 |
| `ForEach(items.enumerated(), …)` | 26; use `Array(items.enumerated())` below it |
| `CopyButton` | does not exist in the SDK |

- `@State` is a macro since Xcode 27; `@State private var model = Model()` evaluates `Model()` once
  per view identity, and that behaviour back-deploys to macOS 14. Its source breaks: assigning in
  `init` when the declaration also carries an initial value — declare `@State private var model:
  Model` with no initial value and assign in `init`; a `private` `@State` drops out of the
  synthesised memberwise `init`, whose access follows the members left; weaker generic inference; and
  composing `@State` with another property wrapper or macro. `_count = State(initialValue:)` still
  compiles on this toolchain.
- `@Entry` defaults are values. Xcode 27 warns on a class instance or a closure as the default. A
  shared model is `@Entry var model: Model? = nil`, injected from the scene; a `static let` default
  over a `@MainActor` model fails Swift 6 with "main actor-isolated default value in a nonisolated
  context".

## macOS 27 behaviour changes

- Menu-item symbol images are hidden by default for apps linked on the 26 SDK or later; override
  with `NSMenuItem.preferredImageVisibility` (27) or `.labelStyle(.titleAndIcon)`.
- `.squareBorder`, `.roundedBorder` and `FileDocument` are soft-deprecated: `api-currency.md`
  § Replace.
- `Slider`, bordered `Menu` and `Picker` no longer wrap `NSSlider` / `NSPopUpButton` — code that
  reached for the AppKit view underneath finds none.
- `#Preview` bodies run on the main actor; `PreviewProvider` is deprecated by the Xcode 27 notes
  (no compiler warning); `#Preview(arguments:)` renders a grid.

iOS-only APIs to never write in a macOS target: `.topBarLeading`, `.keyboardType`,
`.navigationBarTitleDisplayMode`.

## Rules carried over from the iOS-first packs, kept because they hold on macOS

`Text` interpolation instead of `+` between `Text`s; `ImageRenderer` for rendering a view to an image;
`#Preview`; a label on every icon-only button. Adapted from twostraws' SwiftUI skill, filtered to macOS.
