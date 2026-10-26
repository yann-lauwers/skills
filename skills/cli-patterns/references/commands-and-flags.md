# Commands and flags

## Verbs and nesting

- One command does one thing; a description joining two with "or" is two commands.
- Several verbs on one noun nest as `tool noun verb` — clig.dev: "Use consistent names for multiple levels of subcommand", noun-verb being the common order.
- A verb wearing a flag → cut it into a subcommand, the former default pass named as one too; every citation of the old spelling — notifier text, README, docs, other tools' skills — moves in the same change.
- No two commands with ambiguous or similar names, and no command named like a file the tool keeps that means something else — clig.dev: "Don't have ambiguous or similarly-named commands".

## Flag names

- The same flag names the same thing on every command.
- GNU: spell a long option the way the common table spells it (`--verbose`, `--output`).
- Two idioms for one concept → tolerable on one command that takes both; two commands taking different ones are a finding.
- A destructive or outward act defaults to the dry run and takes `--apply` (or the act defaults
  and `--dry-run` refuses it) — one convention per tool, stated on every page it applies to.
- A flag whose value is a moment takes local time in the form the tool prints, and the help says so.
- `-h`/`--help` and `--version` answer whatever else is on the line — clig.dev: "you should be able to add `-h` to the end of anything and it should show help."

## Done when

The command tree reads noun-verb with one verb per command, no page's help string ends in "and
exit", and the same flag spells the same thing on every page.
