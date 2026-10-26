# Upload a file to a message or DM

Attaches a doc, snippet, log or export to a Slack conversation: reserve a slot, POST the bytes, then complete and share with the message text, so one message carries both.

## Step 1 — Confirm upload is the right shape

1. Classify the content:
   - short and self-contained, a few paragraphs → copy it inline through `cookbook/dm-user.md` or `cookbook/send-message.md` and stop here;
   - hosted externally (a PR, a ticket, a dashboard, a published doc) → post its canonical URL with a one-line summary and stop here;
   - local-only and long (a writeup, a log, an export, a table over the Block Kit `table` limits — `references/api.md § Table block`) → upload it; continue.
2. Done when the content sits in exactly one bucket and the two non-upload buckets have routed away.

## Step 2 — Resolve the destination + gate

0. The request pointed at a conversation per `references/reply-in-place.md`, with no other destination named → its channel and `thread_ts` per its § Read before drafting; no gate runs.
1. Author → the user token by default · the bot token (`bot_secret`) where the config body's bot line allows it; Steps 4, 6 and 7 run under the token chosen here.
2. A DM target → the bot writing to the configured user: the config's `bot_dm` · else the user and DM channel per `cookbook/resolve-identity.md`; cache `user_id → D…`.
3. A channel target → its id per `cookbook/read-channel.md` Step 1.
4. A file shared into a channel the request did not point at is a channel post → `AskUserQuestion` first, with the channel, the filename and the `initial_comment` preview (`SKILL.md § Rules`); a DM posts at once.
5. Done when a `D…` / `C…` / `G…` id and the author are in hand, and a channel destination the request did not point at carries an explicit confirmation.

## Step 3 — Prepare the file

1. Read the file end to end before uploading it, whoever wrote it and however the user described it.
2. Strip or rewrite what the recipient cannot act on — local-only wikilinks, reports they cannot open, another project's identifiers, machine-local paths, personal tooling; a purpose-built standalone copy beats the working artifact.
3. Scan every line for a token, key or credential.
4. Draft in the recipient's language per `references/drafting.md`; code, commands, paths and error strings stay verbatim.
5. Record the byte length → `wc -c < <path>`.
6. Done when the whole file was read, the byte count captured, and the credential scan covered every line.

## Step 4 — Reserve the upload slot

1. POST `files.getUploadURLExternal` with `filename` and `length` (the exact byte count from Step 3); `snippet_type` for a text snippet → `references/api.md § File upload`.
2. Auth → Step 2's author, through `references/api.md § Endpoint + auth`; confirm `files:write` on that token.
3. Capture the response to a variable and read `ok` off it before using anything (`SKILL.md § Rules`).
4. Done when `ok: true`, with `upload_url` and `file_id` both captured; `ok: false` → surface `error` verbatim and stop.

## Step 5 — POST the bytes

1. `curl -sS -X POST "$UPLOAD_URL" -F "file=@<path>" -o /dev/null -w '%{http_code}'`.
2. No JSON comes back; HTTP 200 is success.
3. Done when the status is 200; anything else → surface it and stop, leaving the Step 4 slot unused.

## Step 6 — Complete the upload and share it

1. POST `files.completeUploadExternal` with `files: [{id, title}]`, the destination as `channel_id`, and the message text as `initial_comment`, plus Step 2's `thread_ts` where it set one; one call makes one message with text and attachment, never a separate `chat.postMessage`.
2. Build the payload with `jq -nc`, the message body passed through `--rawfile` so newlines and non-ASCII survive.
3. Capture the response, print `{ok, error}` raw, read the verdict off the variable (`SKILL.md § Rules`); keep stderr attached.
4. `ok: false` → surface `error` verbatim and retry this step with the SAME `file_id`; re-running Steps 4–5 uploads a second copy.
5. Done when `ok: true` returns for this `file_id`, or the error was surfaced to the user.

## Step 7 — Confirm what landed

- An unreadable or errored Step 6 response leaves the outcome unknown, not failed (`SKILL.md § Rules`); the share may already have posted.

1. Read `conversations.replies` on Step 2's `thread_ts` where it set one, else `conversations.history` (`limit: 3`), for the message carrying the attachment.
2. Absent → retry Step 6 with the same `file_id` · present once → done · present twice → tell the user and offer `chat.delete` on the duplicate's `ts`.
3. Done when the destination holds exactly one message bearing this file.

## Step 8 — Report back

- One line → `Sent <name> as <you | the bot> — "<first 60 chars of comment>…" + <filename> — ts:<ts>`.
