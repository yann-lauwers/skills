---
name: plain
description: >-
  Re-explains the previous assistant message in plain language, visual first. Use when the user
  types '/plain ', says 'say that again simply' or 'plain english please', or signals the last reply
  was too dense. Not for drawing something the last reply did not explain.
---

# Plain

Re-explain the assistant's own previous message for a reader holding none of its vocabulary, none of its prior context, and a short attention span.

## Steps

1. **Draw it first.** The picture comes before any prose, in the form `AGENTS.md` § Shape's show-first list picks; it carries the structure, the prose below it the rest. A message whose structure is one fact takes no picture.
2. **Re-explain, never re-answer.** The content is fixed — no new claims, no new questions, no tool calls, no work picked up.
3. **Facts survive verbatim.** Every path, command, file name, number, URL, identifier, and decision stays exactly as it was. Simplify around the facts.
4. **Simpler, not shorter.** The target is "impossible to misunderstand" — a longer re-explanation that lands beats a tighter one that does not.
5. **Plain words.** A technical term the reader needs again rides once in parentheses after its plain meaning — "the program that starts the app (the bootstrapper)", in that order.
6. **A second /plain restarts from a different case.** The wording that failed is not re-worded; the form and the example both change.
7. **The user's language.** French in, French out — labels inside the visual included.

## Scope

This skill owns the plainness — which words, which example, how much is spelled out.

A /plain turn stays a re-explanation turn, whatever the previous message left unfinished — the next user turn resumes the work. No previous assistant message to simplify → say so in one line.
