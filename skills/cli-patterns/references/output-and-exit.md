# Output and exit codes

"Human-readable output is paramount. Humans come first, machines second" — and "have
machine-readable output where it does not impact usability" (clig.dev).

## What a command prints

- The human form on stdout; diagnostics, progress and warnings on stderr, in a `--json` run too.
- `--json` on every command whose output has structure — a table, a list, a verdict with gates.
  One object, every column the table shows plus the ones it rounds away, keys stable across
  versions. clig.dev: "Display output as formatted JSON if `--json` is passed."
- A timestamp in `--json` → epoch plus a local ISO string.
- `--plain` where the human table carries alignment or Unicode a script cannot split; a one-consumer tool skips it.
- A read command that succeeds and finds nothing prints a sentence saying so, never an empty stdout.

## Exit codes

- "Return zero exit code on success, non-zero on failure" (clig.dev) — and the page says which non-zero code means what.
- A verdict command whose "unknown" is a real state gives it its own code.
- Usage errors exit 2 (the argparse and POSIX convention), with the accepted forms in the message.
- A command that took its act and then failed to record something exits 0 and says so on its own
  line — the act is done, and a non-zero here would make a caller retry it.

## Done when

Each page names its exit codes, every structured read has `--json`, and a failing run's message
names the fix.
