# Resolve a Slack identity

## Step 1 — Pick the resolution path

- An email → `users.lookupByEmail`, one exact call.
- A name (display, real or handle) → `users.list`.
- A roster phrase or role ("the founder") → the person the config body's roster maps it to: their user id, else by name; several entries match → ask.
- A user id (`U…`) → skip Step 2; Step 3 only if a DM channel is needed.
- A DM channel id (`D…`) → both sides through `conversations.members` when needed.

## Step 2 — Resolve

1. By email → `users.lookupByEmail`: one user or `users_not_found`; it needs `users:read.email`, confirmed in the token's granted scopes (`references/api.md § Reading the granted scopes`).
2. By name → `users.list` (`references/api.md § Method traps`), paginating by `cursor` past 100 users; match case-insensitively on `real_name`, `display_name`, `name`; several matches → ask the asker to disambiguate by email or a unique attribute.
3. No match → report the searched phrase to the asker; never guess.
4. Done when one user id is in hand, or the miss is reported.

## Step 3 — Open the DM channel (optional)

1. The caller needs a DM channel id → under the user token, the DM id the person's roster entry holds · else, and always under the bot token, `conversations.open` with `users: <user_id>`.
2. Cache the `D…` id as `user_id → dm_channel_id` for the session.

## Step 4 — Report back

- Standalone → `[name] → [user_id] ([email if known])`, plus `[dm_channel_id]` when Step 3 ran.
- Sub-step → hand the values to the calling cookbook with no user-visible report.
