# Handoff — Chat Post Format

Reader — a person in a chat client; the file's body is pasted straight into a message box.

## Rules

- First line is the message's first line: no H1, frontmatter, metadata header or fence around the message.
- Shape: a one-line opener, 1–3 sentences of context, an optional short bullet list, a one-line close naming where questions go — "ping me", "thread for questions", a link.
- Length: 6–20 lines; longer content → a teammate guide, offered as a follow-up attachment, never inlined.
- Bullets as `•` or `-`; bold as `*bold*` for Slack, `**bold**` elsewhere, one style per file.
- No headers, no tables, no fenced block of ten lines or more.
- A command or path the reader copies → inline code or a one-line fence.
- No agent vocabulary — `subagent`, `dispatch`, slash commands — and no `path:line` framed for an agent.
- Slack → mrkdwn: `*bold*`, `_italic_`, `~strike~`, `` `code` ``; emoji shortcodes (`:wave:`) render as typed.
- Channel and user mentions stay plain text (`#dev`, `@yann`), for the person pasting to convert.
