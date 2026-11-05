---
name: voice
description: "How Yann sounds in a message a person receives. Use before drafting any message, comment, PR body or email another person reads, where no channel skill owns the wording."
---

# Voice & Register

- Voice — the invariants, true in every message whoever reads it.
- Register — social distance, three named levels.
- Relationship — per person: which register, plus what they already know.
- Channel — what the medium imposes on shape, never on register.
- A drafted message is Voice ∘ Register ∘ Channel, with Relationship choosing the register and naming what to leave out; each of the four has one home, § Where each piece lives.

## Voice — the invariants

- The point arrives in the first words: no preamble, no meta-framing — no "petit heads-up", no "pour info".
- `Je me permets de` — his own softener for a second approach: it stands on a chase; anywhere else it is preamble and goes.
- Each idea is said once: the request, plus at most one clause justifying it; never a second sentence restating the first differently.
- The message stops when it is understood.
- A reply carries what settles the question and nothing else it happens to know: drop every line the question does not reach, however true, recent or close to the same file.
- A second subject is a second message, with its own subject line, whenever the two arose together.
- Before a draft goes → cut every unasked line and every second subject, even where every sentence in it is true.
- No scaffolding: never the arc opener → context → request → thanks; never a bold label or heading inside a short message.
- Chat → no blank line after the greeting · email → always one.
- Never a bare "Merci" as the whole of a closing paragraph; as an email sign-off above the signature it is a closing formula, and stands.
- Verbatim stays verbatim, in its own language: PR titles, ticket IDs, code, error messages, URLs, amounts, legal references pass through unchanged, never reworded to fit a register.
- Correct accents and apostrophes in every register: a missing accent is a slip — a decision overriding his habit, which leaves them off 69% of his own Slack messages; a re-measure never softens this line to match the figure.
- Reproduce what is typed on purpose, fix what slipped: `thxxxx`, `jsp`, `okok`, a bare fragment, a missing greeting, a message ending on a question survive; `actuelleemnt`, `j'avias po vu`, `normaelment` get corrected; structure is never an error.
- No em dashes: use "..", "...", a comma, or a line break.
- Never `🙏` / `:pray:`: an ask closes on its own question, or on the reward the register supplies (`ca serait top`, `trop top!`); where an emoji belongs, the register's own set has one.
- A message needing an answer ends on the question, never on a softener.

## Register — three levels

- Register follows social distance, never the medium: one channel carries different registers to different people, and one person keeps their register across channels.
- `familiar` — friends, partner, family, close colleagues → read `references/familiar.md`.
- `professional-friendly` — work peers seen daily, tutoiement → read `references/professional-friendly.md`.
- `cordial` — people not known well, and professional contacts, in three levels → read `references/cordial.md`.
- A chase, a complaint, bad news, or an error of Yann's own → read `references/conflict.md` too.

## Composing an outbound message — the order of resolution

Resolve five things, in this order, before drafting; an existing thread outranks a stored register or a stored identity.

1. Recipient — who receives it: an entity's `entities/<entity>/contacts.json` in the personal-ops repo (a personal contact: the person entity's own), or a project roster in that tool's config. Unreadable → say the roster was unreachable and fall through to the thread.
   - The register belongs to the person spoken to, never to everyone copied: one name in To, others in copy → the To recipient · several in To → whoever the message opens by addressing · a group with no individual addressee → the collective forms, which the channel supplies.
   - The addressee changes mid-thread while the correspondent stays → a reply saying the file now sits with a team is answered to that team, opening on the collective form; the correspondent's stored level stays where it was.
   - An addressee not obvious → say which one was resolved and why, before the message goes out.
2. Register — the recent messages of a live thread show the register in play and outrank the stored one; a disagreement makes the stored record stale enough to mention. No thread, or a stale one → the level the relationship record names. Neither → `cordial-formel`, said plainly as an assumption.
3. Shared context — what the recipient already holds, named by their relationship record, so it is never explained back: someone holding the file gets the question and stops there, never their own client's identity or the reasoning behind a number they produced.
4. Channel shape — subject line, salutation, sign-off, one document or a run of short messages, attachment list, a greeting repeated mid-thread: email's in the mail skill's `references/email.md`, a channel with its own skill carries it there. Neither readable → derive the shape from the thread and say so.
5. Sender identity — which of Yann's own addresses or handles it goes out as, resolved from the recipient, never from the account a mail tool opened first; the mail skill's drafting reference carries the address mapping. A reply goes out as the identity the thread already used. Neither resolves → say which identity is assumed and why the recipient implies it.

Whatever channel carries it:

- Never cite a local path — a reports directory, a vault path, a file on this machine, a workspace artifact; short content goes inline, content too long to inline as an attachment.
- It goes out signed as the sender, in the first person and the sender's own voice; no third-person or tool-attribution framing.
- Match the recipient's language, resolved from their own record; nothing answers → ask; never draft in a language nobody chose.
- An external artifact — a pull request, a ticket, a document, a build — goes out as its canonical URL plus a short summary, never inlined.
- Emoji → only in chat (messaging apps and Slack) and only where the register has one; email carries none at any level (the mail skill's `references/email.md` § No emoji), nor does a message whose setting is squarely professional.
- A channel never decides register; never put a register block in a channel's config — it is unreachable once the same person is addressed through another medium.
- This file governs how a message is written and which identity it goes out as; whether it leaves the machine, and what carries it → the channel's own skill; no channel skill carries it → hand the draft back and say so.

## Where each piece lives

| Piece | Home |
|---|---|
| Voice, this composition rule | this file |
| Each register's measured shape | `references/<register>.md` |
| Who a person is, their register, what they know | `entities/<entity>/contacts.json` in the personal-ops repo, shaped by its `.claude/rules/contacts.md`; work rosters stay in their project's config |
| Channel shape | that channel's own skill (email: the mail skill's `references/email.md`; Slack's lives in its skill) |

## Undefined — do not improvise this

- A case named here → say so and hand the draft over; never invent a rule.
- A formula above Yann's observed range, the institutional `agréer` family → a deliberate act for a recipient or a procedure that demands it, never a default (the mail skill's `references/email.md` § The `agréer` family); a formal demand routes to the Belgian administrative-document skill instead.

## Keeping this file true

Adding a finding, re-measuring a line, dating a claim, or telling Yann's own messages from drafted ones → `references/maintaining.md`.
