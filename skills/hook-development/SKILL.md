---
name: hook-development
description: "Builds, proves live, rolls out and retires the hooks Claude Code runs — deterministic guards on events, tool calls and file state — wires them in `~/.claude/settings.json`, and keeps their check registry true. Use on 'create a hook', 'add a PreToolUse hook', 'block this command', 'from now on whenever X', 'the hook never fires', 'retire this hook'; on a `hooks` key in a settings.json, a script under `hooks/`, a `permissionDecision` emission or a registry row. Not for whether a hook is the right home — /managing-harness ."
---

# Hook Development

Hook — a program the host runs at a lifecycle point: JSON on stdin, JSON on stdout, and an exit code that decides whether the action proceeds.

- Read `references/events-and-contracts.md` before the first hook file is written or wired; the decision field differs per event, and a hook built on a remembered contract never fires.
- A hook's level — user or project, shared or local → /managing-harness § Config levels.

## Premises

Three premises hold across every reference:

- **Exit 2 blocks; exit 1 does not.** A crashing hook allows the action it exists to prevent, so a crashed hook is an absent hook.
- **A hook fires on an act, never on wording.** Deterministic by default; a request for a regex judging prose → `references/deciding.md` § The request that will arrive, and how to answer it, in three moves, the third building it. Judgement → a `type: "prompt"` hook, which writes no decision row.
- **Every check has a registry row, every handler — deciding or not — is listed, and the row lands in the same change as the check.** A check missing from the registry is a defect; a retired check is retired in the same change, row and all.

## Routing table

| Intent | Read |
| --- | --- |
| IF deciding whether a request deserves a hook, deterministic or model-judged, block or nudge — including a request to fire on wording | THEN `references/deciding.md` |
| IF writing or wiring any hook — event, matcher, handler type, payload, decision field, exit code | THEN `references/events-and-contracts.md`, first |
| IF changing, adding or retiring a handler of the user-level layer | THEN `references/shared-layer.md` |
| IF building one check from a signal to shipped | THEN `references/build-procedure.md` |
| IF writing or fixing a trigger | THEN `references/trigger-design.md` |
| IF writing a block or nudge text | THEN `references/messages.md` |
| IF handling a payload field, a hang, or concurrent writers | THEN `references/robustness.md` |
| IF a wired hook never fires, or fires on the wrong call | THEN `references/events-and-contracts.md` § Facts that fail silently and § Lifecycle facts that bite, then `references/trigger-design.md`; a deny that a prior read masks is `references/testing.md` § The masking trap |
| IF minting, retiring or reconciling a check id, or landing a second script on an event already hooked | THEN `references/registry.md` |
| IF logging a decision, shipping a check that can block, or flipping observe to enforce | THEN `references/rollout.md` |
| IF claiming a hook works, or breaking one on purpose to show the claim | THEN `references/testing.md` |
| IF dispatching a subagent to attack, census or run genuine work against a hook layer | THEN `references/test-agents.md` |
| IF improving a layer that already exists | THEN `references/auditing-a-layer.md`, then `references/hardening-cycle.md` |
| IF making an existing hook smaller | THEN `references/simplifying.md` |
| IF running the inventory, or starting from the example engine | THEN `references/toolkit.md` |
| IF declaring a check built, retired or audited — what done is for each | THEN `references/done-when.md` |
| IF the request matches none of the above | THEN `references/deciding.md`, say which row was closest |
