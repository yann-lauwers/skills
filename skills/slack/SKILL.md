---
name: slack
description: "Sends and reads Slack — a DM, channel post, threaded reply, channel read, file upload — and arms a watcher that wakes the session when a teammate replies. Use on 'DM Sam', 'ping Sam', 'tell Sam on slack', 'post in #dev', 'what did the team say in #dev', 'watch for Sam's reply', a person named without the word slack, a pasted `slack.com/archives/…` permalink, or before any `curl` to `slack.com/api/*` or `mcp__*_Slack__*` call. Not for email — the mail skill; not for waiting on anything but a Slack conversation — /watching ."
---

# Slack

- Author → the configured user's token (`secret`) by default, channels included · the bot's (`bot_secret`) where the config body's bot line allows it.

## Project config

- Read a key → `~/.claude/skills/agents-config/scripts/agents-config get slack <key> [--root "$CLAUDE_PROJECT_DIR"]`, `--root` only inside a repo.
- `agents-config get slack` exits 1, `secret` resolves to nothing or `null`, or `keyless ls` lacks the item's name (uppercased, every non-alphanumeric as `_`) → report Slack unwired, naming the file or item missing, and stop; no other token or the Slack MCP stands in.
- Never fabricate a workspace, roster entry, channel id or token name.
- The floor resolves and `<repo>/docs/agents/integrations/slack.md` is absent → write it before the first call, shaped per /managing-harness , `references/skills.md` § A tool's skill and its config, and name the floor's workspace in the reply.
- A repo whose code or docs point at a workspace other than the config's `workspace` → stop and ask.

## Rules

- Every Slack op runs through its matched cookbook, whatever the transport; the payload comes from the cookbook, never improvised.
- A session holding `mcp__*_Slack__*` tools still takes the token path; the one carve-out is `references/transport.md`.
- A token reaches a call through `keyless run` only (`references/api.md § Endpoint + auth`).
- A post to `#anything`, a `C…` / `G…` id, a private channel or an MPIM → ask first via `AskUserQuestion`, with channel and preview.
- A DM to any teammate, the configured user included → post at once under the user token.
- A reply into the conversation the request pointed at → authorised by the pointing, no gate — `references/reply-in-place.md`.
- Assign every `slack.com/api/*` response to a variable, read `ok` / `error` off it, format after; keep stderr visible, never `2>/dev/null`; never pipe it straight into a formatter.
- A response that could not be read → unknown, not failed, never retried blind: `references/api.md § Error handling`.

## Routing table

Read the matched row's file before any tool call.

| Intent | Read |
| --- | --- |
| IF posting to a channel or a known channel id — "post in #dev" | THEN `cookbook/send-message.md` |
| IF the request points at a conversation — a permalink, a thread, a quoted message — "réponds-lui" | THEN `references/reply-in-place.md`, then the cookbook its last line names |
| IF DMing a member by name or email — "DM Sam", "ping me" | THEN `cookbook/dm-user.md` |
| IF reading recent messages from a channel — "what did the team say in #dev" | THEN `cookbook/read-channel.md` |
| IF resolving a name or email to a user id or DM channel | THEN `cookbook/resolve-identity.md` |
| IF attaching a file, doc, snippet or log, or content too long to inline | THEN `cookbook/upload-file.md` |
| IF waiting on a reply — "watch for Sam's reply", a session blocked on a teammate | THEN `cookbook/watch-reply.md` |
| IF drafting any outbound body | THEN `references/drafting.md` |
| IF a remote Claude-app routine holds `mcp__*_Slack__*` tools and no local token | THEN `references/transport.md` |
| IF searching messages across channels | THEN PARTIAL — read the token's granted scopes (`references/api.md § Reading the granted scopes`), say what is searchable, offer `cookbook/read-channel.md` or the missing scope |
| IF auth, an error, a rate limit or a token's scopes | THEN `references/api.md` |
| IF a config key or the config body's roster | THEN `references/config.md` |

## Done when

- The cookbook's report line is printed, and every write's `ok: true` was read off the captured response or `conversations.history` confirmed what landed · or Slack was reported unwired, naming what is missing, and nothing was sent.
