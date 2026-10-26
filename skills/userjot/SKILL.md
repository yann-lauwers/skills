---
name: userjot
description: "Reads, searches, votes on and files to public UserJot feedback boards — a product's feature requests, bug reports and roadmap — and keeps the session a vote or post replays. Use on \"file a feature request\", \"report this bug to them\", \"is that already asked for\", \"vote on that post\", \"what's on their roadmap\", \"userjot\", a product whose board is wired here (SuperWhisper among them), any call to `api.userjot.com`, or a mutation answering `UNAUTHORIZED` or an HTML challenge page."
---

# UserJot

- File, vote, search or read a roadmap → `cookbook/feedback.md`.
- The API answers something unexpected → § The API, then `check.sh`.

## Project config

- `~/.claude/skills/agents-config/integrations/userjot.md`, read through `~/.claude/skills/agents-config/scripts/agents-config get --role feedback-board <key>`, the user floor the only level: `secret`, `boards` (per product: `host`, `board_slug`, `board_id`), `default_board`.
- A product with no `boards` entry → read that board's `x1.organization.getMeta` for its slug and categories, ask the user, and on their yes add the entry through /managing-harness , `references/skills.md` § A tool's skill and its config, then continue; config absent → the same section bootstraps it, on the user's yes.
- `~/.local/share/agent-web/userjot/login.mjs` mints the session into `.state/session.json` beside it, mode 600 — never printed, committed or synced.
- `~/.local/share/agent-web/userjot/check.sh` — the contract check: exit 0 the record holds · 1 the API moved, re-discover · 2 unreachable, the record stands.

## The API

- Every board answers on one tRPC endpoint, `https://api.userjot.com/trpc/<procedure>`; `x-host: <board host>` on every call selects the board, and a call without it fails.
- Superjson envelopes: a query takes `?input={"json":{…}}`, url-encoded; a mutation posts `{"json":{…},"meta":{…}}`; answers come back as `{"result":{"data":{"json":…,"meta":…}}}`.
- Procedures: `x1.organization.getMeta` (the board's slug and categories) · `x1.roadmap.getPage` (`{"limit":N}`) · `x1.feedback.getPage` (`{"search":"<terms>","limit":N,"order":"top"}`) · `x1.submission.create`, posting `{"json":{"title":…,"description":…,"boardSlug":"<board_slug>","imagesIds":[],"onBehalfOf":null},"meta":{"values":{"onBehalfOf":["undefined"]}}}`.
- Reads answer unauthenticated; a vote or a post carries the session cookie `auth_session` (`Domain=.userjot.com`, 30 days), replayed straight against the endpoint.
- Mint it with `keyless run -s UJ_EMAIL=<SECRET>__EMAIL -s UJ_PASSWORD=<SECRET> -- node ~/.local/share/agent-web/userjot/login.mjs`, `<SECRET>` being `secret` uppercased, every non-alphanumeric as `_`; exit 2 → the flow asked for a code or a passkey, which only the user can answer.
- `login.mjs` exit 1 → bad credentials, or the login flow changed · exit 3 → no Playwright, or no credentials in its environment.
- Expiry signal — only a mutation carries one: HTTP 401 with `error.json.data.code == "UNAUTHORIZED"`.
- The owner REST API at `https://api.userjot.com/v1` manages boards the account owns and never reaches a board it only posts to.

```sh
curl -s -G -H 'x-host: <host>' \
  --data-urlencode 'input={"json":{"search":"<terms>","limit":10,"order":"top"}}' \
  https://api.userjot.com/trpc/x1.feedback.getPage
```

Provenance: 2026-09-13, curl, `superwhisper.userjot.com` with `"search":"api","limit":3` — `200`, `result.data.json` carrying `hasMore`, `nextPage` and `submissions`.

## Traps

- Carry the superjson envelope through whole, `meta` included; never unwrap it at the edge.
- Several read procedures answer `200` with `json: null` once the session is gone → never take that for an empty board; check auth through a mutation.
- The composer stores `description` Markdown as literal characters → write prose.
- A replay answering with an HTML challenge page → a TLS-fingerprint failure, never a bad session: the client changed, and re-minting fixes nothing.
