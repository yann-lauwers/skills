# Audit a CLI's surface

The checks are fixed; what counts as a finding on a one-person tool against a published one is judgement, set in Step 4.

## Step 1: Dump every help page

1. Run `<tool> --help`, then `<tool> <command> --help` for every command it lists, and one level deeper where a command has subcommands. Read the real output, never the source.
2. Run `<tool> --version` and `<tool>` with no arguments.

**Done when:** every page is in the transcript, and the no-argument run's behaviour is known.

## Step 2: Score each page

1. Score the top-level page and every command page against each cell of its row in `references/help-surface.md` § What each page carries.
2. Across pages, check: the same flag name for the same thing; noun-verb nesting where a command has several verbs; no verb wearing a flag.

**Done when:** each page has a row of pass/fail against those checks.

## Step 3: Read output and exit codes

1. Run each read command once for a person and once with `--json` where it exists; a command printing a table with no `--json` is a finding.
2. Provoke one failure per command that can fail, and read the exit code and the message: the message names the fix or it is a finding.

**Done when:** every read command has its output shapes and exit codes recorded.

## Step 4: Write the findings

1. One table: guideline · state today, quoting the real output where it fails.
2. Then the fix list, split in two: what is a local edit (descriptions, help strings, `--json`, exit-code epilogs, a test that holds the surface) and what changes the surface others cite (a flag becoming a subcommand, a rename) — the second half is the owner's call, with every citation named.
3. A tool with one consumer → a missing man page and a missing `--plain` are not findings; say so rather than listing them.

**Done when:** the table and the two-part fix list are in the reply, and the local edits are either made or handed over as a list.
