# Handoff — Teammate Guide Format

Reader — a teammate reading it cold, with none of this session's context.

## Rules

- First line is an H1 naming the document.
- Under it, a 1–3 sentence plain-prose intro: what the document is and who it is for.
- Sections in H2 / H3 as the content needs; tables, callouts, checklists and links where they help; a fenced block for every command, config snippet or example the teammate copies.
- Optional: a TL;DR or quick start near the top, trade-offs and limits before the close, a verification checklist near the end.
- Length follows the content.
- Resolve every reference to this session inline — what the prior analysis concluded, the finding itself — never "as we discussed" or "the agent found".
- No agent dispatch section, slash-command prefix, paste-into-chat instruction, line addressed to Claude, `path:line` anchor framed as an order to an agent, or orchestration vocabulary (`/x`, `subagent`, `cookbook`, `verify gate`).
- No stub: a section is filled or omitted, never `[fill in later]`.
- An owner who fields follow-ups → close on a "Questions / contact" line; none → omit it.
- A `Last updated: <YYYY-MM-DD>` line near the top only where the content drifts with outside changes, a vendor's setup among them.
