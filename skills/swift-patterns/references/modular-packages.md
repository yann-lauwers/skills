# Modular SwiftPM packages under an app target

Checked on Xcode 27.0 / Swift 6.4: `swift package init --type library` output and `swift build -v`
flags, SE-0386, SE-0435, SE-0491, SE-0540, WWDC25 225 and 268, Xcode 27 release notes. The
app-target → package `package`-access boundary and String Catalog symbol generation inside a
package target were not built here.

## Layout

A thin app target over local packages: the app module holds the lifecycle and the windows; each
layer — domain, ports, adapters, UI — is a package target with its own settings. Resources a
package's code needs (a `.metal` library, a String Catalog) live in that package. Previews live in
the package that owns the view (what Xcode 27 changed about `#Preview`: `swiftui-macos.md` § macOS
27 behaviour changes).

## Settings per target

- **Default isolation.** Which targets take `.defaultIsolation(MainActor.self)` and why is
  `toolchain-and-modes.md` § Default isolation per module.
- **Language mode.** Read `swiftLanguageModes` and every per-target `.swiftLanguageMode(_:)`
  beside the tools version — `toolchain-and-modes.md` § The settings that change the answers.
- **Shared settings.** SE-0540 default target settings is accepted and not in Swift 6.4, so a
  manifest-level `let settings: [SwiftSetting]` array is repeated on each target by hand.
- **Warning groups.** `.treatWarning("ActorIsolatedCall", as: .error)` per target closes the
  warning-only hazards — `sendable-and-escape-hatches.md` § Warnings that should be errors.

## Visibility across modules

- `package` access (SE-0386) exposes a symbol to sibling targets of the same package and no
  further. SwiftPM passes `-package-name` itself (`swift build -v` shows it). That is the tool for a
  port protocol shared between adapter targets without going `public`. An Xcode app target that
  imports the package is a different package, so `package` symbols are not visible there; Xcode's
  `SWIFT_PACKAGE_NAME` setting exists and its use across that boundary is unverified.
- Module selectors `Module::Name` (SE-0491, Swift 6.4) disambiguate same-named types across adapter
  modules without a typealias.
- `MemberImportVisibility` (on in the Xcode template) and `InternalImportsByDefault` (a Swift 7
  feature, opt-in now) keep an adapter's imports from leaking through a module's public API — the
  compiler-enforced half of a layered architecture; nothing in the toolchain enforces the layering
  itself.

## Localization in a package

- New Xcode 26/27 projects set `LOCALIZATION_PREFERS_STRING_CATALOGS`,
  `STRING_CATALOG_GENERATE_SYMBOLS` and `SWIFT_EMIT_LOC_STRINGS`.
- Inside a package or framework, pass `bundle: #bundle` (and `tableName:` where the catalog is not
  `Localizable`) to `Text` and `String(localized:)`; `#bundle` compiles at macOS 14.
- Generated symbols are `LocalizedStringResource` statics (`Text(.introductionTitle)`), so a
  reusable view takes `LocalizedStringResource` parameters, not `String`.
- Xcode 27 marks a string commented "do not translate", and previews render in another locale
  through the preview's override.

## Module names

The Xcode 27 dependency scanner requires unique Clang module names across the whole build: a
vendored `module.modulemap` that redeclares a name another dependency already uses is an error, not
a shadowing.
