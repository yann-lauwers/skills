# DM a workspace member

## Step 1 — Resolve the target user

1. Match the user's phrase to the roster in the config body, case-insensitively; "me" → the configured user.
2. User id not cached this session → `cookbook/resolve-identity.md`; cache `name → user_id` for the session.
3. A phrase no roster entry names, or one several could ("someone on the team") → ask the user to name the person.
4. Done when one user id is in hand.

## Step 2 — Open the DM channel

1. The configured user → `self_dm` · anyone else → `cookbook/resolve-identity.md` Step 3.
2. Done when a `D…` id is in hand.

## Step 3 — Read the recent exchange (continuity)

1. `conversations.history` on the DM channel, `limit: 8`, user token.
2. Classify the conversation:
   - Fresh → the channel is empty, or its last message is stale: nothing today, no active back-and-forth.
   - Continuing → a message from either party today or within the last few hours, or our own last message (`user` == the configured user's id) already opened with a greeting.
3. `ok: false` → Fresh; surface the `error` verbatim and never block the send on it.
4. Done when the conversation is classified Fresh or Continuing.

## Step 4 — Draft the message body

1. Read `references/drafting.md` first; plain text by default, in mrkdwn per its § Markup.
2. Address the recipient directly.
3. Write as the configured user, in the first person: no bot-attribution framing, no third-person attribution.
4. Language → `references/drafting.md § Which language`.
5. Register → the recipient's roster entry in the config body; no entry → the register of the exchange read in Step 3. Register and language are independent; both apply.
6. Fresh → open with a short greeting · Continuing → lead with the substance in the same register, no second greeting.
7. Weight → `references/drafting.md § Layout`.
8. Done when the body is drafted.

## Step 5 — Post directly (no confirmation gate)

- A DM posts at once, under the configured user's name, without confirmation; a channel post still gates (`cookbook/send-message.md § Step 3`).
- "show me first", "let me review", "draft only", "preview" → paste the draft and its target, and wait for `yes` / `go` / `send`.
- Otherwise → Step 6.

## Step 6 — Post via chat.postMessage

1. `channel` → the DM id from Step 2; POST under the user token (`secret`) per `references/api.md § Endpoint + auth`.
2. Capture the response per `SKILL.md § Rules`; `ok: true` → Step 7 · failure → surface `error` verbatim.

## Step 7 — Report back

1. One line → `DM'd <name> as you — "<first 60 chars>…" — ts:<ts>`; a self-DM → `DM'd you — "<first 60 chars>…" — ts:<ts>`.
2. The message asked something the current work is blocked on → continue into `cookbook/watch-reply.md` with this `ts` as `--after` and the sent text as the question.
3. Done when the line is printed and, where 2 applied, the watcher's task id beside it.
