---
name: relogin
description: >-
  Re-logs a Claude Code account that cswap shows dead and re-registers its slot, so sessions can be
  seated on it again. Use on "relogin that account", "re-auth this account", "that account is dead",
  "cswap says relogin needed", or a named cswap account that stopped working; fires on `cswap list`
  showing `relogin_required` (or CodexBar flagging one) held fifteen minutes unbroken. An
  `unavailable` account is not a dead login and is left alone. Not for signing an account into
  claude.ai for anything other than a cswap credential — /claude-login .
---

# relogin

- The browser half → /claude-login ; this pass owns the cswap snapshot, `claude auth login` held on a pty, the capture, the restore and the verify.

| IF | THEN read |
| --- | --- |
| a slot looks dead and the question is whether to run | § When it runs |
| running the relogin | § Run it, then § Validate, then record |
| the run stopped instead of finishing | `references/stops.md` |
| the watcher — its verdicts, its backstop, a tick to run or read | `references/watcher.md` |
| anything else | § When it runs, then § Run it; none fits → name the closest row |

## When it runs

- Run it → `relogin_required` has read on that slot for fifteen minutes unbroken — `credential-watch status` shows the slot under `waiting` with `since` 15+ min back (`references/watcher.md`).
- A fresh `relogin_required` alone → wait; it can be a stale copy of a login a running session still holds, which cswap heals on its next save of that login.
- `unavailable` → leave it: the usage endpoint answered 429 (`per-token usage budget reached` in `~/.claude-swap-backup/claude-swap.log`), cswap is backing off, and the reading returns within the hour.
- `unavailable` again right after its reset → a live seat elsewhere polls that token: name it to Yann, never wait again.
- Read `usageStatus` from `cswap list --json`, never CodexBar's icon, which paints both states the same.
- A session whose reply Yann reads → run it on the trigger unasked, saying first that the global account moves for about a minute.
- A seat he is not reading (a detached session) → leave the run to the watcher.
- One account at a time, in series → run one, validate it, record it, then start the next; never two in parallel or in a batch, since each run repoints the global cswap account.

## Run it

```
python3 ~/.local/share/cswap-relogin/oauth.py --email <account>
```

- `--org <org>` → picks the organization for a multi-org account · `--dry-run` → prints the plan.
- The account's mailbox and org come from the manifest /claude-login owns.
- The manifest marks the account `sso` → the tool refuses; sign it in by the by-hand line it prints.
- In scope → any account whose login mail reaches Apple Mail; login mail absent from Apple Mail → out of scope, sign it in by hand.
- `auto.py` in the same package → a one-year setup-token that makes model requests and reports no usage: right for an account that only runs Claude Code, wrong for one the ranker seats.

## Validate, then record

1. Never report success on the tool's word; read both facts:
   ```
   cswap list --json | jq '.accounts[] | select(.email=="<account>") | {number,usageStatus}'
   cswap-laxity rank --json | jq '.rows[] | select(.email=="<account>") | {account,servable}'
   ```
2. `usageStatus: "ok"` and `servable: true` → done; anything else → not relogged, report both readings.
3. Remove any older dead slot for the same email: `cswap remove <n>`, which prompts for `y`.
4. Set that account's `"verified"` in the manifest to today's date.

- An account never run before → `discover.py --email <account> --write` in the same package fills `orgs_seen` / `method_confirmed`, without touching cswap.
