# Slack ids

- Every id below comes from the workspace once per session and is cached for it; none is stored.
- The configured user → `auth.test` under the user token: `user_id`, and `team` / `url` for the workspace.
- The bot → `auth.test` under the bot token: `user_id`, `bot_id` · its app, where a missing scope is added before a reinstall → `bots.info` form-encoded `bot=<bot_id>`, read `bot.app_id`.
- The self-DM, where "ping me" lands → `conversations.open` with `users: <the configured user's id>` under the user token · the bot's DM with the configured user → the same under the bot token.
- A channel → `conversations.list`, only once the user names it.
- A standing rule in a person's roster entry — how they are addressed, what may be sent to them — holds in every channel and medium, and outranks every cookbook default.
- Provenance: 2026-11-08, `auth.test` under both tokens and `bots.info` under the bot token, curl per `references/api.md § Endpoint + auth` → `ok: true`, the workspace, both user ids and the bot's app id returned.
