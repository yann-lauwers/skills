# Onboard a Repo, or Change Its Entry

Settles whether a repo uses worktrees at all, and where it does, gives it a worktrunk project entry — finds what a fresh tree needs, writes the entry with the decisions recorded beside it, verifies. Steps 0–7 run in order, Prerequisites and Steps 1–7 only once Step 0 chose onboarding; what a tree needs and the branch convention are judgment. A repo that already has an entry → § Change an existing entry.

## Step 0: Read the repo's recorded decision

```bash
cat "$(git -C <repo> rev-parse --show-toplevel)/docs/agents/worktrees.md" 2>/dev/null
```

- Declares the repo runs without worktrees → stop here and report it.
- Absent → onboarding IS the decision, so it is the user's: put both outcomes to them before Step 1, and where they decline, write the file, then stop here and return to the caller:

```markdown
# Worktrees

This project runs without worktrees. Work happens in the checkout as it stands.

Recorded <date> by <who>. Reversing it is a worktrunk project entry for this repo, plus deleting this file.
```

**Done when:** the file has been read, and either it stopped this run, or the user chose onboarding, or their refusal is written to that path.

## Prerequisites — once Step 0 chose onboarding

```bash
git wt --version
```

- Fails → the `worktrunk` formula or the `~/.local/bin/git-wt` link is missing; → `brew install worktrunk` on macOS, the release binary on Linux; say so and stop.
- No `~/.config/worktrunk/bin/` on this host → this setup's layer is absent here: say so and stop.

## Step 1: Find the repo's key

```bash
git -C <repo> remote get-url origin
```

- The entry's key is that URL as `<host>/<owner>/<repo>`: `git@github.com:NexusGPT/nexus.git` → `github.com/NexusGPT/nexus`.
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
- Ask or detect the repo's convention: a ticket tracker (`<PREFIX>-<number>`) · GitHub issues · free-form (`feat/<name>`, `fix/<name>`); it is recorded as `branch_pattern` in the `vcs` role's project config, or its recorded `auto` stands; never in `config.toml`.

**Done when:** one convention is chosen and the `vcs` config's `branch_pattern` carries it, or its `auto` stands.

## Step 4: Write the entry

Copy the existing entry in `~/.config/worktrunk/config.toml` closest in shape, and adapt it; `references/config.md` holds the keys.

- One `[[projects."<key>".pre-start]]` block per step, in this order, each one a named command: `canon` (always) · `env` — `wtk-step copy <wt> <primary> <file>…`, or `copy-optional` for a file the main checkout may lack · `deps` — `wtk-step run <wt> deps -- <install>` · `build` — `wtk-step run <wt> build --heavy -- <build>`.
- One dev server → `aliases.dev` running `wtk-web {{ worktree_path }} <app> {{ args }} -- <command reading $PORT>`, plus `pre-remove` running `wtk-web {{ worktree_path }} <app> down`.
- A server pinning its port in tracked files cannot run twice → no `dev` alias, and the reason recorded per Step 5.
- Git hooks that re-run the canon linker after a rebase → a `relink` step running `wtk-step relink-hooks {{ worktree_path }}`; it refuses a repo whose `core.hooksPath` is set.
- More than one command per act — servers, a database, a tunnel → a project folder `~/.config/worktrunk/projects/<repo>/` like nexus's, with its own contract and tests, per `references/tooling-contracts.md`.
- Never a `.config/wt.toml` in the repo: its hooks are committed for every clone and each needs approval; this setup's steps stay in the user config.
- Canon → copy the closest `~/.config/worktrunk/canon/<name>.conf` to the canon name Step 1 resolved, per `cookbook/canon.md` § Sharing a new top-level path.

**Done when:** every need Step 2 found has a step, an alias or a hook, or a recorded reason it has none.

## Step 5: Record the repo's worktree decisions

- Record the repo's own worktree decisions as TOML comments beside the block each governs.
- Only what a reader cannot derive: a create-time default the repo always wants, with the constraint behind it · why the entry is shaped unusually — no dev alias, a step that is normally skipped.
- A fact about another resource goes in that resource's own config — a shared cache whose keyspace spans every tree, per-tree tunnel hostnames, the branch pattern: each is owned by the cache, tunnel or version-control config, where an agent reaching for that resource resolves it.

**Done when:** every non-derivable decision is written beside the block it governs.

## Step 6: Verify

```bash
git wt -C <repo> hook show
git wt -C <repo> hook pre-start --dry-run
```

**Done when:** `hook show` lists the entry's steps in order and the dry run renders every command. A step that fails to render is the finding → report it and stop, never print completion over it.

## Step 7: Print Completion

- Report the key, the canon conf path, every step, the dev alias, then the create command that exercises it — `~/.config/worktrunk/bin/wtk-new -C <repo> <test-branch>`.
- Onboarding produces an entry, never a worktree: a caller that came here to start work still owes the create and `cookbook/depart.md`'s next step.

**Done when:** the report carries the values this run resolved.

## Change an existing entry

- Add a setup step → a new `[[projects."<key>".pre-start]]` block at its place in the order, named so `git wt -C <tree> -y hook pre-start <name>` re-runs it alone; existing trees never get it until it is run there.
- Add a dev server, a teardown or a canon root → Step 4's lines for that part.
- Every change closes on Step 6.

**Done when:** `hook show` lists the change and every existing tree that needs it has run it.
