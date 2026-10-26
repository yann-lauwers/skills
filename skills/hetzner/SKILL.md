---
name: hetzner
description: >-
  Manages Hetzner Cloud servers through its API — servers, firewalls, SSH keys, rescale, rebuild,
  rescue mode, IPs. Use on "hetzner", "hcloud", "rescale the server", "rebuild the server",
  "rescue mode", or before any Hetzner Cloud API request or a server created, rebuilt, rescaled or
  given a key. Not for a machine joining or leaving the private network — that network's skill.
---

# Hetzner

## Project config

- `~/.claude/skills/agents-config/scripts/agents-config get hetzner <key> [--root "$CLAUDE_PROJECT_DIR"]` — keys `secret`, `ssh_host`, `server`, `server_id`.
- A repo with no `docs/agents/integrations/hetzner.md` → ask the user; on their yes, write one per /managing-harness , `references/skills.md` § A tool's skill and its config.
- A repo on another Hetzner project → its config names `secret`, `ssh_host`, `server` and `server_id` together, `null` where it has none.
- Nothing resolves → the tool is unwired: say so and stop.

## Calls

- Base `https://api.hetzner.cloud/v1`; spec `https://docs.hetzner.cloud/cloud.spec.json`.
- Shell — `ssh <ssh_host>`.
- Auth — Bearer, the `secret` item's `api-token` field; `<SECRET>` is `secret` uppercased, every non-alphanumeric as `_`:

```sh
keyless run -s K=<SECRET>__API_TOKEN -- curl -s --variable %K \
  --expand-header 'Authorization: Bearer {{K}}' \
  https://api.hetzner.cloud/v1/servers
```

Provenance: 2026-09-25, curl 8.7.1, `<SECRET>` as `NEXUS_HETZNER` — `200`, one server.

## Traps

- `ssh_keys` is taken only at create and by `enable_rescue`; rebuild takes none and wipes the disk.
- A running server gets a key over SSH, in `authorized_keys`.
- A server object carries `location`, not `datacenter`.
- `change_type` needs the server off.
