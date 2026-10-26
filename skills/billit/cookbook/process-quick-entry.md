# Process the quick-entry queue

1. Look at the queue: `billit queue list`. Documents marked invalid stay queued for the user.
2. Download everything: `billit files get <FileID>… --out <dir>`.
3. Read each document per `add-expense.md` steps 2–3.
4. Group the documents by supplier — same name and same VAT number — and settle the supplier, category and VAT code once per group, per `add-expense.md` steps 4–5.
5. Encode each document per `add-expense.md` steps 6–7.
6. Clear what was encoded: `billit queue clear <FileID>:<OrderID>…`.

Report: the entity, one row per document as `add-expense.md` reports it; apart, the documents left queued and why.
