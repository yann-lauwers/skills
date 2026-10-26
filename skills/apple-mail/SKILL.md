---
name: apple-mail
description: "Reads, lists, drafts and trashes mail through the Apple Mail app on this Mac, and searches its archive; a message is drafted, never sent. Use on 'check my email', 'did X email me', 'read that mail', 'draft a reply to', 'send an email to', 'search my mail', 'create a mail rule', 'change my signature', or a named address, sender or thread. Also fires before an `osascript` or JXA call targeting Mail, before reading `~/Library/Mail/`, before reaching mail through IMAP or a connector. Not for a team-chat message — the team chat's skill."
allowed-tools: Bash(${CLAUDE_SKILL_DIR}/scripts/*), Bash(osascript *)
---

# Apple Mail

- The scripts under `scripts/` drive Mail.app over AppleScript, reaching every account signed in there with no credential.
- Each script the routing table names prints JSON on stdout — except `mail-draft.sh`, which prints `drafted` — a diagnostic on stderr, exits non-zero on failure, and lists its arguments under `--help`; the rest of `scripts/` are helpers those scripts call.
- Pass `--account` and `--mailbox` when known, and ask for the smallest `--limit`.
- A message id is per-mailbox and changes when the message moves → read it and act on it in one breath, never store it.

## The one thing this skill will not do

**A message is drafted and left for Yann. It is never sent.**

- Never reach Mail's `send` verb: `mail-draft.sh` has no send path, and `osascript` around it is the same act by another route.
- "Send an email to X" → compose it and say it is waiting in Mail.
- The draft opens in a Mail window with recipients, subject, body and attachments filled in; it leaves the machine when Yann clicks Send.

## Routing table

| Intent | Read |
| --- | --- |
| IF listing which accounts and addresses exist | THEN `scripts/mail-accounts.sh` |
| IF listing what arrived, what is unread, or finding a message's id | THEN `scripts/mail-list.sh --help` |
| IF reading the full text of one message | THEN `scripts/mail-read.sh --help` |
| IF composing a new message, a reply, or a forward | THEN `references/drafting.md` first, then `scripts/mail-draft.sh --help` |
| IF moving a message to trash, or removing a draft | THEN `scripts/mail-trash.sh --help`; a draft whose compose window is still open in Mail is left alone — `references/drafting.md` § Open drafts |
| IF searching any mail, by sender, date or text | THEN `scripts/mail-search.sh --help` |
| IF the answer depends on what arrived in the last minutes, or a mail is about to be reported absent | THEN `scripts/mail-refresh.sh` first, then search again with two or three other terms |
| IF a script reports a permission, a missing window, or `Operation not permitted` | THEN `references/permissions.md` |
| IF a rule, a signature, a mailbox or an account has to be created or changed, or anything else no script covers | THEN `references/bridge-traps.md` |
| IF the request matches none of the above | THEN `references/bridge-traps.md`, say which row was closest |

## Done when

- The request's script exited zero and its output answered the question; for a draft, `mail-draft.sh` printed `drafted`, the reply names the window waiting in Mail, and nothing in the session called `send`.
- A reference row → that reference's own done line holds.
