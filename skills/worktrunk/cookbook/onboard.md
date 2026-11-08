# Onboard a Repo, or Change Its Entry

Steps run in order. A repo that already has an entry → § Change an existing entry.

## Step 0: Read the marker

A repo uses worktrees when its root `AGENTS.local.md` carries this section; a repo without it works in its checkout as it stands.

```markdown
## Worktrees

- Work that will commit runs in its own worktree: `~/.config/worktrunk/bin/wtk-new -C <repo> <branch> [--base origin/<base>]` cuts it under `~/worktrees/<repo>/`.
```

`grep -sF 'runs in its own worktree' "$(git -C <repo> rev-parse --show-toplevel)/AGENTS.local.md"` reads it.

- Present → onboarding goes ahead.
- Absent → onboarding IS the decision, so it is the user's: put it to them before Step 1. Where they decline, stop here and return to the caller with nothing written.
- Chosen → write the marker into the root `AGENTS.local.md`, creating it; then make sure `CLAUDE.local.md` carries `@AGENTS.local.md` as a line of its own, creating it or adding the line at its top.

**Done when:** the marker has been read, and either the user declined, or both files reach the marker line.

## Prerequisites

- `git wt --version` fails → `brew install worktrunk` on macOS, the release binary on Linux; say so and stop.
- No `~/.config/worktrunk/bin/` on this host → the layer is absent here: say so and stop.

## Step 1: Find the repo's key

- The entry's key is `git -C <repo> remote get-url origin` as `<host>/<owner>/<repo>`: `git@github.com:<owner>/<repo>.git` → `github.com/<owner>/<repo>`.
- `grep -nF 'projects."<key>"' ~/.config/worktrunk/config.toml` finds an entry → § Change an existing entry instead.
- The canon conf takes another name: the main checkout's directory name (`basename "$(dirname "$(git -C <repo> rev-parse --path-format=absolute --git-common-dir)")"`).

**Done when:** the key and the canon name are both resolved, and the entry is confirmed absent.

## Step 2: Find what a fresh tree needs

1. The install command — the lockfile names the package manager.
2. Gitignored files the main checkout holds that a tree cannot run without — env files above all.
3. A build a dev run or a test needs before it can start.
4. Dev servers: their command, and whether each reads `$PORT` or can be told to (`--port $PORT --strictPort`, `-p $PORT`).
5. Anything a running server leaves behind that a removal must stop.

**Done when:** each of the five has an answer, or is recorded as absent.

## Step 3: Determine the branch convention

- worktrunk names the branch exactly as typed: it fetches nothing from a tracker, and holds no branch convention of its own.
- Ask or detect the repo's convention: a ticket tracker (`<PREFIX>-<number>`) · GitHub issues · free-form (`feat/<name>`, `fix/<name>`); it is recorded as one line in the project's instructions, never in `config.toml`.

**Done when:** the project's instructions state one convention.

## Step 4: Write the entry

Copy the entry in `~/.config/worktrunk/config.toml` closest in shape, and adapt it; `git wt hook --help` documents the syntax.

- One `[[projects."<key>".pre-start]]` block per step, in this order, each one a named command: `canon` (always) · `env` — `wtk-step copy <wt> <primary> <file>…`, or `copy-optional` for a file the main checkout may lack · `deps` — `wtk-step run <wt> deps -- <install>` · `build` — `wtk-step run <wt> build --heavy -- <build>`.
- One dev server → `aliases.dev` running `wtk-web {{ worktree_path }} <app> {{ args }} -- <command reading $PORT>`, plus `pre-remove` running `wtk-web {{ worktree_path }} <app> down`.
- A server pinning its port in tracked files cannot run twice → no `dev` alias, and the reason recorded per Step 5.
- Git hooks that re-run the canon linker after a rebase → a `relink` step running `wtk-step relink-hooks {{ worktree_path }}`; it refuses a repo whose `core.hooksPath` is set.
- More than one command per act — servers, a database, a tunnel → a project folder `~/.config/worktrunk/projects/<repo>/`, with its own `AGENTS.md`, contract and tests, per `references/tooling-contracts.md`.
- Never a `.config/wt.toml` in the repo: its hooks are committed for every clone and each needs approval.
- Canon → copy the closest `~/.config/worktrunk/canon/<name>.conf` to the canon name Step 1 resolved, keeping `CLAUDE.local.md AGENTS.local.md` in its `CANON_FILES`.

**Done when:** every need Step 2 found has a step, an alias or a hook, or a recorded reason it has none.

## Step 5: Record the repo's worktree decisions

- A TOML comment above the block it governs, only for what a reader cannot derive: a create-time default the repo always wants, with the constraint behind it · why the entry is shaped unusually — no dev alias, a step that is normally skipped.

**Done when:** every non-derivable decision is written beside the block it governs.

## Step 6: Verify

```bash
git wt -C <repo> hook show
git wt -C <repo> hook pre-start --dry-run
```

**Done when:** `hook show` lists the entry's steps in order and the dry run renders every command. A step that fails to render is the finding → report it and stop.

## Step 7: Report

- The key, the canon conf path, every step, the dev alias, then the create command that exercises it — `~/.config/worktrunk/bin/wtk-new -C <repo> <test-branch>`.
- Onboarding produces an entry, never a worktree: a caller that came here to start work still owes the create and `cookbook/depart.md`'s next step.

## Change an existing entry

- Add a setup step → a new `[[projects."<key>".pre-start]]` block at its place in the order, named so `git wt -C <tree> -y hook pre-start <name>` re-runs it alone; existing trees never get it until it is run there.
- Add a dev server, a teardown or a canon root → Step 4's lines for that part.
- Every change closes on Step 6.

**Done when:** `hook show` lists the change and every existing tree that needs it has run it.
