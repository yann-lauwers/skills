---
name: close-session
description: "Close this session's seat once its work has left it — preloaded status, then cmux self-close."
disable-model-invocation: true
allowed-tools: Bash(~/.claude/skills/cmux/scripts/close-status.sh:*), Bash(~/.claude/skills/cmux/scripts/self-close.sh:*), Bash(git:*), Bash(gh:*)
argument-hint: [reason | force | keep]
---

# /close-session

The seat's state is already below — the script ran before you read this line. Decide on it; do
not re-derive it with more commands.

```!
~/.claude/skills/cmux/scripts/close-status.sh
```

## Decide

1. **`BLOCKERS none`** → arm the close with the `CLOSE` line the script printed, writing a real
   `--reason` (what the seat finished). Report the ref and the delay in one line, then stop.
2. **Blockers listed** → say what each one is and stop. They name work that would be lost or
   orphaned, and each has an owner: uncommitted files get committed, an unpushed branch gets
   pushed, an open PR gets watched to merge. Do that work if the session's own task covers it;
   otherwise hand the list back.
3. **`SEAT unknown` or `not in a cmux workspace`** → close nothing, say which of the two it is.
   An unresolved ref and somebody else's seat are indistinguishable from here.

`$ARGUMENTS`:
- `force` — arm the close despite blockers. The user has taken the loss; name what is being
  abandoned in the reply anyway.
- `keep` — report the status and arm nothing.
- anything else — the `--reason` text, verbatim.

## What this does not check

The script reads the seat, the repo under it, and the PR on its branch. What it cannot see is
whether the *work* is done: a ticket left un-updated, a finding left out of the reply, a report still in
the reply. Judge that from this conversation before arming — a clean tree is not a finished
ticket.

ARGUMENTS: $ARGUMENTS
