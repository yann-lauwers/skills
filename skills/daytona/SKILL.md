---
name: daytona
description: "Calls the Daytona sandbox platform and answers how its sandboxes and snapshots behave. Use on a sandbox cold start, a sandbox stopped or deleted, a create rejecting `cpu` or `memory`, an inactive or renamed snapshot, and before a Daytona API, SDK or CLI call or setting `autoStopInterval`, `autoDeleteInterval` or `ephemeral`."
user-invocable: false
---

# Daytona

## Project config

- `~/.claude/skills/agents-config/scripts/agents-config get daytona <key> [--root "$CLAUDE_PROJECT_DIR"]` — keys `secret`, `target`.
- A repo with no `docs/agents/integrations/daytona.md` → ask the user; on their yes, write one per /managing-harness , `references/skills.md` § A tool's skill and its config.
- Nothing resolves → the tool is unwired: say so and stop.

## Calls

- REST base `https://app.daytona.io/api`. Auth — Bearer, the `secret` item; `<SECRET>` is `secret` uppercased, every non-alphanumeric as `_`:

```sh
keyless run -s K=<SECRET> -- curl -s --variable %K \
  --expand-header 'Authorization: Bearer {{K}}' \
  https://app.daytona.io/api/<path>
```

Provenance: 2026-10-02, curl 8.7.1, `<SECRET>` as `NEXUS_DAYTONA`, `<path>` = `snapshots` — `200`, 43 snapshots.

- SDK and CLI → `keyless run -s DAYTONA_API_KEY=<SECRET> -- <cmd>`, the driver passing it as `new Daytona({ apiKey, target })`.
- `target` goes on the `Daytona` constructor (or `DAYTONA_TARGET`), never on the SDK's create params · REST → `target` in the create body.
- `target` omitted → the account default, where a create from a snapshot baked in another region answers `400 "Snapshot … is not available in region us"`: a region mismatch, not a missing snapshot.
- A create from a snapshot never passes `cpu` / `memory`: the snapshot bakes its own and the SDK rejects them; resource fields go only on a bare-image create.
- `executeCommand` lands as root, where Claude Code refuses `bypassPermissions` and `--dangerously-skip-permissions` → `acceptEdits`, or drop to the image's non-root user.

## Routing

| If the question is about … | Read |
| --- | --- |
| Cold starts, `autoStopInterval` / `autoDeleteInterval` / `ephemeral`, a sandbox stopped or **deleted**, what defers or resets the idle clock (open PTY, `refreshActivity`, `setAutostopInterval`), keeping a sandbox alive, tearing one down and verifying it | `references/lifecycle-config.md` |
| The snapshot warm pool, a renamed snapshot starting cold, shipping a new version, naming a snapshot, a snapshot `inactive` or refused while it still exists, reactivating one, a fallback snapshot that stops booting | `references/snapshots.md` |
| Unclear which topic / spans several | Read every `references/*.md` and answer from the union |
