---
name: enable-banking
description: "Operates the Enable Banking PSD2 account-information API for a resolved entity — reading a bank account's transactions and balances. Use on 'enable banking', 'open banking', 'PSD2', 'the consent expired', linking a bank account, refreshing a statement, or a fetch returning fewer transactions than expected. Also fires on a call to `api.enablebanking.com`, a JWT being signed for one, and an application, key pair or whitelist being registered. Not for where a fetched statement goes — the repo's own finance pipeline."
---

# enable-banking

## Project config

- Config: the repo's `docs/agents/integrations/enable-banking.md` over the floor, read merged: `~/.claude/skills/agents-config/scripts/agents-config get enable-banking <key> --root "$CLAUDE_PROJECT_DIR"`, and its body: which accounts are targets.
- No `docs/agents/integrations/enable-banking.md` in the repo → ask the user; on their yes, write it per /managing-harness , `references/skills.md` § A tool's skill and its config, asking for the register block and the target accounts, never guessing them; then continue.

| Key | What it answers |
| --- | --- |
| `register` | `block` — where the resolved entity's register file keeps this tool's block |
| `production` | `restricted` → the production application reaches only the accounts whitelisted in the Control Panel |
| `payment_initiation` | whether the production application registers payment initiation |

## Resolve the entity before the first call

- Read the resolved entity's register file at `register.block`: application id per environment, the ASPSP each account is linked at, the account keys those links feed.
- The secrets-store item is read, never derived: `applications.<env>.secret` in that block.
- No such block → ask which holder; never fall back to another entity's application.

## Payment initiation

- `payment_initiation` not `true` → no call moves money, and a payment request is refused.

## Calls that change state

- `POST /auth` and `DELETE /sessions/{id}` → put to the user first, naming the entity.

## What the sandbox proves

- A shape read from the provider's reference is a draft: a call that disagrees wins, and the file is corrected that turn.
- The sandbox's mock bank imposes no consent ceiling, no daily AIS cap and no history collapse → a sandbox pass proves none of them.

## Routing

- Read the row's file, then every file it cites for the step in hand, before any other tool call.

| If the task is | Read |
| --- | --- |
| registering the application, generating its key pair, whitelisting an account, or putting the key in the secrets store | `references/setup.md` |
| linking an account, re-linking one whose authorisation expired, or reading what a link returned | `references/authorisation.md` |
| calling an endpoint, signing a request, paging a response, or reading an error | `references/api.md` |
| a fetch that returned fewer transactions than expected, or a history that stops short | `references/api.md` § The two limits |
| any surface no row names | `references/api.md` — probe the path against the live application before calling it unavailable |
