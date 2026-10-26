# Sources of truth

Which source settles which question, and how to reach Apple's.

## Which source answers what

- Does it exist, at which floor, does it compile → the compiler: `scripts/sil-check.sh`, one
  API per file (SKILL.md step 3).
- What an API promises, and the pattern Apple recommends → Apple's skill for the subject (the routing
  table in `SKILL.md` names each), then Apple's documentation — the SwiftUI update rules excepted,
  per the `swiftui-updates.md` line below.
- What changed this year → Apple's dated updates page for the framework, and the Xcode release notes.
- Language rules → the swift-evolution proposal, whose status line says which Swift shipped it.
- Idioms nobody at Apple writes down → the rows in this skill's references.
- The SwiftUI update rules an agent needs while writing any view → `swiftui-updates.md`, Apple's
  rules restated with this skill's measurements beside them; Apple's skill keeps the worked
  examples, and a disagreement between the two is settled by the probe rule below.
- Apple's skill and a row here disagree → a compiled probe settles it; neither wins on authority.
  The losing text is corrected in this skill.

## Apple's documentation, as Markdown

- `sh ${CLAUDE_SKILL_DIR}/scripts/apple-doc.sh <page> [out-dir]` saves one page and prints its path.
  `<page>` is a path under `documentation/` (`swiftui/menubarextra`), a `developer.apple.com` URL,
  or a link copied out of another page (`/documentation/...` or `doc://com.apple.documentation/...`).
- Read the saved file whole. A summarising fetch rewrites the wording the fetch was for.
- Exit 1 means nothing answers at that path. A symbol's path carries a hash suffix when overloaded
  (`View/body-8kl5o`), so it is not guessable: fetch the parent type's page and follow its link.
- The JSON comment opening each page lists `availability`; the compiler outranks it.
- Entry points: `swiftui`, `appkit`, `swift`, `observation`, `testing`, `xcode/swift-packages`,
  `updates/<framework>` (SwiftUI, AppKit, Swift and a few others — `updates` lists them),
  `xcode-release-notes/xcode-<major>-release-notes`.
- Xcode also carries older Apple-written guides at
  `/Applications/Xcode.app/Contents/PlugIns/IDEIntelligenceChat.framework/Versions/A/Resources/AdditionalDocumentation/`
  — Liquid Glass for AppKit and SwiftUI, concurrency updates, `InlineArray` and `Span`. Their Swift
  version is older than the toolchain; check a claim from them against the compiler.

## Apple's agent skills

- Xcode ships skills written by Apple for coding agents, versioned with the Xcode build.
  `sh ${CLAUDE_SKILL_DIR}/scripts/sync-apple-skills.sh` installs the ones that serve a macOS app and
  run without Xcode as the plugin `xcode-integration@skills-dir`; they answer to
  `/xcode-integration:<name>`. The script names the ones it keeps and why the rest are left out.
- A fix to one of them goes in this skill.
- A sync printing a `changed xcode-integration:swiftui-specialist/references/…` line → each
  `swiftui-updates.md` rule on that file's subject is re-read against it, and a disagreement is
  probed before the next SwiftUI change.
- The accessibility audits open on `XcodeRead`, a tool that exists only inside Xcode's assistant;
  Read does the same job.
- The `xcode` MCP server the pack ships (`xcrun mcpbridge`) is not installed: it needs a running
  Xcode that has allowed external agents.
- They are written iOS-first. Their SwiftUI practice holds on macOS; their floors and isolation
  advice do not always.

## Where Apple's skills are wrong on macOS with Swift 6

Each was compiled on Xcode 27.0 / Swift 6.4. Follow this skill's row instead.

- `@Entry` floor → `swiftui-macos.md` § Views and state (macOS 14, not 15).
- `ForEach(items.enumerated())` floor → `swiftui-macos.md` § Views and state (macOS 26).
- Apple's skill leaves `@MainActor` off a model a view awaits from `.task`; keep it (`observation.md`).
- Apple's `static let` default for a shared `@Entry` model fails Swift 6 → `swiftui-macos.md` § Views
  and state.
- An AppKit view with the button role also implements `accessibilityPerformPress()`; without it
  VoiceOver finds no press action (`accessibility.md`).
- The soft-deprecated list misses `.roundedBorder`, `.squareBorder` and `FileDocument`, and the
  one-parameter `onChange` is a hard deprecation that warns (`api-currency.md` § Replace).
- Apple's `Equatable` setter skip holds only for a whole-value assignment; an in-place mutation
  notifies whatever the value (`observation.md`).
- The accessibility skills' own examples use `.foregroundColor` and `.cornerRadius`, which their
  sibling lists as soft-deprecated.
