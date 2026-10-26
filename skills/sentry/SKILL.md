---
name: sentry
description: "Reads error-tracking issues, events, stack traces and release health from Sentry. Use when investigating a production error or crash, or on \"sentry\", \"check the errors\", \"production issue\", \"crash report\", \"what is failing in prod\"; also before a call to a Sentry API host, and for a Sentry issue id, event id or link. Not for root-causing or fixing the raised error — /diagnosing-bugs ; not for wiring the Sentry SDK into app code — the repo's own skill."
user-invocable: false
---

# Sentry

## Project config

- Every key below comes from the repo's config, through `~/.claude/skills/agents-config/scripts/agents-config get sentry <key> --root "$CLAUDE_PROJECT_DIR"`; the floor carries none.
- Nothing resolves → `~/.claude/skills/agents-config/scripts/agents-config role errors`; still nothing → write `<repo>/docs/agents/integrations/sentry.md` per /managing-harness , `references/skills.md` § A tool's skill and its config, with the keys below, asking for the org and project slugs, never guessing them.

| Key | What it answers |
| --- | --- |
| `secret` | the `<entity>-sentry` item holding this repo's token |
| `org` | the organization slug |
| `projects` | the project slugs, or the brace pattern naming them |
| `api_base` | the org's region host, `https://de.sentry.io` for a DE-region org; absent → `https://sentry.io` |
| `project_id` | optional — the numeric id, where a call takes it rather than the slug |
| `token_scopes` | optional — what the token may do, read before a write such as resolving an issue |

- More than one project → the body says which app or environment each receives.

## Calls

- Auth — Bearer, the `secret` item; `<SECRET>` is `secret` uppercased, every non-alphanumeric as `_`:

```sh
keyless run -s K=<SECRET> -- curl -s --variable %K \
  --expand-header 'Authorization: Bearer {{K}}' \
  <api_base>/api/0/organizations/<org>/projects/
```

Provenance: 2026-09-13, curl 8.7.1 — `https://sentry.io`, `NEXUS_SENTRY`, org `nexus-td`: `200`, 5 projects · `https://de.sentry.io`, `GITES_DU_HARAS_SENTRY`, org `les-gites-du-haras`: `200`, 2 projects.

## Traps

- A `query=environment:` filter naming an environment the project lacks answers an empty list, never an error → an empty list counts as "nothing failing" only against an environment the project has; its environments → `GET <api_base>/api/0/projects/<org>/<project>/environments/` through the kernel above.
  Provenance: 2026-10-05, curl 8.7.1 — `https://sentry.io`, `NEXUS_SENTRY`, org `nexus-td`, project `backend-dev`: `200`, one environment, `development`.
- A hex id is an event, a numeric id an issue → read the event's `groupID` to reach its issue.
