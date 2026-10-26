# Watch a conversation for a reply

- `scripts/watch-reply.py` emits a line only for a reply the session must act on; acknowledgements and unrelated chatter wake nobody.
- The watcher is a probe armed per /watching : it exits on its first line, and the session re-arms it when the line asks for it.

## Step 1 — Resolve the conversation and the question

1. Channel id → the DM channel from `cookbook/dm-user.md` Step 2 (`D…`), or a channel id (`C…` / `G…`) resolved per `cookbook/read-channel.md` Step 1; a thread → also its parent `ts` for `--thread`.
2. `--after` → the `ts` `chat.postMessage` returned for the message that asked; sent in an earlier session → read it back with `conversations.history` and take its `ts`; nothing sent yet → omit it, and the watcher starts from now.
3. `--from` → the watched person's user id from the roster in the config body; omitted → anyone but the configured user counts; the configured user's own id is the one way their messages count, which is how a self-DM test runs.
4. `--question` → the ask's text, written to a scratchpad file and passed as `@<path>`; several messages made the ask → concatenate them; omitted → no classifier, and every watched message wakes the session.
5. Done when channel, after-ts, from-id and question path are printed in the start banner.

## Step 2 — Read it once

1. Run `keyless run -s SLACK_TOKEN=<NAME> -- ${CLAUDE_SKILL_DIR}/scripts/watch-reply.py --channel <D…> --after <ts> --from <U…> --question @<path> --once`; `<NAME>` → the token that sent the question.
2. `ANSWERED` / `QUESTION_BACK` / `NEW_MESSAGE` → the reply is already there: act on it per the verdict table and stop.
3. `WATCHER_ERROR` with `error=auth` → the token did not reach the script, the vault-scoped session is locked or dead: route to the skill holding `role: secrets` and stop; never arm a watcher with no token.
4. A `--once` read takes no lock and starts nothing, so it is safe against a conversation another watcher already holds.
5. Done when the once-line is `WAITING`.

## Step 3 — Arm the watcher

1. Call Bash with `run_in_background: true`, `description: "Slack reply from <name>"` and this command, which is the whole of arming it:

```sh
keyless run -s SLACK_TOKEN=<NAME> -- \
  ${CLAUDE_SKILL_DIR}/scripts/watch-reply.py --channel <D…> --after <ts> --from <U…> --question @<path>
```

2. Watcher tuning flags go after the script, and only when the user set them → `--interval` (120 s) · `--nudge-after` (4 h) · `--blind-after` (3600 s) · `--model` · `--no-classify`.
3. Record in the start banner: who is watched, the task id, "silent until a reply that needs you".
4. The probe prints nothing until a reply needs the session; the next line wakes it, and the verdict is the last `{` line of the task's output file.
5. Done when the task id is printed and the turn has ended; nothing polls from this side.

- `keyless run` reads the item once and leaves the value in the watcher's environment for the watch's whole life; the vault must be readable when the watcher starts.
- A launch failing on auth → report it, never retry it blind; the vault is the user's to unlock.
- A watch dies with its session → the closing line or handoff carries the arm command.

## Step 4 — Act on each line

- Every line is one JSON object: `verdict` picks the row; `text`, `from`, `permalink` carry the reply; `reason` is the classifier's one-line summary.
- A verdict that reads wrong against the raw `text` → act on the text.

| Verdict | Action |
| --- | --- |
| `ANSWERED` | The watcher has exited. Read `text`; carry the answer into the work that was blocked on it. Post a follow-up DM only when the work needs one. |
| `QUESTION_BACK` | The watcher has exited. Answer it: draft per `cookbook/dm-user.md` (continuing conversation, no greeting), send, then arm a new watch from Step 1 with the new message's `ts` as `--after`. |
| `NEW_MESSAGE` | The watcher has exited without a classifier verdict (`classifier_error` says why, or none was requested). Read `text` and judge it yourself; arm a new watch if it was an ack. |
| `STALE` | No reply for `--nudge-after`; the watcher has exited. Read the watched person's roster entry in the config body first: a standing rule there barring nudges → report the staleness to the user, send nothing, and re-arm with the line's `rearm` (`--after <last_ts> --nudge-after 0`) replacing their namesakes. No such rule → post `up` followed by `question_permalink` on its own line, per the register's nudge shape, then re-arm with `--after <the nudge's ts>`. |
| `WATCHER_ERROR` | `error=auth` or `channel_not_found` → the watcher has exited; report `detail`. Auth routes to the skill holding `role: secrets`; a retry from here reads the same locked store. `error=blind` → no read landed for the whole blind window: report it and arm a fresh watch from Step 1. `error=duplicate` → another watcher holds this conversation; report it and leave that one in place. Any other → report `detail`; the watcher has exited. |
| anything else | Report the raw line and stop. Never infer an action from an unknown verdict. |

1. Parse the last `{` line, look up `verdict`, carry out the row.
2. Every verdict ends the run; watching again is a fresh arm, with `rearm` where the line carries it and Step 1 otherwise.
3. A rate limit or a failed read prints nothing; only `blind` reports a watch that cannot read.
4. An exit with no `{` line → re-arm once with the same command; a second time → report the output file's tail.
5. Done when the row has been carried out and the turn ended.

## Step 5 — End it, or watch again

1. The user no longer wants the watch → `TaskStop <task id>`.
2. A verdict ended the run on its own → nothing to stop; the next question is a fresh Step 1.
3. Done when `TaskStop` has answered, or a fresh arm has been printed.
