# Decision Rules

## The verdicts

- `cut` → the code already says it: a restatement of the next line, a signature paraphrase, commented-out code, a banner, an author, date or changelog line, a ticket id, a record number or a tracker link.
- `carry` → the comment names something the file can hold: a local rename (`amount` → `amount_cents`), a narrowed type, an extracted constant or function whose name states the rule.
- `hand back` → only a change past this file carries it — an exported rename, a new test named for the rule — or its why is not visible in the code.
- `stays` → a line a tool reads.
- An entry carrying a why takes `hand back`, whatever else it holds.

## Lines a tool reads

- The test: removing the line changes what a build, lint or run does.
- A shebang, an encoding line, a tools-version line.
- A linter or type-checker directive: `eslint-disable`, `@ts-expect-error`, `noqa`, `type: ignore`, `swiftlint:disable`, `#[allow]`.
- A `@deprecated` tag.
- Help text the program prints: a CLI's help taken from `__doc__`, a command docstring a framework reads as help (Click), a `///` block clap derive reads (`about`, `long_about`, a field's help).
- A doc-test a test runner executes: a rustdoc code block, a Python doctest.
- Input a code generator consumes in the build.
- A line inside recorded fixture data.
- A doc comment, JSDoc prose, `///` line, `// MARK:` or banner that no tool reads is a comment.

## Carrying a unit, an order or a workaround

- A unit → the name or a type: `timeout_ms`, a `Cents` newtype.
- An ordering constraint → a function whose name states it, or one call that does both steps.
- An external bug worked around → a function named for the workaround (`debounce_safari_double_resize`).
- None of these fits inside the file → `hand back`.
