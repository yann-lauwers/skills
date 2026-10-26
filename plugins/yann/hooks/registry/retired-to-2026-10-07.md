# Retired checks, up to 2026-10-07

The same rules as `registry/retired.md`; this part holds the retirements up to 2026-10-07 and the retired verdicts and pattern names.

## The lane, mission and execution-chain machinery, 2026-10-07

These left with the machinery they guarded, on Yann's word: the build flow is the unmodified Matt Pocock skills, and no lane, mission store, run record or supervising root remains. None has a successor.

**Retired ids — `worktree-seat-claim`, `worktree-not-departed`, `worktree-seat-taken`, `worktree-rm-dirty`, `seat-outside-its-folder`, `branch-cut-in-base`, `stash-borrow-untold`, `stash-recorded`, `stash-unpopped`, `stash-second-borrow`** (2026-10-07). The worktree-custody arms of `worktree-seat.py`: a claim ledger, refusals of a taken or abandoned worktree, an ungrouped seat, a branch cut in a base checkout, and the stash bookkeeping. `stash-safe-allow` is a grant, not a successor, and stays.

**Retired ids — `descent-stamp`, `dispatch-not-handed-off`, `skill-load-stamp`, `dispatch-stamp`, `build-owner-unloaded`, `build-dispatch-unnamed`, `relay-in-background`** (2026-10-07). The lane-chain arms of `worktree-seat.py`, stamping and observing descent, skill loads, dispatches and relays.

**Retired ids — `build-plan-row-missing`, `lane-builds-in-thread`, `lane-launch-stamp`** (2026-10-07). Lane writes checked against the build plan on disk, and the seat stamp `lane-unwatched` read. `lib/build_plan.py` went with them.

**Retired id — `integration-base-rewrite`** (2026-10-07). Refused rewriting a declared or merged-into integration base. `pr_policy.may_rewrite` stays the pull-request skill's own rule.

**Retired ids — `worktree-mission-gate`, `worktree-mission-reminder`, `worktree-mission-base-reminder`, `worktree-mission-credit`** (2026-10-07). The arms of `worktree-mission.py` holding the first write in a ticket worktree until the mission skill ran.

**Retired ids — `mission-entry-owed`, `run-stamp`, `run-store-write`, `dispatch-return`, `supervising-attendant-end`** (2026-10-07). The mission entry owed after a merge, the per-branch run record and its write guard, the dispatch-return ledger, and the pause request a closing attendant wrote. `lib/run_trace.py`, `lib/chain_steps.py` and `lib/path_tokens.py` went with them; `hook_decisions.log` no longer takes `run` or `step`.

**Retired ids — `stop-unfinished`, `turn-standing`, `lane-unwatched`, `attendant-relay-unarmed`, `stop-unwatched-wait`, `design-owed`** (2026-10-07). The `stop-unfinished.py` Stop handler and every arm it hosted: a Haiku judge blocking a close that named an action the agent could still take (1,703 blocks and 707 `broken` rows in its last 30 days), its turn-standing banner, and observing arms for unwatched lanes, unarmed relays, unwatched waits and a missing design record. `lib/turn_standing.py` went with it. The wait reflex survives only as a clause of `bar-reminder`'s line.

**Retired id — `pr-needs-proof`** (2026-10-07). An observing gate on `gh pr create`/`ready` with no validation report for the branch's ticket. Not every pull request needs validation. `lib/proof_owed.py` and `pr_policy.py`'s proof verb went with it.

**Retired id — `report-frontmatter-stamp`** (2026-10-07). Supplied a report's missing frontmatter fields on Write. `validating`'s `render_slice.py` writes its own.

`prune-registry-check.sh` and `registry-recount.sh`, which kept each reports tree's `_registry.md` counted, retired the same day with every report kind but validation; they minted no id.

## Earlier retirements

**Retired id — `managing-meta-unloaded`** (2026-09-30). The old name of `managing-harness-unloaded`, before the skill's rename.

**Retired id — `canon-migrate`** (2026-10-01). A PostToolUse and SessionStart hook whose detached `claude -p` worker rewrote canon files owing a migration behind a mechanical validator. Successor: /managing-harness 's optimize procedure, run by agents over a scanned inventory. Source and migration state archived under `~/.agents/archive/hooks/canon-migrate-2026-10-01/` and `~/.agents/archive/canon-migrations-2026-10-01/`.

**Retired ids — `reply-classification-dump`, `reply-conduct-tally`, `reply-empty-table`, `reply-process-scoreboard`, `reply-recap-section`, `reply-count-announce`, `reply-handback-label`, `reply-self-certification`, `reply-machinery-noun`, `reply-reads-as`, `reply-genuinely`, `reply-superlative`, `reply-bold-lead`, `reply-bold-inline`, `reply-deictic-recap`, `reply-artifact-intent`, `reply-own-work`, `reply-teleological-closer`, `reply-negated-twin`, `reply-worth-frame`, `reply-priced-as-money`** (2026-09-27). Twenty-one record-only `Stop` checks in `reply-forms.py`, each matching one reply phrasing. A Stop advisory arrives after the reply it fired on, and /babysit-writing 's ledger measured the same phrasings; that ledger retired 2026-10-06 with no successor. Source archived under `~/.agents/archive/hooks/`.

**Retired id — `design-medium-route`** (2026-09-23). Warned when a design-routed repo published to the local artifact store; the design flow reversed and a local page became the prescribed act. No successor.

**Retired id — `pr-watcher-inventory`** (2026-09-22). Named the PR watchers still running from `~/.local/state/pr-watch/`. `watch-pr` now runs hosted and `watchkit.py --inventory` lists it.

**Retired id — `mission-writeback-owed`** (2026-09-22). Warned on a side-store decision newer than the session's last mission write. Moved to `mission-entry-owed`, itself retired.

**Retired id — `pr-closes-open-parent`** (2026-09-22). Refused a pull request whose closing link would close a ticket with an unsettled child. Removed the same day: 11 of its 14 real rows refused a `--body` it could not read, because a multi-line body reaches `PreToolUse` unexpanded. A successor answers `allow` on an unreadable body or does not ship.

**Retired id — `compact-reprint`** (2026-09-19). Reprinted the rule files at `SessionStart(compact)`; the harness reloads them itself. No successor.

**Retired ids — `artifact-house-tokens`, `artifact-loose-colour`, `page-house-style`, `run-artifact-uncitable`** (2026-09-09 and 2026-09-08). The first three counted colour literals in a page after it existed; publishing moved behind `house-style-unloaded`. `run-artifact-uncitable` denied a Stop while a hash-named `.webm` under a reports tree went uncited, which no edit at Stop can satisfy; it had been promoted on an empty log that recorded no silent fires. No successor for any of the four.

**Retired id — `seat-title`** (2026-09-09). Stamped the cmux seat's title onto the session. Superseded by `session-title`, itself retired.

**Retired ids — `vendor-skill-unloaded`, `question-answerable`** (2026-09-08). A gate refusing a vendor's tools until its skill loaded, withdrawn the same day as disproportionate; and a Haiku judge on `AskUserQuestion` whose 17 rows all read `broken why=timeout-45s`. No successor for either; reviving the judge needs a model call proven to return inside a budget a person waits through, off the critical path.

**Retired ids — `grill-verdict-gate`, `memory-note-placement`** (recorded 2026-09-08). Removed without a retirement: a one-day observe window and a wiring-probe fire. No successor.

**Retired ids — `secret-output`, `credential-store-read`** (2026-09-02). The local secret-print and credential-read guards. Successor: the keyless pack, in `outside-packs.md`.

**Retired id — `sdk-corpus-reminder`** (2026-08-28). Reminded a session touching Agent SDK code to read its research corpus. Moved to a path-scoped rule, itself archived 2026-09-27.

**Retired id — `reflect-extract`** (2026-08-27). Appended friction observations at `SessionEnd`; the reflection batch that replaced it retired 2026-10-06. No successor.

**Retired id — `component-canon-read-first`** (2026-08-26, `bdcd06ea76c`). A per-component canon gate. Successor: `frontend-skill-unloaded`, in `project.md`.

**Retired id — `dead-slash-name`** (2026-08-26). Denied a canon write naming a `/name` nothing answered to. A name dies when a skill is renamed, not when it is typed; /managing-harness 's § The claim search covers it.

**Retired ids — `stop-wake`, `secret-file-write`** (2026-08-25). A Stop challenge read off the opt-in task board, and a write guard whose digest index of vault values went stale with no job rebuilding it. Successors: `stop-unfinished` (retired) and `keyless run`.

**Retired id — `register-numbers`** (2026-08-22). Measured replies against character caps, a proxy for prose quality. The output style re-injects its own reminder every turn. No successor.

**Retired id — `api-record-handoff`** (2026-08-17). Warned on a literal marker that every session analysing the hook quoted, so it fired only on itself. A trigger quoted in its own documentation cannot be measured. No successor.

**Retired ids — `language-match`, `context-map-registration`, `context-map-scope`, `design-pass-first`, `render-pick-missing`, `render-look-unknown`** (2026-10-06 and earlier). A reply-language recorder whose one reader retired; the old-filename twin of `glossary-map-registration`; a scope column now read from the filesystem; and the design-routing gates, retired with that flow. `house-style-unloaded` was rebuilt the same day bound to the write; the others have no successor.

**Retired ids — `domain-canon-unread`, `domain-canon-gate`, `domain-canon-reset`, `adr-placement-unread`.** The first canon-ledger checks, warning or refusing on a governed file touched or an ADR written before its glossary was read. Replaced by `canon-read-gate` and `canon-read-first`.

## Retired verdicts and pattern names

- `breaker` — until 2026-08-26 a third attempt at one path released `canon-read-first`; removed, so a row carrying it is history.
- `pattern=git-stash` — before 2026-08-27; split into `git-stash-destroy` and `git-stash-push`.
- `pattern=rm-rf` — before 2026-09-24; replaced by `rm-rf-outside-scratch`.

**Retired id — `domain-drift-nudge`** (2026-10-20). A DENY check in observe mode on `Stop`: every 5th new typed turn a model judged whether the person had argued a project term or retook a structural decision, and blocked the stop to push a glossary or ADR entry. Retired on the owner's word: what goes into `GLOSSARY.md` or an ADR is /domain-modeling 's to decide, during the session, and nothing outside it adds one. No successor. `domain-drift-nudge.py`, `domain-drift-nudge.judge.json`, `lib/domain_drift_judge.py` and `registry/domain-drift-nudge.md` are deleted (git history keeps them).
