# Slack Web API — how we call it

- A method's own shape → https://api.slack.com/methods.

## Endpoint + auth

- `POST https://slack.com/api/<method>` for writes and reads alike, `Content-Type: application/json; charset=utf-8`; the charset carries non-ASCII content.
- `<NAME>` → the item the config's `secret` (the user, default) or `bot_secret` (the bot) names, in its `keyless` form (`SKILL.md § Project config`).
- Build every JSON body with `jq -nc`, never with shell-escaped `-d` text.
- Every call takes this form; the token reaches curl through `--variable`, never argv:

```bash
RESP=$(keyless run -s SLACK_TOKEN=<NAME> -- curl -sS -X POST https://slack.com/api/<method> \
  --variable %SLACK_TOKEN --expand-header 'Authorization: Bearer {{SLACK_TOKEN}}' \
  -H "Content-Type: application/json; charset=utf-8" --data "$PAYLOAD")
printf '%s' "$RESP" | jq -c '{ok, error}'
[ "$(printf '%s' "$RESP" | jq -r '.ok')" = "true" ] || exit 1
```

## Method traps

- `chat.postMessage` → set `text` beside `blocks`, as the notification and screen-reader fallback · a thread reply takes the parent's `ts` as `thread_ts` · `chat.update` is unwired · `chat.delete` runs only on the user's yes to the duplicate offer in § Error handling.
- `conversations.list` → `types` defaults to `public_channel`; name `private_channel,mpim,im` to see the rest.
- `users.list` → returns deactivated members, bots and app users; humans only → `deleted: false` and `is_bot: false`.
- `conversations.history` → the token's user or bot must be a member of the channel, else `not_in_channel`.

## File upload

- `files:write` sits on the user token and the bot token separately → confirm it on the one in use.

## Table block

- The only real grid in a message: a `table` block in `blocks` — `rows` (the first row the header), each cell `{type: "raw_text"|"raw_number"|"rich_text", text}`, optional `column_settings` per column (`align`, `is_wrapped`).
- Limits → ≤100 rows · ≤20 columns · ≤10,000 chars across all cells; over any → upload a snippet (`cookbook/upload-file.md`) or post a Canvas.

## Error handling

- `ok: false` → surface `error` verbatim; never retry blind, each code takes its own action.
- A response that could not be read → the write may have landed: read `conversations.history` on the target first. Absent → retry, an upload reusing its `file_id` · present once → report its `ts`, no second send · present twice → tell the user and offer `chat.delete` on the duplicate's `ts`.
- `invalid_auth` / `not_authed` / `token_revoked` → ask the user to reinstall the app (`app_id`) and refresh the matching item.
- `missing_scope`, often with a `needed` field → ask the user to add the scope on the app (`app_id`) and reinstall.
- `not_in_channel` / `channel_not_found` → the token's user or bot is not in the channel: the bot → ask the user to `/invite @<handle>` there, the handle from the config body · the configured user → ask them to join · the other token is in it → offer posting under it, never switch.
- `msg_too_long` (40k chars) · `no_text` · `invalid_blocks` → fix the payload.
- HTTP 429 → wait `Retry-After` seconds, retry once; a second 429 → surface it, never loop.

## Reading the granted scopes

- The `x-oauth-scopes` response header on any call is what a token may do:

```sh
keyless run -s T=<NAME> -- curl -sS -D - -o /dev/null -X POST https://slack.com/api/auth.test --variable %T --expand-header 'Authorization: Bearer {{T}}' | grep -i '^x-oauth-scopes'
```

- Provenance: 2026-10-02, the text above with the nexus bot token, curl through `keyless run` → the header listed 15 scopes.
- A scope added on the app's OAuth page takes effect only after the app is reinstalled.
