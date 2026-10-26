# What the cloud key reaches

| Tier | Reached by | Covers |
| --- | --- | --- |
| Site Manager cloud | the account-scoped key, from anywhere | inventory and state — consoles, sites, devices, ISP metrics; read only |
| Console-local | a key generated on the console itself, from the same LAN | Protect control — arming, camera settings, snapshots, streams, alarm state |
| Console UI | a person, in the browser or the mobile app | Alarm Manager rules — triggers, scope, actions, geofencing |

- The tiers never compose: `api.ui.com` proxies no console-local path, so a cloud key plus a correct local path still answers `404`.
- A request landing in tier 2 or 3 → say which tier it needs and what reaching it takes; never try an endpoint.
- No API authors an alarm: tier 3 is built by a person; the contribution is the rule's content, written out for them to enter.
- A tier-3 setting can gate a tier-1 read: remote management off, or a console dropped from the account, removes its rows from `/v1/hosts` with no error → a short `data` array is a state to check, never a malformed call.

Provenance: 2026-08-19, a console-local Protect path at `api.ui.com` — `404` plain text, as for an invented path; tiers 2 and 3 are from Ubiquiti's documentation, never attempted.
