---
name: claude-artifacts
description: "Finds, opens, supersedes and archives the local copies of artifacts, which the mirror hook keeps of every page published with the Artifact tool, files included, so each opens from every account on this machine. Use on 'the artifact store', 'the local copy', 'open it from another account', 'port 4310', 'the page renders blank', 'the store is down', 'supersede that page', 'archive that page'. Also fires on any `artifact` verb about to run and an edit under `~/.local/share/claude-artifacts/`. Not for publishing a page — the Artifact tool; not for the page's look — /house-style ."
allowed-tools: Bash(~/.local/share/claude-artifacts/bin/artifact *), Bash(launchctl kickstart *), Read, Grep, Glob
---

# Claude artifacts

- `A` is `~/.local/share/claude-artifacts/bin/artifact`; its verbs and flags → `$A --help` and `$A <verb> --help`.
- The Artifact tool's publish lands its local copy, the page and every file it sent in `files`, through the `artifact-mirror-publish` hook.
- Which account holds a hosted copy → `$A links <slug>`; from a hosted url → its row in `~/.local/share/claude-artifacts/*/registry.json`; no row → the owning account is unrecorded: say so.
- Opening a stored page → `$A open <slug> --open`.
- Which pages a session published → `$A pages`, this session's by default, `--session <id>` for another.
- A fix to an artifact → `$A links <slug>` names the account owning its hosted copy; a session on another account → name that account to Yann and stop. Otherwise copy its `source.html` into the session scratchpad, edit the copy, and redeploy it to that `url`; never edit the stored `source.html` or `current.html`.
- A generated index, registry or vault note edited by hand is skipped as `human-edited` → delete it and re-run `$A index`.

## Project config

- `~/.claude/skills/agents-config/integrations/claude-artifacts.md`, read with `~/.claude/skills/agents-config/scripts/agents-config get claude-artifacts home` → the store's URL and label; config absent → `$A` still serves.

## Stored pages

- A stored page with no hosted copy (`state: local-only`) → edit its `source.html`, then `$A publish` that file; its place in the store decides the group and slug.
- A wrong page is replaced with `$A supersede <slug> --by <new> --reason <text>`, never overwritten.
- A page a script rebuilds → `$A stamp <file>` on its output before the hosted publish, so the hosted copy names the local one.
- Archiving a page → `$A archive <slug>`, then `$A index`; its vault note follows only on the index run.

## When it misbehaves

- Nothing answers on the port → `$A open <slug>` kickstarts the server; still down → `launchctl kickstart -k gui/$(id -u)/com.yann.claude-artifacts`.
- Which page a browser actually fetched → `~/Library/Logs/claude-artifacts.log`, never a scripted browser.
- A `/_runtime/` file answering 404 names a library the store lacks → vendor it into `_runtime/` with its sha256 in `RUNTIME.json`.
- The store's invariants → `$A sweep --check` and `$A index --check`, both exit 0 before a store change lands.
- A local copy missing files → `$A sweep --check` names each; a redeploy to the same `url` sending them completes it.
- The session row inside Claude Code does not draw, or draws twice → `references/session-row.md`.
