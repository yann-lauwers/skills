# Sources of truth

Which source settles which question, and how to reach Apple's documentation.

## Which source answers what

- Does it exist, at which floor, does it compile → the compiler: `scripts/sil-check.sh`, one
  API per file (SKILL.md step 3).
- What an API promises, and the pattern Apple recommends → Apple's documentation — the SwiftUI
  update rules excepted, per the `swiftui-updates.md` line below.
- What changed this year → Apple's dated updates page for the framework, and the Xcode release notes.
- Language rules → the swift-evolution proposal, whose status line says which Swift shipped it.
- Idioms nobody at Apple writes down → the rows in this skill's references.
- The SwiftUI update rules an agent needs while writing any view → `swiftui-updates.md`, Apple's
  rules restated with this skill's measurements beside them.
- Apple's documentation and a row here disagree → a compiled probe settles it; neither wins on authority.
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
