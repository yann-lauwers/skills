# Maintaining the voice file

## Where a new finding goes

- A measured tell resolves to exactly one home, by the scope it holds at, never where it was observed:

| The finding holds | Home |
|---|---|
| whoever reads it, whatever the medium | a **Voice invariant** |
| for one register, whoever the reader | that **register's** own bullets |
| for one person | their **relationship record** |
| for one medium | that **channel's** shape file |

- Place it on the bullet already owning its subject; a finding with no owning bullet earns a new one; never a second entry elsewhere.
- Holding across several registers but not all → write it in the register where it was measured, and the inheriting register says so once; never state it twice.
- A per-person delta → an exception on that person's `register` field, in the shape the personal-ops contacts rule defines; never prose in their record, never a register, never a new bullet here.
- `(0/n)` after a ban — measured at zero in his own messages against n in his assistant's: a construction only the drafting produces, the strongest form a ban takes here; a plain ban with no numbers is a directive.

## When a re-measure contradicts a written line

- One test decides the outcome — is the new measurement clean?

| | Outcome |
|---|---|
| The measurement is contaminated by drafted messages | The written line **stands**. Record the contamination beside the filter it defeats, so the next pass does not re-derive the same wrong number. |
| The measurement is clean and the written line was built on contaminated data | The line is **replaced**, not qualified. |
| The measurement is clean and Yann prefers the written line anyway | The line **stands, marked as a decision**, naming the number it overrides. |

- Never blend: a line narrowed by the measurement it survived, or kept as a qualifier on its replacement, carries the superseded version forward under the new name.

## What a claim carries, so staleness is readable

- Every number here states the corpus it came from and its size.
- A new claim arrives with its corpus and size, or is marked as unmeasured.
- A re-measure updates the corpus line in the same edit as the number.

## Separating Yann's messages from drafted ones

- Reaching the Slack corpus → the claude.ai connector's `mcp__claude_ai_Slack__slack_search_public_and_private`, which authenticates as Yann (`U09G0FDNUET`) and searches every channel plus his DMs: query `from:<@U09G0FDNUET> before:YYYY-MM-DD`, 20 results a page, paginating on `cursor`; the Nexus bot token cannot, lacking `search:read.public`.
- Exclude the self-DM: it carries automated price-watch notifications and nothing he wrote.
- The assistant writes under Yann's own accounts, so every raw corpus mixes his messages with drafted ones; on Slack the drafted ones start 2026-06-18 and run continuously, so a date cut cannot separate them.
- Filter every corpus, email included, on the em dash: zero in his hand-typed messages, near-universal in the drafted set — a punctuation filter, so it leaves the length findings untouched.
- `:pray:` — the second signature, which bleeds back: his own uses appear only from 2026-07, after the assistant had closed asks with it for weeks; date-filter it before counting, and read a low non-zero count as contamination, never as a tail.
- Per-axis numbers, method and verbatim examples → the vault notes `professional-friendly-register-measured-against-slack-sent-history` (Slack) and `cordial-register-body-measured-against-sent-email-corpus` (email).
- Still unmeasured: the very formal opening (one instance), the `agréer` family (zero, consistent with it not being his habit), a group addressee (none in the corpus), and cordial mail from the Nexus work address (zero sent messages — every email measured is the iCloud account).
