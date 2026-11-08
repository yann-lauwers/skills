# Invoice a client for a period

1. Find the client's last invoice: `billit orders list --direction income --party <customer>`, then `billit orders get <newest>`. Copy its layout: lines, rate, units, VAT code, payment method. No previous invoice → ask the user for the layout.
2. Hours: `billit time list --from <date> --to <date> --project <id>`, the id from `billit projects list`. One line per day, in the last invoice's line shape.
3. Expenses re-invoiced: the period's cost orders the entity re-invoices (`billit orders list --direction cost --since <date> --until <date>`, then `billit orders get` for the project). One line per label.
4. A discount the user grants → one negative line in hours; the hours themselves stay as worked.
5. A draft for the period already in Billit → add the lines to it with `billit orders amend`. None → write the file per `../references/order-spec.md`: the number the entity's numbering gives after its highest sales invoice, the due date its payment terms give; tell the user Billit's own counter was not checked. Done when the write prints the id and `verified`.

Report: the entity, the number, the id, the dates, hours, discount, expenses and total, the link `https://my.billit.be/Order/Income/Invoice/<id>/EditOrder`, and that it is unsent.
