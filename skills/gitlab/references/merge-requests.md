# Merge requests

## Resolving a number

- Issues and merge requests have separate per-project sequences → `#42` and `!42` are two objects, both real.
- A bare `42` from a branch name or commit subject → read what the branch was cut for; `glab mr view 42` and `glab issue view 42` both answer, about different things.
- The full sigil set → `references/hierarchy.md § The sigils, since a parent line is written by hand`.
- `glab mr view` takes a branch name in place of a number; with no id, the `mr` verbs act on the current branch's merge request.

## Reading one

- With discussions → `glab mr view <id|branch> --comments`; `--unresolved` or `--resolved` narrows to one kind and implies `--comments`.
- Diff → `glab mr diff <id|branch>`; `--raw` to pipe it · `--color never` to parse it.
- JSON → `glab mr view <id> -F json`, filtered in the same call with `--jq '<expr>'`; which verb spells JSON which way → `references/search.md`.

## Commenting and threads

- A comment is a note → `glab mr note` (alias `comment`).
- Its flags `--message`, `--unique`, `--resolve`, `--unresolve` are deprecated and hidden from `--help` → use the subcommands, marked experimental: `create`, `delete`, `list`, `reopen`, `resolve`, `update`.
- Post → `glab mr note create <id> --message "…"` · on a diff line → add `--file <path> --line <n>`.
- Discussion ids → `glab mr note list <id> -F json`; `resolve` and `--reply <prefix>` consume them.
- Close or re-open a thread → `glab mr note resolve <id> <discussion>` · `glab mr note reopen <id> <discussion>`.
- A loop that may run twice over one merge request → `note create --unique`, which skips a body already posted.

## Triage and mutation

- External merge requests → `glab mr list -F json`, keeping authors who are not project members or owners; open by default, `--all` adds closed and merged.
- Label → `glab mr update <id> --label <a>,<b> --unlabel <c>`.
- Close → post the reason as a note first; `glab mr close <id>` takes several ids and no comment flag.
- `glab mr update --fill` prompts, and needs `--yes` in a non-interactive session; no other `mr update` form prompts.
