# Formatting and linting: swift-format with SwiftLint

Checked on the swift-format Xcode 27.0 bundles (`swift format --version` prints `main`),
swiftlang/swift-format@b15dd59, and SwiftLint 0.65.1. This file is about Apple's swift-format
(`swift format`, `.swift-format`), not Nick Lockwood's SwiftFormat (`.swiftformat`).

## Who owns what

- swift-format owns layout: indentation, spaces, line breaks, brace position, blank lines, trailing
  commas, import order, and the length of any line it could break. Its `lint` compares each line
  with what `format` would write, so every layout difference is already a finding.
- SwiftLint owns what the formatter cannot see: correctness (`force_cast`, `force_try`, unused
  bindings), idiom, size metrics, naming beyond case, and custom bans.
- One concern, one owner. A SwiftLint layout rule running beside the formatter can only repeat it
  or contradict it.
- Line length is split. swift-format flags a long line only when its own output would fit
  (`WhitespaceLinter.swift:244-247`); a lone long string literal passes. Keep SwiftLint's
  `line_length` at the formatter's number for that remainder, with `excluded_lines_patterns` for
  lines the codebase keeps whole on purpose (a user-facing sentence), or turn it off.

## Running them

- Order: `swift format --in-place`, `swiftlint --fix`, then the two checks,
  `swift format lint --strict --parallel` and `swiftlint lint --strict`. Without `--strict`,
  `swift format lint` exits 0 on findings.
- Both checks read one file set, the tracked Swift files:
  `git ls-files -z '*.swift' | xargs -0 <tool> …`. `--recursive .` walks git-ignored folders.
- `swiftlint --fix --format` is a second formatter; never pair it with swift-format. `--strict`
  does nothing with `--fix`.
- Under `--strict` every warning is an error: give each threshold one number.
- `swift format` runs the selected toolchain's binary, whatever `PATH` holds. Pin the formatter by
  pinning Xcode, or call one pinned `swift-format` by its own name in every task and in CI.

## The two config files

- `.swift-format`'s `rules` map is the whole rule set: a rule it leaves out is off
  (`Configuration.swift:470-476`, `Context.swift:118`). Generate it from the pinned binary,
  `swift format dump-configuration > .swift-format`, then edit; check with
  `swift format dump-configuration --effective`.
- Read a SwiftLint option off the pinned binary, `swiftlint rules <name>`: an invalid key warns
  and lints anyway. `swiftlint rules --enabled` lists what runs.

## Aligning them

1. List both live rule sets with the two commands above.
2. Turn off every SwiftLint layout rule: `attribute_name_spacing`, `closing_brace`,
   `closure_parameter_position`, `colon`, `comma`, `function_name_whitespace`, `indentation_width`,
   `leading_whitespace`, `no_space_in_method_call`, `opening_brace`, `return_arrow_whitespace`,
   `statement_position`, `switch_case_alignment`, `trailing_comma`, `trailing_newline`,
   `trailing_whitespace`, `vertical_parameter_alignment`, `vertical_whitespace`.
3. Where both tools name a rule for one concern, keep one: the formatter's when it rewrites
   (`swift format` fixes it), otherwise the one whose options the repo needs.

   | Concern | swift-format | SwiftLint | Owner |
   | --- | --- | --- | --- |
   | import order | `OrderedImports` | `sorted_imports` | formatter; the two disagree on case and on `@testable` |
   | semicolons | `DoNotUseSemicolons` | `trailing_semicolon` | formatter; SwiftLint sees only a trailing one |
   | parentheses round a condition | `NoParensAroundConditions` | `control_statement` | formatter |
   | `Array<T>` | `UseShorthandTypeNames` | `syntactic_sugar` | formatter |
   | `-> ()`, `-> Void` | `NoVoidReturnOnFunctionSignature`, `ReturnVoidInsteadOfEmptyTuple` | `redundant_void_return`, `void_return` | formatter |
   | a case with only `fallthrough` | `NoCasesWithOnlyFallthrough` | `no_fallthrough_only` | formatter |
   | `()` before a trailing closure | `NoEmptyTrailingClosureParentheses` | `empty_parentheses_with_trailing_closure` | formatter |
   | file-scope `private` | `FileScopedDeclarationPrivacy` | `private_over_fileprivate` | formatter |
   | a hand-written memberwise init | `UseSynthesizedInitializer` | `unneeded_synthesized_initializer` | formatter |
   | force unwrap | `NeverForceUnwrap` (skips files importing a test library) | `force_unwrapping` | formatter |
   | force try | `NeverUseForceTry` | `force_try` | SwiftLint; with both on, an exception needs two suppressions |
   | `T!` | `NeverUseImplicitlyUnwrappedOptionals` | `implicitly_unwrapped_optional` | formatter |
   | identifier case | `AlwaysUseLowerCamelCase` | `identifier_name` | SwiftLint (it also checks length and has exclusions) |
   | type name case | `TypeNamesShouldBeCapitalized` | `type_name` | SwiftLint |

4. Prove the pair over the whole tree: format in place changes nothing, `swiftlint --fix` changes
   nothing, and both checks exit 0. Then format a probe of awkward shapes (wrapped signatures,
   conditions, type headers, trailing closures with parameters, long literals) and lint it: a lint
   finding on formatter output is a conflict still in the config.
5. A conflict found later → change SwiftLint's config to accept what the formatter writes. The
   formatter's output is the definition of layout.

## Suppressions

- A finding is fixed in the code. An inline `// swiftlint:disable` is a config decision made at one
  call site, and the next agent copies it.
- The same suppression for the same shape more than twice → the config is wrong for that shape:
  bend the rule to it (`excluded_lines_patterns`, a rule's own `ignore_*` option) or turn the rule
  off, then delete what `superfluous_disable_command` reports.

## Changing a rule

- A config change and the code it makes compliant land in one commit: the check goes red on the
  old code, `swift format` and `swiftlint --fix` rewrite what they can, the rest is fixed by hand,
  the check goes green. The tree is what agents copy; a rule the tree breaks is followed by nobody.

## Starter pair

`.swift-format`, from the pinned binary; the values are a repo's call:

```sh
swift format dump-configuration | jq '.lineLength = 100 | .indentation = {spaces: 4} | .tabWidth = 4
  | .rules.NeverForceUnwrap = true | .rules.NeverUseImplicitlyUnwrappedOptionals = true' > .swift-format
```

`.swiftlint.yml`:

```yaml
disabled_rules:
  # layout: the formatter owns it
  - attribute_name_spacing
  - closing_brace
  - closure_parameter_position
  - colon
  - comma
  - function_name_whitespace
  - leading_whitespace
  - no_space_in_method_call
  - opening_brace
  - return_arrow_whitespace
  - statement_position
  - switch_case_alignment
  - trailing_comma
  - trailing_newline
  - trailing_whitespace
  - vertical_parameter_alignment
  - vertical_whitespace
  # a swift-format rule owns the concern
  - control_statement
  - empty_parentheses_with_trailing_closure
  - no_fallthrough_only
  - private_over_fileprivate
  - redundant_void_return
  - syntactic_sugar
  - trailing_semicolon
  - unneeded_synthesized_initializer
  - void_return
opt_in_rules:
  - contains_over_filter_count
  - empty_count
  - first_where
  - redundant_nil_coalescing
  - toggle_bool
line_length:
  warning: 100
  error: 100
  excluded_lines_patterns:
    - '^\s*"([^"\\]|\\.)*"[,)]*$'
```

Formatter rules this pair leaves on and SwiftLint has no counterpart for: `AlwaysUseLowerCamelCase`
and `TypeNamesShouldBeCapitalized` → off in `.swift-format`, per the table. Measured on a
3,482-file app: after the rewrite, no layout rule fired.
