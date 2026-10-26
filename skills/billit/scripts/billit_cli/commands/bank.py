from .. import assignment
from ..batch import each
from ..reconcile import reconcile
from ..render import day, money, trim
from ..surface import day_arg, group, new_command


def assigned_orders(tx):
    return [e.get("EntityID") for e in tx.get("AssignedEntities") or [] if e.get("EntityType") == "Order"]


def signed(tx):
    amount = float(tx.get("TotalAmount") or 0)
    return -amount if tx.get("TransactionType") == "Debet" else amount


def note_of(tx):
    if tx.get("Note"):
        return tx["Note"]
    lines = (tx.get("Description") or "").strip().splitlines()
    return lines[0] if lines else ""


def in_window(tx, since, until):
    value = day(tx.get("ValueDate"))
    return not (since and value < since) and not (until and value > until)


def list_bank(ns, app, out):
    rows = [t for t in app.pages("/v1/financialTransactions") if in_window(t, ns.since, ns.until)]
    if ns.unassigned:
        rows = [t for t in rows if not t.get("AssignedEntities")]
    if ns.json:
        out.dump(rows)
    elif not rows:
        out.say("No bank transaction matches.")
    else:
        out.table(["id", "value date", "type", "amount", "counterparty", "note", "orders"], [
            [t.get("BankAccountTransactionID"), day(t.get("ValueDate")), t.get("TransactionType"), money(signed(t)),
             t.get("NameCounterParty"), trim(note_of(t)), ",".join(str(i) for i in assigned_orders(t))]
            for t in rows])
    return 0


def row_text(tx):
    return "row %s  %s  %s  %s" % (tx.get("BankAccountTransactionID"), day(tx.get("ValueDate")), money(signed(tx)),
                                   tx.get("NameCounterParty") or "")


def order_text(order):
    return "order %s  %s  %s  %s  %s" % (order.get("OrderID"), order.get("OrderNumber") or "", day(order.get("OrderDate")),
                                         money(order.get("TotalIncl")),
                                         (order.get("CounterParty") or {}).get("DisplayName") or "")


def reconcile_bank(ns, app, out):
    rows = app.all("/v1/financialTransactions")
    orders = app.all("/v1/orders")
    result = reconcile(rows, orders, ns.since)
    if ns.json:
        out.dump({
            "unique": [{"transaction": r, "order": o} for r, o in result.unique],
            "ambiguous": [{"transaction": r, "orders": os} for r, os in result.ambiguous],
            "none": result.none,
            "orders_without_row": result.orders_without_row,
            "already_assigned": [r.get("BankAccountTransactionID") for r in result.already_assigned],
        })
        return 0
    out.say("unique (%d)" % len(result.unique))
    for row, order in result.unique:
        out.say("  %s  ->  %s" % (row_text(row), order_text(order)))
    out.say("ambiguous (%d)" % len(result.ambiguous))
    for row, found in result.ambiguous:
        out.say("  %s" % row_text(row))
        for order in found:
            out.say("      %s" % order_text(order))
    out.say("none (%d)" % len(result.none))
    for row in result.none:
        out.say("  %s" % row_text(row))
    out.say("orders-without-row (%d)" % len(result.orders_without_row))
    for order in result.orders_without_row:
        out.say("  %s" % order_text(order))
    out.say("already assigned: %d rows" % len(result.already_assigned))
    return 0


def assign_bank(ns, app, out):
    lines, code = each(out, ns.orders, lambda order_id: assignment.assign_one(app, ns.tx, order_id))
    for line in lines:
        out.say(line)
    return code


def register(commands):
    _, sub = group(commands, "bank", "List, reconcile and assign bank transactions.",
                   "Reads the account's bank transactions and matches them to orders. Pick a command below.")

    lst = new_command(
        sub, "list", "List bank transactions.",
        "Reads every bank transaction Billit lists and prints id, value date, type, signed amount, counterparty, a "
        "trimmed note and the ids of the orders each is assigned to.",
        example="  billit bank list --unassigned --since 2026-10-01")
    lst.add_argument("--unassigned", action="store_true",
                     help="Keep only transactions assigned to no entity (default: off, every transaction).")
    lst.add_argument("--since", type=day_arg, metavar="D", default=None,
                     help="Keep transactions valued on or after D as YYYY-MM-DD (default: no lower bound).")
    lst.add_argument("--until", type=day_arg, metavar="D", default=None,
                     help="Keep transactions valued on or before D as YYYY-MM-DD (default: no upper bound).")
    lst.set_defaults(handler=list_bank)

    rec = new_command(
        sub, "reconcile", "Match unassigned bank rows to orders, whatever the orders' status.",
        "Reads every bank row and every order, then puts each unassigned row in exactly one bucket: unique (one order "
        "has its amount, direction and a date within 60 days), ambiguous (several do) or none. An order named by no "
        "bank row is a candidate whatever its status, and a candidate no row matched is listed as orders-without-row. "
        "Writes nothing.",
        example="  billit bank reconcile --since 2026-09-01")
    rec.add_argument("--since", type=day_arg, metavar="D", default=None,
                     help="Match only rows valued on or after D as YYYY-MM-DD (default: every unassigned row).")
    rec.set_defaults(handler=reconcile_bank)

    asg = new_command(
        sub, "assign", "Assign one bank transaction to one or more orders.",
        "Writes to Billit through the portal: for each order it reads the transaction's payment page, checks the order "
        "is among the portal's candidates, posts one Add, then reads the transaction and the order back. --dry-run "
        "prints the form it would post and sends nothing.",
        example="  billit bank assign 193758056 148812336 --dry-run", write=True)
    asg.add_argument("tx", type=int, metavar="TXID", help="Bank transaction id (required).")
    asg.add_argument("orders", nargs="+", type=int, metavar="ORDERID", help="Order ids to assign it to (required).")
    asg.set_defaults(handler=assign_bank)
