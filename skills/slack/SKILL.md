---
name: slack
description: "Sends and reads Slack messages, and wakes the session when a teammate replies. Started only by /slack ."
disable-model-invocation: true
---

# Slack

Needs: `SLACK_TOKEN` — a Slack user or bot token; every call and `scripts/watch-reply.py` read it alone, the watcher exiting `error=auth` when it is unset.

- Author → the configured user's token by default, channels included · the bot's where the project's instructions allow it.

## The workspace's own choices

- Which item fills `SLACK_TOKEN` for the user and for the bot, the roster with each person's standing rules, language and register, the channels' audience and greeting, when the bot posts → as the project's instructions state them; none stated → ask the user.
- The project's instructions name no item for `SLACK_TOKEN` → report Slack unwired and stop; nothing else stands in.
- A repo whose code or docs point at a workspace other than the one `auth.test` returns → stop and ask.

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
| the configured user, the bot, its app, a DM or a channel id, or the roster | `references/config.md` |
