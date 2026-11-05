---
name: claude-artifacts
description: "Operates the local artifact store, which keeps a local copy of every page published with the Artifact tool, served at http://127.0.0.1:4310 so it opens from every account on this Mac. Use when opening, fixing, superseding or archiving a published page, when a page belongs to another account, or when the store misbehaves. Also fires before an `artifact` command runs or an edit under `~/.local/share/claude-artifacts/`."
allowed-tools: Bash(~/.local/share/claude-artifacts/bin/artifact *), Bash(launchctl kickstart *), Read, Grep, Glob
disable-model-invocation: true
---

# Claude artifacts

A **local copy** is the store's version of a published page: `source.html` (the authored bytes, canonical), `current.html` (derived from it) and the files its publishes sent. The `artifact-mirror-publish` hook writes one on every Artifact publish. A **hosted copy** lives on claude.ai, one per account that published the page, and only that account sees it.

`A` is `~/.local/share/claude-artifacts/bin/artifact`; its verbs and flags → `$A --help`, `$A <verb> --help`.

## Find and open

- Every address of a page, and the account owning each hosted copy → `$A links <slug>`.
- A hosted url in hand → its row in `~/.local/share/claude-artifacts/*/registry.json`; no row → the owning account is unrecorded: say so.
- This session's pages → `$A pages`; another session's → `--session <id>`.
- Open a page → `$A open <slug> --open`, which serves it from the store; a stored file opened from disk renders its diagrams blank.

## Fix a page

1. `$A links <slug>`. Done when the owning account is known.
2. This session runs on another account → name that account to Yann and stop: a redeploy only lands from the owning account.
3. Copy `source.html` into the session scratchpad, edit the copy, and redeploy it to the hosted `url`. The mirror hook refreshes the local copy; the stored `source.html` and `current.html` stay untouched by hand.
4. A page with no hosted copy (`state: local-only`) → edit its stored `source.html` in place, then `$A publish` that file; its place in the store sets group and slug.
5. A script that rebuilds a page → `$A stamp <file>` on its output before the hosted publish, so the hosted copy names the local one.

## Retire a page

- A wrong page → `$A supersede <slug> --by <new> --reason <text>`: the store keeps it, bannered, pointing at the replacement.
- An obsolete page → `$A archive <slug>`, then `$A index`, which carries the change to its vault note.

## When it misbehaves

- Nothing answers on 4310 → `$A open <slug>` kickstarts the server; still down → `launchctl kickstart -k gui/$(id -u)/com.yann.claude-artifacts`.
- Which page a browser actually fetched → `~/Library/Logs/claude-artifacts.log`.
- A `/_runtime/` file answering 404 names a library the store lacks → vendor it into `_runtime/` with its sha256 in `RUNTIME.json`.
- A local copy missing files → `$A sweep --check` names each; a redeploy to the same `url` sending them completes it.
- An index, registry or vault note reported `human-edited` → delete it and re-run `$A index`.
- A change to the store itself lands only with `$A sweep --check` and `$A index --check` both exiting 0; how the store works inside → `references/artifact-store.md`.
- The session row inside Claude Code draws nothing, or twice → `references/session-row.md`.

## Config

- `~/.agents/skills/agents-config/scripts/agents-config get claude-artifacts home` → the store's URL and label; no config → `$A` still serves.
