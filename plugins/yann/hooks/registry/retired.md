# Retired checks

- Every id here is retired and never reused: a log row carrying one is history. `lib/hook_registry.py` reads each `Retired id —` / `Retired ids —` clause to classify those rows.
- Retirements up to 2026-10-07, and the retired verdicts and pattern names → `registry/retired-to-2026-10-07.md`.
- A clause states what the check did, why it went, and its successor or that there is none; measurements and the argument behind it are in git history.

## The domain-canon move to the plugin, 2026-10-28

**Retired id — `canon-unplaced-read`** (2026-10-28). Refused a shell operand the hook could not resolve to a file (a variable, a substitution, a directory searched whole) while the canon above it was unread. It rested on re-parsing each command's flags, and every review round found another spelling it misread. Successor: `canon-read-first`, which gates every directory a call runs in or names, with no flag parsing. The checks also moved from per-repo copies into the `yann` plugin; NexusGPT/nexus and NexusGPT/nutshell vendor its files.

## The Codex layer, 2026-10-25

**Retired id — `codex-inject-integration-roles`** (2026-10-25). A Codex `SessionStart` handler that injected `roles.md` as session context. Went with the Codex wiring: this setup runs on Claude Code only. No successor; Claude reads the roles through `AGENTS.md`.

## The render layer, 2026-10-25

**Retired id — `wiring-render`** (2026-10-25). An arm of `settings-integrity.py` that re-rendered `wiring.json`, the settings sources, the skill links and the Codex agent TOMLs whenever their sources moved. Went with the render layer: `~/.claude/settings.json` and `~/.codex/hooks.json` are hand-written files linked from `~/Code/machine-setup/home/`. Successor for the parts kept: `link.sh` makes the skill links and runs `render-agents.py`, by hand.

**Retired id — `wiring-drift`** (2026-10-25). Warned at session start when a rendered file differed from its render or a layer file was untracked. Nothing is rendered into the hook wiring, so there is nothing to drift. No successor.

**Retired id — `settings-integrity`** (2026-10-25). Compared the bytes of the permission-system files and the hook layer's own code against a baseline, after every tool event, and kept a byte copy for recovery. Went with the render layer; every file it watched is a link into `~/Code/machine-setup`, whose git diff shows a change. No successor; `guarded-name-no-grant` still withholds the allowlists' grants.

**Retired id — `generated-output-write`** (2026-10-25). Refused an edit to a rendered output — `~/.claude/settings.json`, `~/.codex/config.toml`, a Codex agent TOML, a file through a skill link — and named its source. Those files are now their own sources, except the agent TOMLs. No successor.

**Retired id — `codex-bridge`** (2026-10-25). Recorded what the Codex bridge dropped or failed to run, and its last-good fallback (`degraded`), while it translated Codex calls into Claude-shaped ones. Codex now runs each script from `~/.codex/hooks.json` directly, and a handler reads `apply_patch` itself. No successor; the verdict `degraded` retires with it.

**Retired id — `machine-setup-drift`** (2026-10-25). Warned at startup when `~/Code/machine-setup` was behind `origin/main` or the last `machine-setup-sync` run failed. Went with the sync job: a host updates by hand. No successor.

## The audience record, 2026-10-21

**Retired id — `setup-files-stay-local`** (2026-10-21). Refused a commit carrying the files setup writes — `GLOSSARY.md`, ADRs, `docs/agents/*`, a new `## Agent skills` block, the `.claude/hooks/` files setup delivers — in any repo neither recorded `shared` in `~/.agents/setup-audience.json` nor carrying setup's hook files or `## Agent skills` block at HEAD. Removed on the owner's word: those files commit like any other. It also refused, whatever the record, `AGENTS.local.md`, `CLAUDE.local.md`, `.claude/rules/conventions.md`, a `docs/agents/` file new to git other than `domain.md`, `issue-tracker.md` and `triage-labels.md` in a shared repo, and a `docs/agents` link; those went too — the owner kept tool configs alone. Successor for the one part kept: `tool-config-commit`, which refuses `docs/agents/integrations/` alone.

**Retired id — `audience-publish-ask`** (2026-10-21). Put `bin/audience.py --record shared`, and any write to the audience record, to the owner as a permission prompt. Went with the record, `bin/audience.py` and `lib/audience_policy.py`. No successor.

## Hook-layer cleanup, 2026-10-12 and 2026-10-13

**Retired id — `canon-stays-local`** (2026-10-13). The old name of `setup-files-stay-local`, renamed because it guarded every file setup writes; its rows are that check's history.

**Retired id — `permission-ask-census`** (2026-10-13). An ANNOT arm of `permission-request.py`: one row per host permission prompt with `outcome=granted|prompted`, read by `hook-decisions --asks`. It sized `cd-relative-read-allow` and then nothing read it. `--asks` went with it. No successor. Its first 74 rows carry `backfilled`: their outcome was derived by pairing, not observed.

**Retired id — `session-title`** (2026-10-13). Named each session from its `ai-title` or its cmux seat for the status line. Removed twice on the owner's word; never rebuild a hook, plugin or status-line reader that names sessions unless Yann asks for one in so many words. `lib/hook_cmux.py` went with it. No successor.

**Retired ids — `compact-at-seam`, `postcompact-resume`** (2026-10-13). The continuous-compaction plugin's Stop and PostCompact hooks that typed `/compact` and a resume line into the session's pane. The plugin is a hooks module from 2.0.0 and writes no rows here; its outcomes show on `/compaction` and in `claude --debug`.

**Retired id — `artifact-publish-route`** (2026-10-12). A once-per-session advisory injecting the local store's publish command when a standalone HTML page was written. No successor: a page stays where its skill writes it, and only a page published with the Artifact tool reaches the local store, through `artifact-mirror-publish`. `lib/artifact_page.py` stays for `house-style-unloaded`.

**Retired ids — `user-rule-ban`, `managing-harness-unloaded`, `ticket-overlap-gate`** (2026-10-12). The last checks of `skills-line-unloaded.py`: a write under `~/.claude/rules/` denied, a canon write before /managing-harness loaded, a tracker create before the overlap check (both observing, never flipped). None blocked a call in 30 days, at an interpreter start per call. No successor; `lib/tracker_create.py` went too.

**Retired id — `canon-rendering-refresh`** (2026-10-12). A `SessionStart` arm of `domain-canon.py` re-rendering each repo's `.claude/rules/domain-canon.md` through setup-dory's `stamp-canon.py`. Repos now commit `docs/agents/domain.md`, so nothing is rendered. No successor.

**Retired id — `work-context-record`** (2026-10-12). `work-context.py` recorded the tracker ids, missions and design stores a session named, for `precompact-rearm`'s lead. Its subjects left with the lane machinery. No successor.

**Retired id — `hook-drift`** (2026-10-12). `drift-reminder.py` printed a `[HOOK-DRIFT]` banner at session start on nearly every session, about leftovers nobody acted on. The same facts stay in `hook-decisions --drift` and `--modes`, and `hook-review-notify` carries the last day's crashes.

**Retired id — `glossary-map-registration`** (2026-10-12). A reminder to register a new `GLOSSARY.md` in the nearest `GLOSSARY-MAP.md`; it never wrote a row. Successor: each repo's own domain-canon line; no check enforces it, and setup no longer delivers repo copies.

## The owner's removals, 2026-10-08

**Retired id — `permission-file-write-ask`** (2026-10-08). An ask in `auto-allow-bash.sh` on a shell write aimed at a permission-system file. No successor ask: `settings-integrity` reports every change afterwards, and `guarded-name-no-grant` still withholds both allowlists' grants.

**Retired id — `guard-file-write-ask`** (2026-10-08). `protect-guard-files.sh` raised an ask on an edit tool writing a guard script, a settings file or the bridge files. No successor; the file list in `lib/permission_files.py` stays for `settings-integrity`.

**Retired ids — `recommended-then-asked`, `ask-user-question`** (2026-10-08). An observing deny on a single-select question whose option label carried `recommend`. No successor.

**Retired id — `skills-line-unloaded`** (2026-10-08). An observing deny on a subagent writing before it loaded a skill its brief's `Skills:` line named. No successor; `skill-reach-read` and `lib/skills_line.py` retired 2026-10-11.

**Retired id — `report-tree-shape`** (2026-10-08). The old name of `validation-report-layout`, renamed once validation was the only report kind; its rows, the 170 `REPORTS_SEG` crashes of 2026-09-08 among them, are that check's history.

**Retired id — `settings-write-ask`** (2026-10-08). The ask on a shell write to the permission-system files, narrowed 2026-09-09 to a write verb at a command position, then removed with the other askers. No successor.

**Retired id — `slack-channel-post`** (2026-10-08). An observing ask on a Slack write to a channel rather than a DM. Removed before its first review. No successor.

**Retired ids — `service-lifecycle`, `track-service-start`, `reap-owned-services`** (2026-10-08). Marked a `wt start` and stopped that instance at `SubagentStop` and `SessionEnd`. No successor; the markers under `~/.claude/state/service-markers/` are read by nothing.

**Retired ids — `cmux-seat-colour`, `cmux-seat-colour-hook`** (2026-10-08). Filled a colourless seat with its folder's colour on every prompt. No successor; the command is archived under `~/.agents/archive/lanes-retired-2026-10-07/local-bin/`.

**Retired id — `vendored-patch-drift`** (2026-10-08). Named a vendored file that lost its local patch in /managing-harness 's `references/vendored.md`. No successor.

**Retired id — `watchkit-inventory`** (2026-10-08). Listed the watchers alive across a seam. No successor; `lib/kernel_lock.py` went with it, and `watchkit.py --inventory` lists watchers on request.

**Retired id — `vault-sync`** (2026-10-08). Ran `vault sync` at session start and `vault save` at every turn end, about 2,200 times a day, and cut git mid-rebase. Successor: `vault tick`, every 5 minutes from one scheduled job per host (`agents-bin/vault-tick` in machine-setup).

**Retired id — `stop-api-failure`** (2026-10-08). Recorded each turn that ended on an API error. No successor.

**Retired id — `seat-events`** (2026-10-08). Recorded why a client exited and each notification it raised. No successor.

**Retired id — `log-instructions-loaded`** (2026-10-08). Logged each loaded instruction file for `precompact-capture`'s `rules` feed, which went with it. No successor.

**Retired id — `audit-reminder`** (2026-10-08). Told a new session when `hook-review-notify` stopped delivering. No successor.
