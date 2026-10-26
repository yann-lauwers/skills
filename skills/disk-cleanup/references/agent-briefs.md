# Research briefs

One Sonnet agent per area, all dispatched in one message, each brief filled with `<scratch>` (the session scratchpad holding `tree.txt` and `scan.txt`) and today's date.

## Shared preamble — every brief opens with it

```
Skills: none

Read-only disk research on this Mac. Delete, move, prune, uninstall and kill nothing; write files only under <scratch>/agents/. Machine load runs high: targeted `du -sk`, `find -maxdepth`, `stat`, never a whole-disk walk. Dry-run flags only (`brew cleanup -n`, `pnpm store status`, `docker system df`).

The size map is <scratch>/tree.txt (one row per folder ≥1 GB; GB = total, other = files outside its 1 GB+ subfolders) and the raw `du` lines are <scratch>/scan.txt. Start from the rows in your area, then drill below 1 GB where the small pieces add up.

The owner's bar: rebuildable, temporary, duplicated, superseded, or untouched for over a month and not in use → candidate.

In use → a process has its cwd inside (`lsof -d cwd -Fn`), the app runs (`pgrep -x <App>`), a Claude session's transcript ~/.claude/projects/*/<uuid>.jsonl changed in the last few hours, or a live service (Postgres, a dev server) holds it.

Return a table, largest first: path | GB | what it is | why deletable (the evidence: dates, PR state, nothing running, nothing referencing it) | what is lost and how it comes back | the exact command that clears it | confidence. Then what you checked and kept, with the reason. Absolute paths, exact sizes.
```

## Areas

- Library → `~/Library`: data of uninstalled apps (`/Applications`, `~/Applications`), Electron and browser caches of closed apps, updater downloads, superseded tool versions, leaked build folders, VM images, iOS backups, old profiles; privacy-protected folders listed as unreadable, never forced.
- Agent tools → `~/.claude` (transcripts split by age, by working directories that no longer exist, subagents, `tool-results`), `~/.claude-swap-backup`, `~/.codex`, `~/.cursor`, `~/.cmuxterm`, `~/.local/share/claude-artifacts`, judged by `~/.claude/skills/claude-artifacts/references/artifact-store.md`, never by age, `~/.local/share/claude-login`.
- Toolchains and builds → `~/.cache`, `~/.local/share`, `~/.rustup`, `~/.nvm`, `~/.npm`, `~/Library/pnpm/store` (which store version the pinned pnpm uses), `/opt/homebrew`, and every `target`, `.build`, `DerivedData`, `.turbo`, `.zig-cache`, `node_modules`, `log` inside `~/Code` repos.
- Temp, worktrees and evidence → `/private/tmp` and its session scratchpads `/private/tmp/claude-501/<project>/<session-uuid>`, `/private/var/folders`, every worktree under `~/worktrees` and each repo's `.claude/worktrees` (branch, PR state through `gh pr list --state all --head <branch>`, dirty files, commits on no remote, process inside, and the rebuildable parts inside a live one), and evidence media older than a month — screenshots, videos, traces — wherever it sits, saying whether git tracks it.
- Explorer → anything the size map shows that no other area claims, and anything outside code: media libraries, VM and container disks, mail, downloads, iCloud placeholders, a folder nobody has named before; follow the bytes wherever they lead, and report what fills the gap between volume used and scanned when it can be reached.
