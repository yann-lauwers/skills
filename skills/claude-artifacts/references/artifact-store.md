# The local artifact store

The store at `~/.local/share/claude-artifacts/` keeps a local copy of every artifact — a page published with the Artifact tool — page and files, per project, served from `http://127.0.0.1:4310/` so it opens from every Claude account here, since a hosted artifact is visible only from the account that published it.

- Only an artifact enters the store; every other page stays where its skill writes it.
- Read this when something is added to the store, or when a decision here is argued; operating it → the `claude-artifacts` skill.
- The commands → `~/.local/share/claude-artifacts/bin/artifact --help`; the mirror hook's trigger → its row in `~/Code/skills/plugins/yann/hooks/REGISTRY.md`.

## One route in — the Artifact tool, captured

- The Artifact tool publishes through `/api/frame/deploy/direct` with the session's own OAuth credential: a hosted page belongs to the publishing account, an update needs a page that account owns, and `action:"list"` with `scope:"mine"` returns only that account's.
- No setting self-hosts the tool: its host is derived from the API base URL.
- Never set `enableArtifact: false`: off in user settings wins over every per-session escape, `CLAUDE_CODE_ARTIFACT=1` included, so it takes sharing away from every later session.
- The hosted page reaches a person away from this machine; the local copy, the page and every file its publishes sent, opens from every account here and outlives the scratchpad and the session.
- `artifact-mirror-publish` stamps each mirrored copy with the account and org `claude auth status` reads at that moment; the hosted listing carries neither.

## What happens when a page is captured

1. The Artifact tool publishes to `claude.ai/code/artifact/<slug>`, then `artifact-mirror-publish` (PostToolUse, `Artifact`) runs `artifact capture`.
2. Capture finds the page by its hosted id, else by its stored position, else resolves the group (§ Grouping; a capture records no kind) and slug from its path; writes `source.html` (the authored bytes, verbatim) and `current.html` (`wrap(source.html)`, what the server sends); copies each file the publish sent in `files` to `snapshots/<group>/<slug>/<published path>`, keeping the files earlier publishes sent and dropping each sent as `null`; then writes `artifact.md`, the manifest (state, provenance, hashes, runtime, a `remote[]` row with url, version, account and org, and the `files` record); sets `state: published`; and commits only when something changed.
3. `artifact index` regenerates `index.md`, `registry.json` and one vault note.
4. `http://127.0.0.1:4310/<group>/<slug>/` serves it through `com.yann.claude-artifacts`, with `/_runtime/` and the back button injected.

- `artifact publish` re-derives a stored page from its own `<root>/<group>/<slug>/source.html` and refuses every other path.
- A file capture cannot copy (a source gone, a path above the page, an `{artifact, path}` source with no local copy) lands in `files_missing` with its reason; the page is still captured, `files_complete` is false, and the mirror hook names the file.

## The store's shape

```
~/.local/share/claude-artifacts/
  .git/                      its own repo; a commit per real change, no remote
  bin/artifact               the CLI; `artifact --help` lists its verbs
  bin/artifact-server        the HTTP server and the browser
  lib/                       artifacts_path · store · index · browser
  _runtime/                  mermaid + chart, vendored, sha256 in RUNTIME.json
  _incoming/                 the harvested back catalogue, not yet placed
  _sessions/                 which pages each session published
  plugin/                    the artifacts-local plugin
  tests/  docs/              the store's own suites and notes — never a group
  <group>/
    index.md  registry.json  .generated.json    generated; hash-guarded
    <slug>/
      source.html            CANONICAL — authored, unwrapped
      current.html           DERIVED = wrap(source.html)
      artifact.md            the manifest
      files -> snapshots/<group>/<slug>   the files the artifact's publishes sent, at their published paths
  snapshots/<group>/<slug>/              those files' bytes; never a group, never in git
```

- `snapshots/` holds the only local copy of live artifacts' files: deleting any of it breaks those pages until a redeploy sends the files again, and `artifact sweep --check` names each break.

- `store.NON_GROUP_DIRS` is the one list of top-level names that are not groups; the CLI, the index, the browser and the server all read it.
- The server answers 404 for a name in that list, a dot- or underscore-prefixed name, and a name with no directory behind it.

## Pages that belong together — kind, parent, files, immutable

- These flags serve the pages `artifact publish` stored before the store took artifacts only; a capture sets none of them.
- The store records how pages relate and never interprets it: `kind` is an opaque label.

| Flag | Recorded as | Effect |
| --- | --- | --- |
| `--kind K` | `kind`, `kind_source: declared` | overrides the kind a stored page's manifest kept |
| `--parent P` | `parent` | the browser nests the page under `P`, and only `P` gets a vault note; a `P` not yet published is accepted |
| `--immutable` | `immutable: true` | a later publish of different bytes to that slug exits 5 and writes nothing; identical bytes pass as unchanged |
| `--ticket T` | `ticket` | stamps a ticket on a stored page |

### A page that links a tree beside it

- An artifact's files sit at their published paths under its page, as on the host, so `/<group>/<slug>/<path>` serves each from `files/<path>` (the route table in `artifact-server`'s header) and no link climbs above the route.
- A page served at a different depth than its source loses every `../` link that climbs above its route: 298 pages stored before the store took artifacts only render without their stylesheets, and stay archived as they are.

### Superseding a page

- `artifact supersede <slug> --by <other> [--reason TEXT]` marks a page superseded without touching its bytes.
- Superseded is terminal, as archived is: the row leaves the default listing and returns with the archived chip or a search.
- The server banners the page with a link to its replacement, and its vault note names the replacement as a wikilink, a served URL and the reason.
- Every banner and back-link value comes from a manifest a caller wrote, on the one shared origin `127.0.0.1:4310` → the frame builds its DOM with `textContent` and `setAttribute`, never `innerHTML`, escapes `<`, `>` and `&` in any value it embeds in a script, and builds an href only from a group and slug matching `^[A-Za-z0-9._-]+$`.

### Canonical and derived

- `source.html` is canonical and `current.html` derived: wrap downward, a byte concatenation; never unwrap at republish, since the Claude Code bundle checker rejects *"repeated artifact skeletons (`<!doctype html><html><head>…` wrapped around the page again)"*.
- The strip runs exactly once, at import, and the manifest records its offsets.

### Outside the vault

- The store lives outside the vault; where a page placed inside the vault lands, and what the guard refuses → /obsidian , `references/operate.md` § The boundary guard.
- How the store outlives the disk → § Surviving the machine.
- The vault keeps one small note per artifact at `artifacts/<group>-<slug>.md` under the vault root, so a prior-work grep finds the page.

## Grouping — one declaration, two trees

- `lib/artifacts_path.py` resolves an artifact's group, first declaration wins:
  1. The page's own path under a reports tree (`from_reports_path()`): `…/projects/<slug>/reports/<kind>/…` answers group `<slug>` and kind `<kind>`; the user-level tree `~/.agents/reports` points into answers `agents`.
  2. `AGENTS_ARTIFACTS_DIR` in the environment.
  3. The same key in the nearest `<repo>/.claude/settings.local.json`.
  4. `AGENTS_REPORTS_DIR`, read for its group only: a repo declaring `…/projects/<slug>/reports` gets group `<slug>`.
  5. The user level, group `agents`, for work bound to no repo.
- Above all rungs, a stored page's own `source.html` names its group by position (`group_source: store-path`), whatever the environment says.
- Rung 1 sits above the environment: a page published from a report directory names its own group wherever the publishing session stands.
- Outside a reports tree nothing new is declared: artifacts follow the reports declaration; `nexus` and `nexus-ui` share one group and one index.
- Reports and artifacts share an address, never a directory.
- The manifest records the rung as `group_source` (`reports-path` · `env` · `repo-settings` · `default` · `store-path`) and the kind's as `kind_source` (`reports-path` · `declared` for `--kind` · null).
- `declared_dir()` reports whether the repo itself declared anything; never read a fall-through to `default` as the repo's choice.

## Serving, and why not `file://`

- Open a stored page from its served URL, never from disk: the host injects its diagram and chart libraries at serve time as a root-relative `<script src="/_runtime/mermaid-11.16.1.min.js">`, and from `file://` every diagram renders blank with nothing reported.
- Serving also restores `fetch` of a sibling, ES modules, `localStorage` on a real origin, and fonts.
- `needs_runtime` in each manifest is derived by scanning the page; a page with no diagram gets no script tag.
- A `/_runtime/` file a page asks for and the store lacks → 404 naming the file.

## How a page reaches a browser, and which one

- No route names a browser: each ends in bare `open <url>`, which LaunchServices hands to the person's default.
- `open -a` and `open -b` only to force one browser past that default.
- Never set `BROWSER`: it overrides LaunchServices and outlives any change to the default.

| The page was | What opens it |
| --- | --- |
| published with the Artifact tool | Claude Code opens the hosted URL itself, tagged `?via=auto_preview`, skipped on a redeploy, in a background, teammate, remote, desktop or vscode session, and with `CLAUDE_CODE_ARTIFACT_AUTO_OPEN` off; `artifact-mirror-publish` opens the served copy beside it under the conditions its registry row names |
| already stored, opened again | nothing — the `claude-artifacts` skill's open verb |

- `open` without `-n` hands the URL to a running browser, which adds a tab; a browser showing several processes is one Chromium app with its helpers — its main process's start time tells them apart.
- Verified 2026-09-10: `artifact open --open` logged `GET /agents/<slug>/ 200` there, with the default browser raised and Google Chrome at zero processes throughout.

## Getting back out of a page

- Every served page carries a back button and, once superseded, a banner, both injected at serve time in shadow roots; where each leads and how they stay out of the page → `~/.local/share/claude-artifacts/lib/serve_chrome.py`.

## The server

- The server is the LaunchAgent `com.yann.claude-artifacts`, `RunAtLoad` + `KeepAlive`, on the fixed port 4310.
- Keep the port fixed: every stored URL, bookmark and vault-note link has to resolve months later.
- Nothing answering → the `claude-artifacts` skill § When it misbehaves.

## Provenance, stamped at publish

- `session_id`, `branch` and `ticket` are stamped at publish; none survives the session or the worktree, and the hosted listing carries neither repo nor org.
- A ticket is read from the branch, or a `worktrees/<repo>/<ticket>` segment, and nowhere else: a pattern matched anywhere in the path reads `/private/tmp/claude-501/page.html` as ticket `CLAUDE-501`.
- A stored-source republish or capture keeps `repo`, `reports_dir`, `branch`, `ticket`, `kind` and `kind_source` from the page's manifest (each empty when it has none); only `--ticket` and `--kind` replace them, and `session_id` is stamped again.

## Every page names its other copies

- One page can live at several addresses: the local copy, and one hosted copy per account that published it, each visible only from its own account.
- Every served copy is `wrap(stamp(source.html))`; `source.html` stays the caller's bytes.
- The stamp has two fenced halves, replaced on every re-stamp and never doubled:

| Half | Where | For |
| --- | --- | --- |
| a comment, `<meta name="artifact:*">` tags, and a JSON block `#artifact-provenance` | right after `<head>`, within the first few hundred bytes | an LLM reading the page, even truncated; a script reading structure |
| one footer line, 11px, half opacity | before the page's last `</body>` | a person looking for the other copies |

- The stamp names the local address, every hosted copy with its account and publish time, and the command that rebuilds the page when its manifest records one (`--generator`, set only on pages stored before the store took artifacts only). A republish keeps the recorded generator; `--no-generator` clears it.

| Command | What it does with the stamp |
| --- | --- |
| `artifact publish` | stamps the served copy; the caller's file is never touched |
| capture (the mirror hook) | adds the new hosted copy, restamps the local one, and names every OTHER hosted copy on stderr; the hook relays that list to the model and to the person |
| `artifact stamp <file>` | stamps a file in place before a hosted publish, so the hosted copy names the local one and its siblings. A hosted copy cannot name itself: its URL exists only after the publish |
| `artifact restamp [--group]` | re-derives every served copy from its source and manifest, one commit — for pages stored before the stamp, or after its format changes |
| `artifact links <slug>` | prints every address one page lives at |
| `artifact sweep --check` | holds `unwrap(current.html)` equal to `source.html` once the stamp is set aside on both |

- A republish of unchanged content keeps the stamp byte-identical and makes no commit.
- A generator that rebuilds a page runs `artifact stamp` on its output before publishing.

## Surviving the machine — two layers

- The store is a git repo with no remote; Time Machine backs up the disk it sits on.

| Layer | Holds | Survives |
| --- | --- | --- |
| the store's own git | a commit per publish and per capture, named `<group>/<slug>` | a bad edit, a wrong overwrite |
| the vault note | both addresses, the owning account, the provenance | everything — it is the layer a prior-work grep reads |

- An artifact outlives the disk as its hosted copy, which its vault note names; a `local-only` page has no copy off this disk but Time Machine's.
- Pages stay out of the vault and their notes go in: the vault holds what a person reads and greps.
- Each artifact with no `parent` leaves one note at `artifacts/<group>-<slug>.md` under the vault root, its frontmatter carrying `served`, `hosted[]`, `accounts[]` and `kind`.
- A page with a parent writes no note; its parent's note lists it by title, slug and served URL.
- A page never published hosted says so in its note's body: an absent hosted address and an unrecorded one look identical.

## Where the note lands

- `index.notes_dir()` resolves the notes folder from `~/.agents/reports`: `realpath` it, take its parent as the vault root, append `artifacts`.
- `CLAUDE_ARTIFACTS_VAULT` overrides it, for tests only; a battery driving a real capture sets it, or its fixture note lands in the live vault.

## Hash-before-write

- Every generated file's hash is recorded when the store writes it, and the file is re-hashed before regenerating.
- A mismatch → the write is skipped and reported as `human-edited`; the store never overwrites one.

## The checks

| Command | What it proves |
| --- | --- |
| `artifact sweep --check` | every artifact has a readable manifest and a `source.html`; `unwrap(current.html)` equals `source.html`; no `files_complete: false`; every legacy `files_link` and every captured page's `files` link resolves to a directory; every `parent` names a slug in the same group |
| `artifact index --check` | the index and registry match the artifacts on disk in both directions — a row naming a directory that is gone, and a directory no row names — and no vault note stands for a page that has since gained a parent |

- The two-way check reads the registry as it stands on disk before regenerating it; checking the file the same call writes proves nothing in the disk-to-registry direction.

## The browser

- `http://127.0.0.1:4310/` lands on three doors: `/artifacts`, the pages with no `kind`; `/validations`, the `validation` kind; and `/reports`, every other kind — the last two stored before the store took artifacts only.
- The landing counts each side and breaks the reports down by kind, counting report pages, never the runs nested under them.
- Each listing is one table: most recent first, a filter box over title, slug, ticket, branch, group and repo, sortable columns, group chips, and kind chips on the reports side.
- `?g=` and `?kind=` preselect chips and compose: `/reports?g=nexus&kind=plan` is every nexus plan.
- A chip rewrites the URL inside the listing it sits in, and its count is that listing's own.
- `/` focuses the box, Escape clears it.
- `/` carrying `?kind=` serves the reports listing, and `/` carrying `?g=` the artifacts one.
- A page with a `parent` in its group sits in a collapsible list under that parent, which shows its count; a search matching only the child surfaces it with its parent.
- A child whose parent does not exist stays a top-level row.
- An archived or superseded page is hidden from the default view, counted on the archived chip that reveals it, and found by a search for its own name; `isClosed` is the one predicate the filter and that count read.
- Search runs client-side over the whole index, so it costs no round trip and survives a server restart.
- The browser deletes nothing; removing a page is a deliberate filesystem act.

## The session row — this session's pages inside Claude Code

- What it draws, where, and what breaks it → the `claude-artifacts` skill, `references/session-row.md`.

## Scope

- This covers the store, its server and its browser.
- The hooks' triggers, tiers and batteries are their rows in `~/Code/skills/plugins/yann/hooks/REGISTRY.md`.
