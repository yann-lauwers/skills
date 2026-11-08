---
name: unifi
description: "Reads the UniFi Site Manager cloud API for a home console. Started only by /unifi ."
disable-model-invocation: true
---

# unifi

Needs: `UNIFI_API_KEY` — one Site Manager account's key; unset, curl exits 2 with `variable expansion failure`.

## The location's console

- Which console and site belong to the resolved location → as the project's instructions state them; none stated → ask the user.
- The location has no console → say so, never reach for another location's.

## Routing

| Intent | Read |
| --- | --- |
| a call, an endpoint, a 401 or a 404 | § Calls |
| camera control, arming, snapshots, alarms, console settings, or any surface § Calls doesn't name | `references/reach.md`, before promising anything |

## Calls

- Base `https://api.ui.com`, paths under `/v1/`.
- Auth — an account-scoped Site Manager key in `X-API-KEY`, never a console credential:

```sh
curl -s --variable %UNIFI_API_KEY \
  --expand-header 'X-API-KEY: {{UNIFI_API_KEY}}' -H 'Accept: application/json' \
  https://api.ui.com/v1/hosts
```

Provenance: 2026-11-08, curl 8.7.1, through the project's command — `200`; no key → `401`.

- Endpoints: `/v1/hosts` (consoles) · `/v1/sites` · `/v1/devices` · `/v1/isp-metrics/5m`.
- `/v1/devices` groups devices by console; `productLine` separates the controllers — `network` the console, `protect` a camera.
- `/v1/isp-metrics/5m` answers `data: []` where the routing is not a UniFi gateway.
- `pageSize` is accepted; paging past one page is unobserved → read a live response before writing a loop.

## Traps

- Device state, firmware, online status and site statistics → a live read on the day they are used; the location's record and the vault say which console this is, never what it reports.
- `401` → missing, wrong or revoked key, indistinguishable; no refresh flow: the key is rotated by hand in the secrets store.
- `404` with a plain-text `404 page not found` body → the route does not exist on this host, console-local paths included.
- Hardware, camera placement and setup decisions → the vault, never this skill or the location's record.
