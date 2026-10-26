---
name: obsidian
description: "The vault tool — navigates, searches, captures into and links notes in the Obsidian vault (personal notes, synthesis, every wired repo's validation reports). Use on 'note this down', 'search the vault', 'find the handoff/report on X', 'link this note', 'set up reports for this repo', 'backlinks', or a bare pasted link or one-line idea (a capture into `inbox/`, never a cue to act). Also fires on `vault setup|status|save`, a `.vault-sync-failed` file, an edit under `.obsidian/`. Not for where a validation report lands — /validating ."
allowed-tools: Read, Grep, Glob, Bash(ls:*), Bash(find:*), Bash(readlink:*), Bash(/usr/bin/grep:*), Bash(~/.claude/skills/agents-config/scripts/agents-config:*)
---

# Obsidian

- The vault is one tree of plain Markdown that Obsidian opens: everything the app or a session writes is a file the other reads, so every verb here is a file operation.
- Writes land in the vault's own checkout; a scheduled job commits and syncs them → no git, no worktree, no sync command in a session.

## Root

- `~/.claude/skills/agents-config/scripts/agents-config role vault` → the config declaring `role: vault` (`~/.claude/skills/agents-config/integrations/obsidian.md`, a repo's `docs/agents/integrations/obsidian.md` over it); its `defaults.vault_root` is `$VAULT_ROOT`.
- Resolves nothing, or the root is not on disk → stop; keep the artifact in the reply and report any search as unrun, never empty. No path stands in for the root.
- A vault location is named only in the obsidian skill, the `role: vault` config, the `~/.agents/reports` pointer, a repo's `env.AGENTS_REPORTS_DIR`, a reply, a path example the user wrote, and `allowed-tools` patterns or enforcement code.

## Layout

- Six top-level folders, closed: `Personal/` · `inbox/` · `synthesis/` · `projects/<slug>/` · `reports/` · `artifacts/`.
- `Personal/` is PARA: `Projects/` (ends; a folder from note 1) · `Areas/` (ongoing; one loose `<Area>.md`, a folder from the third note) · `Archive/` (flat, moved in whole). The folder is the classification → no type in frontmatter.
- `projects/<slug>/reports/` holds a wired repo's validation reports as real files; `reports/` holds the unbound ones (`~/.agents/reports` points there); `artifacts/` holds one note per page in the local artifact store.
- A topic is an Area or waits in `inbox/` → never a new top-level folder.
- Folders scope lifecycle; `[[wikilinks]]` and index hubs carry topic.

## Find

- Resolve the root first. Content → `/usr/bin/grep -rl '<term>' "$VAULT_ROOT"/` (`-rn` for lines); filename → `find "$VAULT_ROOT"/ -iname '*<term>*.md'`.
- Frontmatter → `/usr/bin/grep -rl '^type: <kind>' "$VAULT_ROOT"/`, likewise `^project:`, `^status:`.
- Backlinks to `Foo` → `/usr/bin/grep -rl '\[\[Foo' "$VAULT_ROOT"/`; index hubs → `find "$VAULT_ROOT"/ -iname '*index*.md'`, then follow the hub's links outward.
- Names carry spaces → pass null-separated (`grep -rl --null … | xargs -0 …`).
- Prior work before non-trivial work: a ticket id is the best term; search the repo's project folder (`dirname "$AGENTS_REPORTS_DIR"`, unset → skip), then the whole root; follow relevant hits' links to depth 2.
- Credit a hit only once opened, in one line on what it says; unopened → label it unread; nothing relevant → say so.

## Capture

- A topic with no instruction → write to `inbox/`, confirm in one line, research or act only when asked.
- Placement: a personal note → `Personal/Areas/` or `Personal/Projects/`; a note on one code project → `projects/<slug>/`, never its `reports/`; agent-setup or cross-project method → `synthesis/`; unresolved → `inbox/`, which nothing clears unless asked.
- Search first; an existing note covers it → edit that one, never a sibling.
- Filename `Title Case.md`; a file under `reports/` keeps its kebab-case name. Never `index.md`: a hub is `_<Topic> Index.md`, curated with one line per entry.
- Frontmatter: `type` (note · index · reference · handoff · analysis · decision), `project` (`personal` or the group slug), `created` (today, `YYYY-MM-DD`), `tags` (lowercase). Reports are `type: validation`.
- Body is the knowledge, then `## Related` with `[[wikilinks]]`; add the note to its topic hub. A `[[Topic]]` with no note yet is a deliberate stub.

## Link

- `[[Exact Title]]` resolves by basename across the tree → keep basenames unique, case-insensitively.
- Inside any vault file cite a note `[[slug]]`, a multi-file report `[[<slug>/index]]`, a repo file `path:line`, anything else its URL or id.
- Rename → grep `\[\[Old Name`, rename and rewrite every match in one pass, done when no match is left.
- `New link format` stays "Shortest path"; never "Absolute path in vault".

## Wire a repo's reports

- `env.AGENTS_REPORTS_DIR` in the repo's `.claude/settings.local.json` is the whole binding: an absolute path to `$VAULT_ROOT/projects/<slug>/reports`, merged into the existing `env`; link nothing into the repo.
- `<slug>` is the repo's basename, worktree-safe: `basename "$(cd "$(git rev-parse --git-common-dir)/.." && pwd)"`. Several repos of one product may share one folder only with one audience and one tracker → read the other repos' declarations first (`grep -l AGENTS_REPORTS_DIR ~/Code/*/.claude/settings.local.json`); a joining repo declares the group's folder.
- Then `mkdir -p` the folder, move any in-repo reports there, remove the emptied directory. Un-wiring removes the key and leaves the folder.
- Folder name still open → ask.

## Hands off

- A job every 5 minutes (`~/.claude/skills/obsidian/scripts/vault-tick`) commits and syncs the vault; a note reaches the other host within two ticks.
- `projects/nexus/` is its own git repository, shared with teammates, and holds only `reports/` plus root `.gitignore` and `README.md`; a commit touching anything else is refused → such a file belongs outside `projects/nexus/`.
- `$VAULT_ROOT/.vault-sync-failed` exists → a merge conflict is pending: `$VAULT_ROOT/scripts/vault.sh resolve`, edit the marked files, `resolve --continue`. Any other sync trouble → report it, run no git on the vault.

## Operate

- Adding a machine, the `vault` verbs and exit codes, access, remote rotation, un-wiring, moving the root, the boundary set growing, a lock or merge stuck, an edit to `vault.sh` or `vault-tick` → `references/operate.md`.

## The app

- `.obsidian/` is the app's state: version plugins, themes and settings; exclude `workspace*.json`.
- The graph, backlinks pane, autocomplete, plugins and mobile add nothing a file depends on; the vault works with the app absent.
- A rename inside the app repairs inbound links (with "Automatically update internal links" on); outside it nothing does.
- Obsidian Sync is never the sync layer: it reaches only Obsidian clients.
- `Personal/` holds tax, banking and insurance records → never quote it into a ticket, PR, commit, message or published artifact.
