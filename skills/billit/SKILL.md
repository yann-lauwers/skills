---
name: billit
description: "Operates Billit, the invoicing tool, for a resolved entity through the `billit` command. Use when a supplier document is handed over to encode ('add this expense', 'encode this invoice', or an invoice PDF or photo pasted with no instruction), when documents wait in the quick-entry queue ('saisie rapide', Billit's screen label), when bank rows and orders need linking ('link them', 'reconcile the bank'), when a client is invoiced ('invoice September'), when hours are encoded on a project, or when a `billit` command or a Billit call fails."
---

# billit

Everything in Billit goes through the `billit` command. The command knows how to log in, page, check its own writes and talk to the web portal; this skill says which command to run when.

## Before the first command

- Run it from inside the repo whose config names the entities: `billit` reads that repo's `docs/agents/integrations/billit.md` and its entity register.
- The entity is the one the request names (`--entity <key>`), else the register's default. Never mix two entities in one answer.
- The entity's books read Billit's codes (its register says `reads_codes` is anything but `false`) → stop and ask the user how its books are kept.
- No `docs/agents/integrations/billit.md` in the repo → ask the user; on their yes, write it per /managing-harness , `references/skills.md` § A tool's skill and its config, holding `register`: `index`, the entity index's path in the repo; `block`, the path inside an entity file to its Billit details, which hold `party_id`, `secret` when the vault item isn't `<entity>-billit`, and optionally `reinvoiced_expenses` and `time_registration_descriptions`; then `reads_codes`, and for invoicing `numbering`, `prefix`, `payment_terms_days`, each a path inside the entity file. Then continue.

## Ask the user first

- Creating a supplier or a customer, or changing anything already in Billit → run the command with `--dry-run`, show the user what it would send, and wait for their OK. Linking a new order to its own payment and clearing an encoded document from the queue go ahead.
- A document not addressed to the entity with its VAT number, a category the supplier's history doesn't settle, a VAT treatment you can't place → propose the options to the user and wait.
- Sending an invoice → only when the user says so.
- Everything else → go ahead.

## Every figure comes from the page

- Read every document yourself. Billit pre-reads uploads; that pre-read is a guess, never a value.
- The category and the VAT code are two separate choices; settling one settles nothing about the other.

## Commands

`billit <noun> <verb> --help` documents each one: its flags, output and exit codes.

| Command | Does |
| --- | --- |
| `whoami` | proves the key and shows the company |
| `queue list` · `queue clear` | the quick-entry queue; `clear` removes documents already encoded, after proving the order holds the same file |
| `files get` | downloads uploaded files, and the PDF inside a Peppol XML |
| `parties list` · `get` · `create` · `amend` | suppliers and customers |
| `orders list` · `get` · `create` · `amend` | purchase and sales documents; `get` includes the category and project |
| `bank list` · `reconcile` · `assign` | bank rows; `reconcile` pairs rows with orders no row points to |
| `time list` · `add` · `delete` | hours on a project |
| `projects list` · `categories list` | the account's projects and cost categories |
| `api` · `portal` | any other Billit call, when no command covers it — `references/api.md` |

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
