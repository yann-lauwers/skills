# Verdicts

One verdict per comment. Test them in this order; the first that fits wins.

| Verdict | The comment | Becomes |
| --- | --- | --- |
| `tool line` | changes what a build, lint or run does when removed | stays |
| `excuse` | lets a shortcut stand: a skipped check, a disabled rule, a `TODO`, a workaround nobody tracks, "for now" | an issue, then deleted |
| `stale` | describes code, a value or a file that is no longer so | deleted |
| `recorded` | states a decision a record or doc already holds | deleted; the record is named |
| `decision` | holds a non-obvious why that nothing else holds | a decision record, then deleted |
| `tautology` | says what the next line, the name, the type or the file's place already says | deleted |

## Telling them apart

- A why → never `tautology`. Search the records and docs for it: found → `recorded`; absent → `decision`.
- A disable directive is both a `tool line` and a candidate `excuse`: it is an `excuse` when the repo's rules give that rule no line exemption, or when its reason describes a fault in the rule or the code.
- A workaround with its cause stated and deliberate is a `decision`; one waiting on a fix is an `excuse`.
- A number or a count in prose (`nine steps`, `48 apps`) → check it against the code before calling it anything but `stale`.
- A unit, an order or a workaround a rename inside the file can hold (`timeout` → `timeout_ms`, a function named for the rule) → rename, then the comment is a `tautology`.
- A banner, an author, a date, a changelog line, commented-out code, a ticket id → `tautology`.

## Tool lines

- A shebang, an encoding line, a tools-version line.
- A linter, formatter or type-checker directive: `eslint-disable`, `@ts-expect-error`, `noqa`, `type: ignore`, `swiftlint:disable`, `#[allow]`.
- A test runner's or bundler's pragma: `@vitest-environment`, `@jest-environment`, `/// <reference>`, `@vite-ignore`.
- A `@deprecated` tag.
- Help text the program prints: a docstring handed to an argument parser, a `///` block clap derive reads.
- A doc-test a runner executes.
- A marker a generator or an outside tool consumes; name the tool, and say so when no reader was found in the repo.
- A line inside recorded fixture data.
- A doc comment, JSDoc prose, `// MARK:` or a licence header no tool reads is a comment.
- Help text that runs long is still a tool line; report its line count apart, since the sweep leaves it.
