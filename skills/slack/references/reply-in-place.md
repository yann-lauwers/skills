# Where the reply lands

- The conversation the request points at — a pasted permalink, a thread, a channel named in passing, a message quoted back — is the destination; a pointed-at message inside a thread → reply into that thread.
- Pointing is the authorisation the channel-post gate would have raised → spend no `AskUserQuestion` on the destination.
- An explicitly named target outranks the link — "en DM", "en privé", "poste dans #X", "réponds-moi"; only an explicit one does, and the link then supplies only the context to read first.
- A recipient named without a named target ("a thank-you message to Nab") → a threaded reply in the pointed-at conversation, never a DM, and no question about which.

## Read before drafting

- Decode `…/archives/<CHANNEL>/p<DIGITS>` → that `channel` plus a `ts`: insert a `.` before the last six digits of `<DIGITS>`, so `p1788781001227629` is `1788781001.227629`.
- A thread parent → `conversations.replies` · a standalone message → `conversations.history` around it.
- The reply continues what is there, never restates it.
- `thread_ts` on the send → the parent's own `thread_ts` where the pointed-at message is itself a reply · its `ts` where it is the parent.
- `ok: false` on that read → surface `error` verbatim and stop; the remedy is `references/api.md § Error handling`, the `not_in_channel` line; nothing is drafted against a conversation that could not be read.

## What is still asked

- An occasion, a premise or a fact only the user holds → ask once, alongside the draft.
- Where the message goes never appears in that question.
- Then → a file → `cookbook/upload-file.md`, whose Step 2 case 0 takes the decoded destination · otherwise `cookbook/send-message.md`: its Step 1 case 0 takes the decoded destination, and its Step 3 gate does not run.
