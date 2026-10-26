# Invoice a client for a period

1. Find the client's project: `billit projects list`.
2. Find the client's last invoice: `billit orders list --direction income --party <customer>`, then `billit orders get <newest>`. Copy its layout: lines, rate, units, VAT code, payment method. No previous invoice → ask the user for the layout.
3. Hours: `billit time list --from <date> --to <date> --project <id>`. One line per day, in the last invoice's line shape.
4. Expenses re-invoiced: the period's cost orders the entity's Billit block `reinvoiced_expenses` picks (`billit orders list --direction cost --since <date> --until <date>`, then `billit orders get` for the project). One line per label.
5. A discount the user grants → one negative line in hours; the hours themselves stay as worked.
6. Number and dates: the highest sales invoice number + 1 in the register's `numbering` and `prefix` (`billit orders list --direction income`); due date = issue date + the register's `payment_terms_days`. Tell the user Billit's own counter was not checked.
7. Write the file per `../references/order-spec.md`, then show the user `billit orders create --spec <file> --dry-run`; on their OK, run it without `--dry-run`. Done when it prints the id and `verified`.
8. Never send it.

Report: the entity, the number, the id, the dates, hours, discount, expenses and total, the link `https://my.billit.be/Order/Income/Invoice/<id>/EditOrder`, and that it is unsent.
