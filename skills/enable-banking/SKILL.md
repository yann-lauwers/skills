---
name: enable-banking
description: "Operates the Enable Banking account-information API — a bank account's transactions and balances. Started only by /enable-banking ."
disable-model-invocation: true
---

# enable-banking

Needs: `EB_KEY` — the environment's application private key (PEM); the project's command exits naming it when unset.

## The entity's own choices

- Its application per environment, each account's ASPSP, which accounts to link, whether production is restricted, whether payment initiation is registered → as the project's instructions state them; none stated → ask the user.
- Restricted production → the application reaches only the accounts whitelisted in the Control Panel.

## Resolve the entity before the first call

- Read the resolved entity's block where the project's instructions place it: application id per environment, the ASPSP each account is linked at, the account keys those links feed.
- The secrets-store item is read, never derived: `applications.<env>.secret` in that block.
- No such block → ask which holder; never fall back to another entity's application.

## Payment initiation

- Payment initiation not registered for the entity's application → no call moves money, and a payment request is refused.

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
