---
name: hook-development
description: "Builds, proves, rolls out and retires Claude Code hooks and keeps their registry true. Use on 'create a hook', 'add a PreToolUse hook', 'block this command', 'from now on whenever X', 'the hook never fires', 'retire this hook'; also on a `hooks` key in a settings.json, a script under `hooks/`, a `permissionDecision` emission or a registry row. Not for whether a hook is the right home — /managing-harness ."
---

# Hook Development

## Premises

- Exit 2 blocks; exit 1 does not: a crashed hook lets through the action it exists to prevent.
- A hook fires on an act, never on wording; judgement → a `type: "prompt"` hook; a request for a regex judging prose → `references/deciding.md` § The request that will arrive, and how to answer it.
- Every check and every handler, deciding or not, has a row in `~/Code/skills/hooks/REGISTRY.md` or the repo's own registry, landing in the same change as the check; a retirement clears the row in the same change.

## Routing table

| Intent | Read |
| --- | --- |
| Whether a request deserves a hook, deterministic or model-judged, block or nudge | `references/deciding.md` |
| Writing or wiring any hook — event, matcher, handler type, payload, decision field, exit code | `references/events-and-contracts.md`, before the first file is written |
| A hook's level — user or project, shared or local | /managing-harness § Config levels |
| Changing, adding or retiring a handler of the user-level layer | `references/shared-layer.md` |
| Building one check from a signal to shipped | `references/build-procedure.md` |
| Writing or fixing a trigger | `references/trigger-design.md` |
| Writing a block or nudge text | `references/messages.md` |
| A payload field, a hang, or concurrent writers | `references/robustness.md` |
| A wired hook never fires, or fires on the wrong call | `references/events-and-contracts.md` § Facts that fail silently and § Lifecycle facts that bite, then `references/trigger-design.md`; a deny a prior read masks → `references/testing.md` § The masking trap |
| Minting, retiring or reconciling a check id, or a second script on an event already hooked | `references/registry.md` |
| Logging a decision, shipping a check that can block, or flipping observe to enforce | `references/rollout.md` |
| Claiming a hook works, or breaking one on purpose to show the claim | `references/testing.md` |
| Dispatching a subagent to attack, census or run genuine work against a hook layer | `references/test-agents.md` |
| Improving a layer that already exists | `references/auditing-a-layer.md`, then `references/hardening-cycle.md` |
| Making an existing hook smaller | `references/simplifying.md` |
| Running the inventory, or starting from the example engine | `references/toolkit.md` |
| Declaring a check built, retired or audited | `references/done-when.md` |
| None of the above | `references/deciding.md`; say which row was closest |
