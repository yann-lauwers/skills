# Slack config

- The workspace sits at the user floor with `status: default`, so it resolves from any directory, inside a repo or outside one; `~/.claude/skills/agents-config/scripts/agents-config get slack workspace --show-origin` answers `floor` or `project`.
- `secret` → the user token's item, the default identity · `bot_secret` → the bot's item.
- `workspace`, `workspace_url`, `team_id` → the one workspace · `user_id` → the configured user · `bot_user_id` → the bot.
- `self_dm` → where "ping me" lands · `bot_dm` → the configured user's DM with the bot.
- `app_id` → the bot's app, where a missing scope is added before a reinstall.
- `channels` → alias → channel id; a channel not listed resolves through `conversations.list`, only once the user names it.
- `default_language` → optional; unset → ask.
- The body carries what no key can: the roster — each person's phrases, user id, role, language, register, DM id and standing rules — the bot's handle and register, and the channels' audience and greeting.
- A standing rule in a person's roster entry — how they are addressed, what may be sent to them — holds in every channel and medium, and outranks every cookbook default.
