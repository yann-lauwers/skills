---
name: billit
description: "Operates Billit, the invoicing tool, through the `billit` command. Use when a supplier document is handed over to encode ('add this expense', or an invoice PDF or photo pasted with no instruction), on the quick-entry queue ('saisie rapide'), linking bank rows and orders ('reconcile the bank'), invoicing a client ('invoice September'), encoding hours on a project, or a failing `billit` command or Billit call."
---

# billit

Every Billit act goes through the `billit` command; `billit <noun> <verb> --help` documents each one's flags, output and exit codes.

## Project config

- Run `billit` from inside the repo whose `docs/agents/integrations/billit.md` names the entity register; its keys → `references/config.md`.
- The entity is the one the request names (`--entity <key>`), else the register's default. Never mix two entities in one answer.
- The entity's books read Billit's codes (the register's `reads_codes` is anything but `false`) → stop and ask the user how its books are kept.
- No `docs/agents/integrations/billit.md` in the repo → ask the user; on their yes, write it per /managing-harness , `references/skills.md` § A tool's skill and its config, with the keys in `references/config.md`; then continue.

## Ask the user first

- Creating a supplier or a customer, or changing anything already in Billit → run the command with `--dry-run`, show the user what it would send, and wait for their OK. Linking a new order to its own payment and clearing an encoded document from the queue go ahead.
- A document not addressed to the entity with its VAT number, a category the supplier's history doesn't settle, a VAT treatment not yet placed → propose the options to the user and wait.
- Sending an invoice → only when the user says so.
- Everything else → go ahead.

## Every figure comes from the page

- Read every document; Billit's pre-read of an upload is a guess, never a value.
- The category and the VAT code are two separate choices; settling one settles nothing about the other.

## Routing

| If the task is | Read |
| --- | --- |
| one supplier document to encode | `cookbook/add-expense.md` |
| the quick-entry queue | `cookbook/process-quick-entry.md` |
| bank rows and orders to link | `cookbook/reconcile-bank.md` |
| invoicing a client for a period | `cookbook/create-sales-invoice.md` |
| a month of hours on a project | `cookbook/encode-hours.md` |
| choosing a cost category or a VAT code | `references/codes.md` |
| writing the file `billit orders create` takes | `references/order-spec.md` |
| a Billit call no command covers | `references/api.md` |
| the register's keys, or writing the missing config | `references/config.md` |
