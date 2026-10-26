# Operate the Vault

- This file is the whole git surface of the vault → search, capture and link never touch git.
- Run `save`, `sync` or `resolve` by hand only to recover a stopped sync, a conflict or a missing remote.
- `vault` is `$VAULT_ROOT/scripts/vault.sh`, with `$VAULT_ROOT` resolved per `SKILL.md` § Root; it is not on `PATH`.

## The shape

- One directory, two git repositories: the outer one holds `Personal/`, `synthesis/`, `inbox/`, `reports/`, `artifacts/` and every project folder but one; the inner one, `vault-nexus`, is `projects/nexus/`, cloned inside it.
- The outer `.gitignore` excludes `projects/nexus/`; keep both repos in one directory, since a bare `[[Note]]` resolves by basename across one tree only.
- Every verb covers both repositories in one call → never name which one a file belongs to.

## The commands

| Verb | What it does |
| --- | --- |
| `vault sync` | pulls both repos, merging the remote into local work, then converges the inner repo's boundary git hooks |
| `vault save "<msg>"` | stages, commits and pushes everything changed, under `<msg>` |
| `vault tick` | `save` as `vault: <host> tick`, then pulls every repo the save did not, converges the hooks, on macOS keeps `core.fsmonitor` and `core.untrackedCache` on in both repos, writes `~/.local/state/vault/last-tick` |
| `vault status` | modified count, unpushed count and remote per repo, the last tick and its age; reports a missing inner clone or a pending conflict |
| `vault resolve` | enters the pending conflict; `--continue` finishes it |
| `vault find <note>` | every file with that basename, warning `AMBIGUOUS:` on more than one |
| `vault setup` | clones every nested repo `.vault-repos` names and this machine lacks, then installs the inner repo's boundary git hooks |

- Exit codes: `0` success · `1` usage or environment · `2` the work failed and needs a person (a conflict, a refused commit, a failed push) · `3` the remote was unreachable, nothing pulled, nothing lost; 2 wins over 3 when one repo hits each.
- Never fold 3 into 2 in a caller: an unreachable remote would read as a conflict.
- Before naming a note → `vault find` it.

## When sync stops

1. A pull hits a conflict → it aborts the merge, writes `.vault-sync-failed` at the vault root, returns 2; nothing was pushed, nothing lost.
2. Until `vault resolve --continue`, `vault save` and every tick commit, pull and push nothing in that repo (exit 2); on macOS the tick job raises one notification per conflict.
3. `vault resolve` re-enters the merge and names the conflicted files; edit each, both versions sit between the markers.
4. `vault resolve --continue` finishes and pushes; it refuses while any `<<<<<<<` remains; a failed push still clears the conflict, exits 2, and the next tick pushes it.

- An unreachable remote returns 3, warns, and writes no conflict file.

## The boundary guard

- `vault-nexus` carries only `reports/` plus the root files `.gitignore` and `README.md`, matched exactly (`README.md.bak` and `notes/README.md` are refused).
- `vault save`, `vault resolve --continue` and the inner repo's git hooks (at commit and at push) refuse a commit touching anything else → move the file to the outer repo.
- The allowed set grows only for a file authored for that repo that can carry nothing from the private tree; the widening lands with its own test, positive and near-miss both.
- `NESTED_ALLOWED_PREFIX` and `NESTED_ALLOWED_ROOT_FILES` are defined once, in `scripts/nested-boundary.sh`, sourced by `vault.sh` and the hooks → change them only there.
- `vault setup` or `vault sync` refuses to install the hooks while the inner repo sets `core.hooksPath` → unset it for `vault-nexus`, or point it at a directory private to that repo, then re-run `vault setup`.

## What drives it

- One job per host runs `~/.claude/skills/obsidian/scripts/vault-tick` every 5 minutes: launchd on macOS, a systemd user timer on Linux, both installed per § the steps below from `~/.claude/skills/obsidian/jobs/`; change the interval or command in `~/Code/skills`, never on the host.
- `vault-tick` resolves the root through the `vault` role, runs `vault tick`, logs to `~/.local/state/vault/tick.log`; a host with no vault logs that and exits 0.
- One scheduled writer per host: never a session hook, whose caller's timeout kills git mid-pull and whose turn count multiplies with every child session.
- A pull merges the remote, never rebases: live sessions keep writing the tree, and `--autostash` would take their in-flight files out of it. A tick commits before it fetches and merges only when the remote moved.
- `save`, `sync` and `tick` take one lock: an atomic `mkdir` of `.vault-save.lock`; the holder pid lives in `.git/vault-save.pid`; `LOCK_STALE_S` (300) reclaims an older lock only when that pid is gone; `LOCK_WAIT_S` (30) bounds the wait. `vault resolve` takes none.

## Editing the tooling

- An edit to `scripts/vault.sh`, `scripts/nested-boundary.sh`, the hooks under `scripts/hooks/`, `~/.claude/skills/obsidian/scripts/vault-tick` or its job files keeps every line here true.
- `vault.sh` copies itself to a temp file, `exec`s that copy, and the copy unlinks itself → keep that detach block at the top level before any verb runs; as a function or moved, a `vault sync` that pulls a new `vault.sh` leaves the running shell reading different text. `VAULT_SH_DETACHED` guards re-entry; `VAULT_SH_ORIGIN` records the real file and `VAULT_ROOT` derives from it.
- `.vault-repos` is tracked by the outer repo, one `<path>` `<url>` row per nested repo, comments and blanks skipped; it records no commit → never pin one. The ignore probe queries `<path>/` with the trailing slash → keep it.
- The conflict artifact (`write_conflict`), every pending-conflict warning and the tick notification name `vault resolve` and agree with § When sync stops → change them together. The artifact holds one block per conflicted repo; a resolve removes only its own.
- A command whose flags differ between macOS and Linux (`stat`, `mktemp`) takes a form that runs on both.
- After any edit run `$VAULT_ROOT/scripts/test_vault.sh`: it builds real repos with real remotes in a temp tree, drives a same-line conflict, asserts the boundary guard's refusal, exit code, and that a refusal stages nothing. A case uses real file shapes: a manifest with a comment header, a real root file name.

## Adding a machine

1. Clone the outer repo, then let the tool rebuild the rest:
   ```sh
   git clone <outer-remote> <vault-root>
   <vault-root>/scripts/vault.sh setup
   ```
   `setup` reads `<vault-root>/.vault-repos` and clones any missing nested repo; it is idempotent, and refuses a path that holds files and is not a repo, or that the outer `.gitignore` does not cover. `<vault-root>` is that machine's choice.
2. Point that machine's `role: vault` config at the root it used.
3. Each code repo on that machine declares its own `AGENTS_REPORTS_DIR`; nothing derives it from a convention.
4. `vault status` before the first write.
5. Install the host's tick job from `~/.claude/skills/obsidian/jobs/`; `vault status` shows `last tick` within one interval.
   - macOS: `mkdir -p ~/.local/state/vault && cp ~/.claude/skills/obsidian/jobs/com.yann.vault-tick.plist ~/Library/LaunchAgents/ && launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.yann.vault-tick.plist`
   - Linux: `mkdir -p ~/.local/state/vault ~/.config/systemd/user && cp ~/.claude/skills/obsidian/jobs/vault-tick.{service,timer} ~/.config/systemd/user/ && systemctl --user daemon-reload && systemctl --user enable --now vault-tick.timer`

- The two repos are independent: no commit of one pins a commit of the other.
- Only the outer repo cloned → the nested path is empty and every `[[Note]]` into it renders as plain text.
- Names differing only by case collide on a case-sensitive clone → keep them unique case-insensitively.
- Adding a nested repo is three edits in one change: the clone · `/<path>/` in the outer `.gitignore` · its row in `.vault-repos`.

## Access, remotes, un-wiring, moving

- Access to the shareable repo is granted on the inner repository only: `gh repo view --json nameWithOwner` inside `projects/<shareable>/` names it → add the person there with read access. Before the first grant read what is already in that history; a grant exposes every committed file.
- Rotating a remote → `git -C <repo> remote set-url origin <new>`, `vault status` shows a remote, `vault save` pushes. `remote=NONE` on either repo → that half is unbacked.
- Un-wiring a repo → remove `env.AGENTS_REPORTS_DIR` from its `.claude/settings.local.json`; leave `projects/<slug>/`; delete it only when the reports are meant to go, after `vault find` on any note linking them.
- Exactly one nested repository is supported: `NESTED` in `scripts/vault.sh` names one path and `label()` maps it to one name → a second shareable folder is a script change. Moving the boundary: create and clone the new repo at `projects/<new>/`, add `/projects/<new>/` to the outer `.gitignore`, change `NESTED` and `label()`, run the battery.
- Moving the vault root → three declarations move together by hand, nothing derives one from another: `defaults.vault_root` in the `role: vault` config · the `~/.agents/reports` symlink · every wired repo's `env.AGENTS_REPORTS_DIR` (`grep -rl AGENTS_REPORTS_DIR ~/Code/*/.claude/`). Confirm with `vault status` plus one report write.

## Recovery

| Symptom | What it is | What to do |
| --- | --- | --- |
| `remote=NONE` in `vault status` | no remote, nothing backed up | `git remote add origin <url>`, then `vault save` |
| `vault save` exits 2 on the inner repo | the boundary guard | move the file to the outer repo |
| a `[[link]]` renders as plain text | target missing or misnamed | `vault find <note>` |
| `.vault-sync-failed` present | a conflict is pending | `vault resolve` |
| `projects/<shareable>/` is empty | inner repo not cloned | `vault setup` |
| every verb hangs, or reports a lock | a run holds, or died holding, `.vault-save.lock` | the next run reclaims a dead holder's lock; remove it by hand only when `pgrep -f vault.sh` prints nothing; a holder past 15 minutes → `kill -TERM -- -<pgid>`, `<pgid>` from `ps -o pgid= -p "$(cat <vault-root>/.git/vault-save.pid)"`; killing the shell alone holds the lock until its git command returns |
| git reports a merge in progress | a session was killed inside `vault resolve` | `vault resolve` re-enters it; `git -C <repo> merge --abort` discards the attempt and keeps local commits |
| git reports a rebase in progress | a pre-merge-based run was killed | the next tick clears it, or `vault resolve` when `.vault-sync-failed` names that repo: `rebase --abort` once started, `rebase --quit` when only its autostash was written (lands in `git stash list`) |

## Done when

- `vault status` shows a remote and 0 unpushed for both repos.
- No `.vault-sync-failed` sits at the vault root.
- Nothing outside the boundary guard's set was committed to the inner repo.
