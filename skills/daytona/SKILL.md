---
name: daytona
description: "Calls the Daytona sandbox platform — REST API, SDK and CLI under this machine's key — and answers how its sandboxes and snapshots behave. Use on a sandbox cold start, a sandbox that stopped or got deleted, a create rejecting `cpu` or `memory`, an inactive or renamed snapshot, 'autoStop', 'ephemeral sandbox', 'activate snapshot'. Also fires before a Daytona API, SDK or CLI call and before setting `autoStopInterval`, `autoDeleteInterval` or `ephemeral`. Not for a project's own snapshot pipeline — that project's sandbox-ops skill."
user-invocable: false
---

# Daytona

## Project config

- `~/.claude/skills/agents-config/scripts/agents-config get daytona <key> [--root "$CLAUDE_PROJECT_DIR"]` — keys `secret`, `target`, and where a repo sets them `snapshot` (the snapshot its sandboxes boot) and `key_var` (the variable its drivers read the key from; unset → `DAYTONA_API_KEY`).
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

- SDK and CLI → `keyless run -s <key_var>=<SECRET> -- <cmd>`, the driver passing it as `new Daytona({ apiKey, target })`.
- Under the `role: app-secrets` wrapper, a `DAYTONA_API_KEY` injected outside it is overridden by the wrapper's own → inject under another name and pass it as `apiKey`, or re-export it inside the wrapped shell.
- `target` goes on the `Daytona` constructor (or `DAYTONA_TARGET`); the SDK's create params carry none · REST → `target` in the create body. Omitted → the account default, and a create from a snapshot baked elsewhere answers `400 "Snapshot … is not available in region us"`, which is not a missing snapshot.
- Create latency varies → confirm the sandbox's actual region before blaming it.
- A create from a snapshot never passes `cpu` / `memory`: the snapshot bakes its own resources and the SDK errors on them; resource fields go only on a bare-image create, the fallback when no snapshot is used.
- `executeCommand` lands as root, where Claude Code refuses `bypassPermissions` and `--dangerously-skip-permissions` → `acceptEdits`, or drop to the image's non-root user.

## Routing

Read only the file the row names.

| If the question is about … | Read |
| --- | --- |
| Cold starts, why `start()` resumes cheap, `autoStopInterval` / `autoDeleteInterval` / `ephemeral`, why a sandbox stopped or got **deleted**, what defers or resets the idle clock (open PTY, `refreshActivity`, `setAutostopInterval`), keeping a sandbox alive, tearing one down when a run ends, verifying a teardown | `references/lifecycle-config.md` |
| The snapshot warm pool, why a renamed snapshot starts cold, shipping a new snapshot version, snapshot-name constraints, a snapshot reading `inactive`, a create refusing a snapshot that still exists, reactivating one, why a fallback snapshot stops booting | `references/snapshots.md` |
| Unclear which topic / spans several | Read every `references/*.md` and answer from the union |
