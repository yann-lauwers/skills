---
name: voice
description: "How Yann sounds to someone he's addressing. Use before drafting a message written to a person: a Slack DM or channel post, an email, a reply in someone's thread."
---

# Voice

## Voice — the invariants

- The point arrives in the first words: no preamble, no meta-framing — no "petit heads-up", no "pour info".
- `Je me permets de` → only on a chase; anywhere else it is preamble.
- Each idea once: the request, plus at most one clause justifying it.
- A reply carries only what settles the question: drop every line the question does not reach, however true.
- A second subject → a second message, even when the two arose together.
- No scaffolding: never the arc opener → context → request → thanks; never a bold label or heading inside a short message.
- Chat → no blank line after the greeting · email → always one.
- Never a bare "Merci" as a whole closing paragraph; above an email signature it stands.
- Correct accents and apostrophes in every register: a decision overriding his habit, which leaves them off 69% of his own Slack messages.
- Reproduce what is typed on purpose, fix what slipped: `thxxxx`, `jsp`, `okok`, a bare fragment, a missing greeting, a message ending on a question survive; `actuelleemnt`, `j'avias po vu`, `normaelment` get corrected.
- No em dashes: use "..", "...", a comma, or a line break.
- A message needing an answer ends on its question, or on the reward the register supplies (`ca serait top`, `trop top!`); never on a softener, never `🙏` / `:pray:`.

## Register — three levels

- Register follows the person, never the medium; never put a register block in a channel's config.
- `familiar` — friends, partner, family, close colleagues → `references/familiar.md`.
- `professional-friendly` — work peers seen daily, tutoiement → `references/professional-friendly.md`.
- `cordial` — people not known well, and professional contacts, in three levels → `references/cordial.md`.
- A chase, a complaint, bad news, or an error of Yann's own → `references/conflict.md` too.

## Composing an outbound message — the order of resolution

Resolve five things, in this order, before drafting; an existing thread outranks a stored register or a stored identity.

1. Recipient — an entity's `entities/<entity>/contacts.json` in the personal-ops repo (a personal contact: the person entity's own), or a project roster in that tool's config. Unreadable → say so and fall through to the thread.
   - The register is the addressee's, never everyone copied: one name in To → that recipient · several in To → whoever the message opens by addressing · no individual addressee → the collective forms the channel supplies.
   - Addressee not obvious → say which one was resolved and why, before the message goes out.
2. Register — a live thread's recent messages outrank the stored level; a disagreement → mention the stale record. No thread, or a stale one → the level the relationship record names. Neither → `cordial-formel`, said as an assumption.
3. Shared context — what the recipient already holds, per their relationship record, is never explained back.
4. Channel shape — email: the mail skill's `references/email.md` · a channel with its own skill: there. Neither readable → derive it from the thread and say so.
5. Sender identity — resolved from the recipient, never from the account a mail tool opened first; the mail skill's drafting reference maps the addresses. A reply → the thread's identity. Neither resolves → say which identity is assumed and why.

Whatever channel carries it:

- Never cite a local path; short content goes inline, longer as an attachment.
- Signed as the sender, first person; no third-person or tool-attribution framing.
- The recipient's language, from their own record; nothing answers → ask.
- An external artifact — a pull request, a ticket, a document, a build → its canonical URL plus a short summary.
- Emoji → only in chat (messaging apps, Slack), only where the register has one, never in a squarely professional setting.
- Sending → the channel's own skill; none → hand the draft back and say so.
- The `agréer` family → only for a recipient or procedure that demands it (the mail skill's `references/email.md` § The `agréer` family); a formal demand → the Belgian administrative-document skill.

## Keeping this file true

Adding a finding, re-measuring a line, dating a claim, or telling Yann's own messages from drafted ones → `references/maintaining.md`.
