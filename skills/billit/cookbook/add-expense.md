# Add a supplier expense

1. Get the document: the file handed over, or `billit files get <FileID> --out <dir>`. Read it yourself.
2. Write down the supplier's name and VAT number, the document number and date, the amount before VAT, the VAT, the total, the amount actually charged, and who it is addressed to. Done when amount before VAT + VAT = total; when it doesn't, ask the user.
3. Addressed to anyone but the entity with its VAT number → tell the user which is missing and continue only on their answer.
4. Find the supplier: `billit parties list --vat <VAT>`, or `--name`. Not found → ask the user, then `billit parties create`.
5. Pick the category and the VAT code: what the supplier's recent orders carry (`billit orders list --party <id>`, then `billit orders get <id>`). A new supplier, a history that disagrees, or a VAT treatment you can't place → decide it with the user, per `references/codes.md`. An order carries one category: a document mixing a charge and an asset → ask the user.
6. Create the order: `billit orders create --spec <file>`, the file written per `../references/order-spec.md`. Done when it prints the new id and `verified`.
7. Find its payment: `billit bank list --unassigned --since <document date>`; rows carrying the amount actually charged and the supplier's or the shop's name: exactly one → `billit bank assign <row> <order>`; several → show them to the user; none → say so.
8. Came from the quick-entry queue → `billit queue clear <FileID>:<OrderID>`.

Report: the entity, then the order id and number, supplier, category, VAT code, the three amounts, the bank row or its absence; apart, anything the user still has to answer.
