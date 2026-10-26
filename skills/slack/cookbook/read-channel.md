# Read messages from a Slack channel

## Step 1 — Resolve the channel ID

1. A channel name (`#dev`) → the config's `channels` key or `conversations.list` (`references/api.md § Method traps`), matched on `name` without its `#`; cache it for the session.
2. An id already given (`C…` / `G…` / `D…`) → use it.
3. Done when a channel id is in hand.

## Step 2 — Fetch messages

1. `conversations.history` with `channel` and `limit`: 20 for a casual ask · up to 100 for an explicit "last N".
2. Time-bounded ("today", "this morning", "last hour") → `oldest` and/or `latest` as unix timestamps.
3. Auth → the user token (`secret`) · a channel only the bot is invited to → the bot token (`bot_secret`); both per `references/api.md § Endpoint + auth`.
4. `ok: false` → surface `error` verbatim and act per `references/api.md § Error handling`.
5. Never fabricate content the token cannot fetch.
6. Done when the messages are in hand, or the error was surfaced.

## Step 3 — Filter, format, report

1. Resolve each message's `user` id to a name through `users.info` or the session cache.
2. "what did X say" → only messages with `user == <X's user id>` · "last N" → the N most recent · "summarise" → all of them, rendered as a compact summary, never a verbatim dump.
3. Render a bullet list, oldest to newest → `[name] @ [human-readable ts]: [text]`.
4. A message over 200 chars → truncate it there with an ellipsis.
