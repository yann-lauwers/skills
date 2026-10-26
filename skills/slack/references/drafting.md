# Drafting an outbound message

- Every sending cookbook — `cookbook/dm-user.md`, `cookbook/send-message.md`, `cookbook/upload-file.md` — reads this file before the body is written.
- This file owns layout, language and what a message may cite; register and standing rules come from the recipient's roster entry in the config body · posting as the bot → the bot's register there.

Load /voice before drafting the body; unavailable → say so, and match the voice of the thread's recent messages.

## Which language

- Language → the target's roster entry in the config body.
- Recipient missing from the roster, or its entry missing a language → `default_language`; none named → ask; never draft in a language nobody chose.
- Channel post → every roster member in the audience shares one language: use it · mixed audience: ask.

## Greet once per conversation, not per message

- A DM reads the recent exchange first (`cookbook/dm-user.md § Step 3`) and continues in it; only a fresh conversation opens with a greeting.
- A channel post opens on the greeting the config body names for its channels.

## What a message may cite

- Never cite a reports dir, a vault path, a local file path or a workspace artifact in any Slack message.
- Short content → copy it inline · too long to inline → upload it as a file (`cookbook/upload-file.md`) · hosted externally (a PR, a ticket, a dashboard) → its URL, pasted bare so Slack unfurls it.

## Layout

- Every outbound message, DM and channel alike, is a run of single-newline lines, which Slack renders as one tight block.
- One idea per line; a multi-part message is a run of short lines, never a paragraph wall.
- Several updates, asks or links → one bullet each, never a comma-run in one sentence.
- A blank line separates a bare URL from the prose about it; lines carrying prose stay adjacent.
- At most one emoji, at the end of a line.
- A channel post carries the context its readers cannot ask a follow-up about, so it runs longer than a DM.
- A one-fact reply is one line — no opener, body or closer, no bullets; the full structure is for a message with several parts.

## Markup

- `chat.postMessage` text is mrkdwn, Slack's own dialect (https://docs.slack.dev/messaging/formatting-message-text); where it differs from markdown:
- `*bold*` with a single asterisk · `_italic_` · `~strike~`.
- A link → `<https://example.com|shown text>`; a bare URL unfurls on its own.
- A list → a literal `•` or `-` at the start of each line, one item per line; mrkdwn has no list syntax.
- A table → the Block Kit `table` block (`references/api.md § Table block`), or an uploaded snippet over its limits; pipes render as raw text.
- A mention → `<@USERID>`; `<!channel>` / `<!here>` notify every member and go in only when the user asks.
- The Claude-app connector route takes standard markdown instead → `references/transport.md`.
