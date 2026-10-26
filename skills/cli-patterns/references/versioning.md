# Version numbers

- What a caller of the previous build can still rely on decides which part of a command-line tool's version moves.
- Public API — what clig.dev's future-proofing section names, "Subcommands, arguments, flags, configuration files, environment variables: these are all interfaces", plus the two surfaces a script parses, exit codes and `--json` keys (`references/output-and-exit.md`), and the files the tool leaves on disk for its next run to read; Semantic Versioning supplies the three parts and requires that "Software using Semantic Versioning MUST declare a public API" (https://semver.org/).

## The rule

| Part | Moves when the release |
| --- | --- |
| MAJOR | removes or renames a command, flag or env var; changes what an exit code means; removes or renames a `--json` key or changes its type; or writes a stored format — a state file, a config, a cache — that an older build cannot read |
| MINOR | adds a command, flag, env var or `--json` key |
| PATCH | changes anything else — a fix, reworded human output, speed, docs |

- The highest row any change in the release reaches decides it: adding one flag and renaming another is MAJOR.
- Human-readable output is not the API; the stable surface is `--json`.
- A stored format counts from the reader's side: adding a field an older reader ignores breaks nothing.
- Keep changes additive where you can — the new flag beside the old one — and before removing one, clig.dev's "Warn before you make a non-additive change … in the program itself".
- `0.y.z` promises nothing — semver: "Anything MAY change at any time." A tool that scripts already call has left it.

## Setting the version at release

1. Find the last release tag, and read what changed since it on each surface above — the parser
   and its help pages, the exit codes, the `--json` emitters, anything that writes to disk.
2. Place each change in its row.
3. Bump the tool's own version constant, where it keeps one, in the change that ships the
   release, and tag the merge with the resulting version.
4. The tracker milestone that carried this release → rename it to the version just tagged, then
   close it; the milestone marks the release, never its number.

- A repo stating a versioning rule for its own readers — a README section, a CONTRIBUTING page — states it in its own words, saying what the table says; the two disagree → report the difference, following neither.

## Done when

The release's part is decided by the table, the version constant and the tag agree, and the
repo's own statement of the rule, where it keeps one, matches the table.
