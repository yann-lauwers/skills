# How the store works

Read before changing the store's code or layout, or when arguing one of its decisions. Operating it → the `claude-artifacts` skill; its verbs → `~/.local/share/claude-artifacts/bin/artifact --help`; the mirror hook's trigger → its row in `~/Code/skills/plugins/yann/hooks/REGISTRY.md`.

## Why it exists

- A hosted artifact belongs to the account that published it: only that account lists it, opens it or updates it.
- The local copy opens from every account here and outlives the scratchpad and the session.
- Only Artifact-tool pages enter the store; every other page stays where its skill writes it.

## Capture

1. The Artifact tool publishes; `artifact-mirror-publish` (PostToolUse, `Artifact`) runs `artifact capture`.
2. Capture finds the page by hosted id, else stored position, else resolves group and slug (§ Grouping); writes `source.html` verbatim and `current.html`; copies each file the publish sent to `snapshots/<group>/<slug>/<published path>`, keeping files earlier publishes sent and dropping each sent as `null`; writes the manifest `artifact.md` with a `remote[]` row (url, version, account, org); commits only on a real change.
3. `artifact index` regenerates `index.md`, `registry.json` and the vault note.

- The account and org on each `remote[]` row are what `claude auth status` read at capture; the hosted listing carries neither, so the manifest is the only record of ownership.
- A file capture cannot copy lands in `files_missing` with its reason; the page is still captured with `files_complete: false`.
- Keep `enableArtifact` on: off in user settings beats every per-session escape, `CLAUDE_CODE_ARTIFACT=1` included.

## Layout

```
~/.local/share/claude-artifacts/
  .git/              a commit per real change, no remote
  bin/  lib/         the CLI, the server, the store's code
  _runtime/          vendored diagram and chart libraries, sha256 in RUNTIME.json
  _sessions/         which pages each session published
  plugin/            the artifacts-local plugin (references/session-row.md)
  <group>/<slug>/    source.html · current.html · artifact.md · files -> snapshots/<group>/<slug>
  snapshots/         the only local copy of pages' files; never in git
```

- Deleting anything under `snapshots/` breaks those pages until a redeploy sends the files again.
- `store.NON_GROUP_DIRS` is the one list of top-level names that are not groups; CLI, index, browser and server all read it.

## Canonical and derived

- Every served copy is `wrap(stamp(source.html))`, a byte concatenation; republishing sends `source.html`, since the Claude Code bundle checker rejects a page wrapped twice.
- The stamp, in the `<head>` and one footer line, names the local address and every hosted copy with its account; a republish of unchanged content keeps it byte-identical.
- Generated files are hashed when written; a file whose hash no longer matches is skipped as `human-edited`.

## Grouping

`lib/artifacts_path.py` resolves the group, first match wins:

1. A stored page's own position (`group_source: store-path`).
2. The page's path under a reports tree: `…/projects/<slug>/reports/<kind>/…` → group `<slug>`, kind `<kind>`; `~/.agents/reports` → `agents`.
3. `AGENTS_ARTIFACTS_DIR` in the environment, then in the nearest `<repo>/.claude/settings.local.json`.
4. `AGENTS_REPORTS_DIR`, read for its group only.
5. Group `agents`.

- `declared_dir()` reports whether the repo itself declared a group; a fall-through to `agents` is no declaration.

## Serving

- The LaunchAgent `com.yann.claude-artifacts` serves on fixed port 4310; every stored URL, bookmark and vault link depends on that port.
- The server injects `/_runtime/` scripts at serve time; a page opened from `file://` gets none.
- Every route ends in bare `open <url>`, so the person's default browser opens it; `BROWSER` stays unset, since it overrides LaunchServices for good.
- Banner and back-link values come from manifests on one shared origin → the frame builds DOM with `textContent` and `setAttribute`, and builds an href only from a group and slug matching `^[A-Za-z0-9._-]+$`.

## Provenance

- `session_id`, `branch` and `ticket` are stamped at publish.
- A ticket is read from the branch or a `worktrees/<repo>/<ticket>` segment only: matching anywhere in the path reads `/private/tmp/claude-501/` as ticket `CLAUDE-501`.

## Vault notes

- Each page with no `parent` gets `artifacts/<group>-<slug>.md` under the vault root, resolved as the parent of `realpath(~/.agents/reports)`; `CLAUDE_ARTIFACTS_VAULT` overrides it, and a test driving a real capture sets it.
- A page never hosted says so in its note's body: an absent hosted address and an unrecorded one look identical.

## Checks

- `artifact sweep --check` → every page has a manifest and `source.html`, `unwrap(current.html)` equals `source.html`, no `files_complete: false`, every `files` link resolves, every `parent` exists.
- `artifact index --check` → index and registry match the disk in both directions; it reads the registry as it stands before regenerating it.
