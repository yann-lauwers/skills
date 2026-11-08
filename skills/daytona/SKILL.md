---
name: daytona
description: "Calls the Daytona sandbox platform and answers how its sandboxes and snapshots behave. Use on a sandbox cold start, a sandbox stopped or deleted, a create rejecting `cpu` or `memory`, an inactive or renamed snapshot, and before a Daytona API, SDK or CLI call or setting `autoStopInterval`, `autoDeleteInterval` or `ephemeral`."
user-invocable: false
---

# Daytona

Needs: `DAYTONA_API_KEY` — one Daytona organization's key; unset → say so, stop and ask the user.

- `target` — the organization's region, as the project's instructions state it; none stated → ask the user.

## Calls

- REST base `https://app.daytona.io/api`. Auth — Bearer `DAYTONA_API_KEY`:

```sh
curl -s --variable %DAYTONA_API_KEY \
  --expand-header 'Authorization: Bearer {{DAYTONA_API_KEY}}' \
  https://app.daytona.io/api/<path>
```

Provenance: 2026-11-08, curl 8.7.1, through the command the project's instructions name, `<path>` = `snapshots` — `200`, 50 snapshots.

- SDK and CLI read `DAYTONA_API_KEY`; the driver passes it as `new Daytona({ apiKey, target })`.
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
