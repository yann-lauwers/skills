---
name: unifi
description: "Reads the UniFi Site Manager cloud API for a home console. Use to inventory consoles, sites, devices or ISP metrics, on a UniFi call answering 401 or 404, on \"unifi\", \"cloud key\", \"protect\", \"site manager\", \"the cameras\", \"what is online at home\", and before promising to arm a camera, change its recording, pull a snapshot or stream, or write an alarm rule."
---

# unifi

## Project config

- Config: the repo's `docs/agents/integrations/unifi.md` over the floor, read merged: `~/.claude/skills/agents-config/scripts/agents-config get unifi <key> --root "$CLAUDE_PROJECT_DIR"`.
- No `docs/agents/integrations/unifi.md` in the repo → ask the user; on their yes, write it per /managing-harness , `references/skills.md` § A tool's skill and its config, asking which register block names the console, never assuming one; then continue.
- `register.block` → where the resolved location's register file names its console, its site and its secret item.
- No such block in that location's register → it has no console: say so, never reach for another location's.

## Routing

| Intent | Read |
| --- | --- |
| a call, an endpoint, a 401 or a 404 | § Calls |
| camera control, arming, snapshots, alarms, console settings, or any surface § Calls doesn't name | `references/reach.md`, before promising anything |

## Calls

- Base `https://api.ui.com`, paths under `/v1/`.
- Auth — an account-scoped Site Manager key in `X-API-KEY`, never a console credential; `<SECRET>` is the resolved item uppercased, every non-alphanumeric as `_`:

```sh
keyless run -s K=<SECRET> -- curl -s --variable %K \
  --expand-header 'X-API-KEY: {{K}}' -H 'Accept: application/json' \
  https://api.ui.com/v1/hosts
```

Provenance: 2026-08-19, curl 8.7.1, `<SECRET>` as `HOME_UNIFI_NETWORK` — `200`; no key → `401`.

- Endpoints: `/v1/hosts` (consoles) · `/v1/sites` · `/v1/devices` · `/v1/isp-metrics/5m`.
- `/v1/devices` groups devices by console; `productLine` separates the controllers — `network` the console, `protect` a camera.
- `/v1/isp-metrics/5m` answers `data: []` where the routing is not a UniFi gateway.
- `pageSize` is accepted; paging past one page is unobserved → read a live response before writing a loop.

## Traps

- Device state, firmware, online status and site statistics → a live read on the day they are used; config and the vault say which console this is, never what it reports.
- `401` → missing, wrong or revoked key, indistinguishable; no refresh flow: the key is rotated by hand in the secrets store.
- `404` with a plain-text `404 page not found` body → the route does not exist on this host, console-local paths included.
- Hardware, camera placement and setup decisions → the vault, never this skill or a config.
