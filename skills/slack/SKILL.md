---
name: slack
description: "Sends and reads Slack messages, and wakes the session when a teammate replies. Started only by /slack ."
disable-model-invocation: true
---

# Slack

- Author → the configured user's token (`secret`) by default, channels included · the bot's (`bot_secret`) where the config body's bot line allows it.

## Project config

- Read a key → `~/.claude/skills/agents-config/scripts/agents-config get slack <key> [--root "$CLAUDE_PROJECT_DIR"]`, `--root` only inside a repo.
- `agents-config get slack` exits 1, `secret` resolves to nothing or `null`, or `keyless ls` lacks the item's name (uppercased, every non-alphanumeric as `_`) → report Slack unwired, naming the file or item missing, and stop; nothing else stands in.
- The floor resolves and `<repo>/docs/agents/integrations/slack.md` is absent → write it before the first call, per /agents-config , and name the floor's workspace in the reply.
- A repo whose code or docs point at a workspace other than the config's `workspace` → stop and ask.

## Rules

- Every Slack op runs through its matched cookbook; the payload comes from the cookbook, never improvised.
- A token reaches a call through `keyless run` only (`references/api.md § Endpoint + auth`).
- A post to `#anything`, a `C…` / `G…` id, a private channel or an MPIM → ask first via `AskUserQuestion`, with channel and preview.
- A DM to any teammate, the configured user included → post at once under the user token.
- A reply into the conversation the request pointed at → authorised by the pointing, no gate — `references/reply-in-place.md`.
- Assign every `slack.com/api/*` response to a variable, read `ok` / `error` off it, then format; stderr stays visible, never `2>/dev/null`.
- A response that could not be read → unknown, not failed, never retried blind: `references/api.md § Error handling`.

## Routing table

Read the matched row's file before any tool call.

| Intent | Read |
| --- | --- |
| posting to a channel or a known channel id | `cookbook/send-message.md` |
| the request points at a conversation — a permalink, a thread, a quoted message | `references/reply-in-place.md`, then the cookbook its last line names |
| DMing a member by name or email, "ping me" included | `cookbook/dm-user.md` |
| reading recent messages from a channel | `cookbook/read-channel.md` |
| resolving a name or email to a user id or DM channel | `cookbook/resolve-identity.md` |
| attaching a file, doc, snippet or log, or content too long to inline | `cookbook/upload-file.md` |
| waiting on a reply, a session blocked on a teammate included | `cookbook/watch-reply.md` |
| drafting any outbound body | `references/drafting.md` |
| searching messages across channels | read the token's granted scopes (`references/api.md § Reading the granted scopes`), say what is searchable, offer `cookbook/read-channel.md` or the missing scope |
| auth, an error, a rate limit or a token's scopes | `references/api.md` |
| a config key or the config body's roster | `references/config.md` |
