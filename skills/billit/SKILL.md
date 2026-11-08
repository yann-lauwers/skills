---
name: billit
description: "Operates Billit, the invoicing tool, through the `billit` command. Use when a supplier document is handed over to encode ('add this expense', or an invoice PDF or photo pasted with no instruction), on the quick-entry queue ('saisie rapide'), invoicing a client ('invoice September'), encoding hours on a project, or a failing `billit` command or Billit call."
---

# billit

Every Billit act goes through the `billit` command; `billit <noun> <verb> --help` documents each one's flags, output and exit codes.

Needs: `BILLIT_API_KEY` — one Billit account's key; the command exits 4 when it is unset.

## The entity's own choices

- Invoice numbering and payment terms, which costs are re-invoiced, whether hours carry a description, whether its books read Billit's codes → as the project's instructions state them; none stated → ask the user.
- Its books read Billit's codes → stop and ask the user how its books are kept.

## Ask the user first

- Creating a supplier or a customer, or changing anything already in Billit → run the command with `--dry-run`, show the user what it would send — a batch shown whole, for one OK — and **wait for their OK**. Linking a new order to its own payment and clearing an encoded document from the queue go ahead.
- Sending an invoice → only when the user says so.
- Everything else → go ahead.

## Every figure comes from the page

- Read every document; Billit's pre-read of an upload is a guess, never a value.

## Routing

| If the task is | Read |
| --- | --- |
| one supplier document to encode | `cookbook/add-expense.md` |
| the quick-entry queue | `cookbook/process-quick-entry.md` |
| invoicing a client for a period | `cookbook/create-sales-invoice.md` |
| a month of hours on a project | `cookbook/encode-hours.md` |
| choosing a cost category or a VAT code | `references/codes.md` |
| writing the file `billit orders create` takes | `references/order-spec.md` |
| a Billit call no command covers | `references/api.md` |
