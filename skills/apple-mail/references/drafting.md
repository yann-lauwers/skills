# Drafting: what is resolved before `mail-draft.sh` runs, and what the draft path trips on

- Before calling `mail-draft.sh`, resolve who receives it, the register they are addressed in, what they already know and the shape the channel imposes from /voice, loaded whole — its § Composing an outbound message; unavailable → say so, and match the voice of the thread's recent messages.
- Before calling it, resolve `--from` per § Sender.

## Sender

- `--from` follows from the recipient, never from the account order or the mailbox the thread was read out of; always pass it — without it, Mail picks its default account.
- Two addresses send: `yann@gpt.nexus` → a Nexus colleague, or anyone about Nexus work · `yann.lauwers@icloud.com` → everyone else, every company matter included (the accountant, the bank, the insurer, the notary), and whenever "my email" is unqualified.
- A thread already under way → the address it used, over both.
- Every other account Mail holds is a mailbox Yann reads, never a sender; `yann1@gpt.nexus` is a Claude subscription account, never offered as an address to reach Yann.

## What the draft path holds

Every line holds for `mail-draft.sh`; a change to it keeps each one.

- Attach a file through an HFS alias — `"Macintosh HD:Users:…" as alias` — never `POSIX file "/path"`, which Mail accepts while attaching nothing; verify by counting `attachments of content of msg`, never assume.
- Paste a body into the compose window, never assign it to `content`: on a reply or a forward `content` holds the quoted original as one field, writing it replaces the quote, and reading it answers `""` on a fresh reply, so it cannot be read, amended and written back.
- The paste goes through the pasteboard and ⌘V, leaving Mail's attribution line, quote bar, formatting and inline images standing underneath.
- Find the compose window by a nonce stamped into its `subject`, never by focus: raise the window carrying that title, paste, then put the real subject back.
- The pasteboard carries an HTML flavour beside the plain-text one: `- ` at a line's start becomes `<li>`, and the HTML names no font, so Mail applies the compose default; `--html-file` overrides the rendering.
- After the paste, read the top of the composed body back, retry up to three times, and restore the previous clipboard when done.
- The read-back compares the first composed line with the first line sent, never the body as a whole.
- Mail autosaves an open compose window to Drafts every few seconds, so a window still wearing the nonce leaves a draft titled `mail-draft-<pid>-<n>` that restoring the subject never renames → sweep the nonce-titled drafts at the end and on every early exit.
- The sweep runs only after the live window has autosaved under its real subject, so only nonce-titled copies match.
- A draft reference can go stale mid-sweep (`Can't get object (-1728)`), cause unconfirmed → collect ids first and re-fetch each before moving it, skipping a stale one, as `sweep-drafts.js` does.

## Open drafts

- Never trash the saved copy of a draft whose compose window is still open, `mail-draft.sh`'s sweep of the nonce-titled copies it made aside: that draft is Yann's to send or discard in Mail.
- A test that plants drafts with `save` → remove each planted message with `delete outgoing message i` before trashing its draft; `close … saving no` returns without error and closes nothing.

## Done when

The recipient and register came from /voice 's resolution order and `--from` from § Sender,
`mail-draft.sh` printed `drafted`, and no saved copy of a draft whose compose window is still
open was moved.
