# Command Surface

Which command or flag does something is answered by the commands themselves; this file holds only where things are kept, which no page carries.

## Commands and flags

- `git-wt --help` (`git wt -h` for the summary; `git wt --help` opens a man page that is not installed) lists worktrunk's commands; `git wt <command> --help` carries one command's arguments, flags, examples and its `--format json` fields — `git wt remove --help` also carries the branch-integration checks.
- `~/.config/worktrunk/bin/<command>` with no argument prints its usage, and its exit codes where it has them (`wt-dev`): `wtk-new`, `wtk-step`, `wt-dev`, `wtk-web`.
- A project folder's command with `usage` lists its setup, daily and teardown verbs; the daily ones run as `git wt -C <tree> <alias>` through the repo's aliases, and its `AGENTS.md` says how to use them.
- `git wt -C <repo> hook show` lists a repo's setup and teardown steps in order; `git wt -C <repo> config show` prints the config that applies.

## Where things are kept

| What | Where |
| --- | --- |
| `git wt` | `~/.local/bin/git-wt` → Homebrew's `worktrunk` formula (`brew upgrade worktrunk` updates it) on macOS, the release binary itself on Linux |
| user config | `~/.config/worktrunk/config.toml` — the tree path template, the global hooks, one entry per repo |
| this machine's commands | `~/.config/worktrunk/bin/`, their tests in `bin/tests/` |
| canon engine | `~/.config/worktrunk/bin/wt-sync-shared.sh`; its git-hook installer `wt-canon-relink.sh` |
| canon policy | `~/.config/worktrunk/canon/<main-checkout-name>.conf` |
| project folders | `~/.config/worktrunk/projects/<repo>/` — its command, `AGENTS.md`, `CLAUDE.md`, `tests/` |
| ownership token | `<git admin dir>/wtk-owner`; `wtk-step gitdir <tree>` prints the admin dir |
| dev unit records and logs | `wt-dev path <tree>` → under `~/.local/state/wt-dev/` |
| `ports`-edge slots | `~/.local/state/wtk/slots/` |
| worktrunk's own logs | `<repo>/.git/wt/logs/`; `git wt config state logs` lists them |
