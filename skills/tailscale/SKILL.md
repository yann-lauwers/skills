---
name: tailscale
description: "Manages the tailnet through the Tailscale API — devices, auth keys, key expiry, policy. Use on \"tailscale\", \"tailnet\", a machine joining or leaving the private network, a call to the Tailscale API, an auth key minted for a joining node, `tailscale up` on a new server, a joined server node with key expiry still on, or an edit to the tailnet's access policy."
---

# Tailscale

## Project config

- `~/.claude/skills/agents-config/scripts/agents-config get tailscale secret [--root "$CLAUDE_PROJECT_DIR"]`.
- A repo with no `docs/agents/integrations/tailscale.md` → ask the user; on their yes, write one per /managing-harness , `references/skills.md` § A tool's skill and its config.
- Nothing resolves → the tool is unwired: say so and stop.

## Calls

- Base `https://api.tailscale.com/api/v2`; the tailnet segment `-` is the token's own tailnet.
- Auth — Bearer, the `secret` item's `api-token` field; `<SECRET>` is `secret` uppercased, every non-alphanumeric as `_`:

```sh
keyless run -s K=<SECRET>__API_TOKEN -- curl -s --variable %K \
  --expand-header 'Authorization: Bearer {{K}}' \
  https://api.tailscale.com/api/v2/tailnet/-/devices
```

Provenance: 2026-09-25, curl 8.7.1, `<SECRET>` as `YANN_TAILSCALE` — `200`, a device list.

## Traps

- An auth key is a secret: pipe it from the API straight to the joining node (`tailscale up --auth-key=file:<path>`).
- A server node just joined → `POST /device/<id>/key` with `{"keyExpiryDisabled":true}`, or its key expires.
