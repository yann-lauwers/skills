---
name: sentry
description: "Reads error-tracking issues, events, stack traces and release health from Sentry. Use when investigating a production error or crash, on \"sentry\", \"check the errors\", a Sentry issue id, event id or link, or before a call to a Sentry API host. Not for root-causing or fixing the raised error — /diagnosing-bugs ; not for wiring the Sentry SDK into app code — the repo's own skill."
user-invocable: false
---

# Sentry

Needs: `SENTRY_AUTH_TOKEN` — one Sentry org's auth token; unset, curl exits 2 with "variable expansion failure".

## The org's own choices

- The org slug, its region host (`https://de.sentry.io` for a DE-region org, else `https://sentry.io`), and which app or environment each project receives → as the project's instructions state them; none stated → ask the user, never guessing a slug.
- Its projects, their numeric ids → `GET <api_base>/api/0/organizations/<org>/projects/` through the call below.

## Calls

- Auth — Bearer, from `SENTRY_AUTH_TOKEN`:

```sh
curl -s --variable %SENTRY_AUTH_TOKEN \
  --expand-header 'Authorization: Bearer {{SENTRY_AUTH_TOKEN}}' \
  <api_base>/api/0/organizations/<org>/projects/
```

Provenance: 2026-11-08, curl 8.7.1 — `https://sentry.io`, `NEXUS_SENTRY`, org `nexus-td`: `200`, 5 projects · `https://de.sentry.io`, `GITES_DU_HARAS_SENTRY`, org `les-gites-du-haras`: `200`, 2 projects.

## Traps

- A `query=environment:` filter naming an environment the project lacks answers an empty list, never an error → an empty list counts as "nothing failing" only against an environment the project has; its environments → `GET <api_base>/api/0/projects/<org>/<project>/environments/` through the kernel above.
  Provenance: 2026-11-08, curl 8.7.1 — `https://sentry.io`, `NEXUS_SENTRY`, org `nexus-td`, project `backend-dev`: `200`, one environment, `development`.
- A hex id is an event, a numeric id an issue → read the event's `groupID` to reach its issue.
