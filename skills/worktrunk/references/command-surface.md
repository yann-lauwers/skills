# Command Surface

Which command or flag does something is answered by the commands themselves; this file holds only where things are kept, which no page carries.

## Commands and flags

- `git-wt --help` (`git wt -h` for the summary; `git wt --help` opens a man page that is not installed) lists worktrunk's commands; `git wt <command> --help` carries one command's arguments, flags, examples and its `--format json` fields — `git wt remove --help` also carries the branch-integration checks.
- `~/.config/worktrunk/bin/<command>` with no argument prints its usage, and its exit codes where it has them (`wt-dev`): `wtk-new`, `wtk-step`, `wt-dev`, `wtk-web`.
- `~/.config/worktrunk/projects/nexus/nexus-wt usage` lists nexus's setup, daily and teardown verbs; the daily ones run as `git wt -C <tree> <alias>` through the repo's aliases.
- `git wt -C <repo> hook show` lists a repo's setup and teardown steps in order; `git wt -C <repo> config show` prints the config that applies.

## Where things are kept

| What | Where |
| --- | --- |
| `git wt` | `~/.local/bin/git-wt` → Homebrew's `worktrunk` formula (`brew upgrade worktrunk` updates it) on macOS, the release binary itself on Linux |
| user config | `~/.config/worktrunk/config.toml` — the tree path template, the global hooks, one entry per repo |
| this machine's commands | `~/.config/worktrunk/bin/`, their tests in `bin/tests/` |
| canon engine | `~/.config/worktrunk/bin/wt-sync-shared.sh`; its git-hook installer `wt-canon-relink.sh` |
| canon policy | `~/.config/worktrunk/canon/<main-checkout-name>.conf` |
| nexus layer | `~/.config/worktrunk/projects/nexus/` — `nexus-wt`, the husky hook sources in `hooks/`, `tests/` |
| ownership token | `<git admin dir>/wtk-owner`; `wtk-step gitdir <tree>` prints the admin dir |
| nexus tree identity | `<tree>/.wt-dev/identity`, excluded from git |
| dev unit records and logs | `wt-dev path <tree>` → under `~/.local/state/wt-dev/` |
| nexus clusters | data `~/.local/share/wt-pg/<12-hex>/`, socket `~/.local/run/pg/<12-hex>/` |
| nexus seed dump | `~/.local/share/nexus/seed.dump` |
| `ports`-edge slots | `~/.local/state/wtk/slots/` |
| nexus tunnel records | `~/.local/state/nexus-wt/tunnels/<id>` |
| worktrunk's own logs | `<repo>/.git/wt/logs/`; `git wt config state logs` lists them |
