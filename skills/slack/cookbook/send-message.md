# Send a Slack message

## Step 1 — Resolve the destination channel

0. The request pointed at a conversation — a pasted permalink, a thread, a message quoted back — with no other destination named → that conversation is the destination; decode it, read it and reply in place with `thread_ts` per `references/reply-in-place.md`.
1. A person, the configured user included ("DM Sam", "ping me", "DM me", "notify me") → leave for `cookbook/dm-user.md`.
2. A named channel ("post in #dev", "send to #engineering") → its id per `cookbook/read-channel.md` Step 1.
3. Ambiguous ("send a message", "tell the team") → `AskUserQuestion` with target options, and ask for the body.
4. Done when a channel id is in hand, or the request has left for another cookbook.

## Step 2 — Draft the message body

1. Read `references/drafting.md` first; plain text by default, in mrkdwn per its § Markup.
2. Sections, dividers, buttons → Block Kit JSON in `blocks` (https://api.slack.com/block-kit), `text` set beside it (`references/api.md § Method traps`).
3. Language → `references/drafting.md § Which language`.
4. Register → a channel whose audience the config body names takes the register given there · any other → the register its own recent messages are written in.
5. Layout → `references/drafting.md § Layout`.
6. Tabular data → the Block Kit `table` block (`references/api.md § Table block`), never a wide code block; a fenced code block only for a narrow table whose every row stays on one line unwrapped.
7. Done when the body is drafted in the audience's language and register.

## Step 3 — Confirm before posting (channels the request did not point at)

- Step 1 case 0 matched → skip this step.
- A channel this side picked always gates; no default channel skips it.

1. `AskUserQuestion` → "Send to `<#channel-name>`?", with the body verbatim in the question text or preview.
2. `Send` → Step 4 · `Edit` → redraft and re-ask · `Cancel` → stop.
3. Done when the user chose `Send`, or the post is dropped.

## Step 4 — Call chat.postMessage

1. Payload → `channel`, plus one of `text` / `blocks` / `attachments`.
2. POST per `references/api.md § Endpoint + auth` under the author `SKILL.md` names, the response captured per `SKILL.md § Rules`.
3. `ok: true` → capture `ts` and `channel`.
4. `ok: false` → surface `error` verbatim and act per `references/api.md § Error handling`; never report a send that did not land.
5. Done when `ok: true` was read, or the error was surfaced.

## Step 5 — Report back

- One line → `Posted to <#channel-name or DM> — "<first 60 chars of message>…" — ts:<ts>`, naming a non-default channel explicitly.
