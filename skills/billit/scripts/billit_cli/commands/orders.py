from .. import creation, records
from ..batch import each
from ..render import day, money
from .amend import add_amend, report
from ..surface import day_arg, group, new_command


def match_order(order, ns):
    if ns.direction and (order.get("OrderDirection") or "").lower() != ns.direction:
        return False
    if ns.party is not None and (order.get("CounterParty") or {}).get("PartyID") != ns.party:
        return False
    if ns.status and (order.get("OrderStatus") or "").lower() != ns.status.lower():
        return False
    if ns.since and day(order.get("OrderDate")) < ns.since:
        return False
    if ns.until and day(order.get("OrderDate")) > ns.until:
        return False
    if ns.number and (order.get("OrderNumber") or "").lower() != ns.number.lower():
        return False
    return True


def selected(app, ns):
    found = []
    for order in app.pages("/v1/orders"):
        if match_order(order, ns):
            found.append(order)
            if ns.limit and len(found) >= ns.limit:
                break
    return found


def list_orders(ns, app, out):
    found = selected(app, ns)
    if ns.json:
        out.dump(found)
    elif not found:
        out.say("No order matches.")
    else:
        out.table(["id", "number", "date", "party", "total incl", "status"], [
            [o.get("OrderID"), o.get("OrderNumber"), day(o.get("OrderDate")),
             (o.get("CounterParty") or {}).get("DisplayName"), money(o.get("TotalIncl")), o.get("OrderStatus")]
            for o in found])
    return 0


def show_order(out, order):
    party = order.get("Supplier") or order.get("CounterParty") or {}
    out.say("order %s  %s %s  %s" % (order.get("OrderID"), order.get("OrderDirection"), order.get("OrderType"),
                                     order.get("OrderStatus")))
    out.say("number: %s" % order.get("OrderNumber"))
    out.say("date: %s  due: %s  paid: %s" % (day(order.get("OrderDate")), day(order.get("ExpiryDate")),
                                            day(order.get("PaidDate")) or "no"))
    out.say("party: %s (%s)" % (party.get("DisplayName") or party.get("Name"), party.get("PartyID")))
    out.say("total: %s excl, %s VAT, %s incl, %s to pay" % (money(order.get("TotalExcl")), money(order.get("TotalVAT")),
                                                            money(order.get("TotalIncl")), money(order.get("ToPay"))))
    out.say("cost category: %s  project: %s  ventilation: %s" % (order.get("CostCategoryCode"), order.get("ProjectID"),
                                                                  order.get("VentilationCode")))
    for line in order.get("OrderLines") or []:
        out.say("  %s x %s  %s excl  %s%%  code %s" % (line.get("Quantity"), line.get("Description"),
                                                      money(line.get("TotalExcl")), line.get("VATPercentage"),
                                                      line.get("VentilationCode")))


def get_orders(ns, app, out):
    found, code = each(out, ns.ids, lambda order_id: records.read_order(app, order_id))
    if ns.json:
        out.dump(found)
    else:
        for order in found:
            show_order(out, order)
            out.say()
    return code


def create_order(ns, app, out):
    return report(out, creation.create_order(app, creation.load_spec(app.rt, ns.spec)))


def register(commands):
    _, sub = group(commands, "orders", "List, read, create and amend orders.",
                   "Reads and writes the account's orders: purchase invoices and credit notes (cost) and sales "
                   "invoices (income). Pick a command below.")

    lst = new_command(
        sub, "list", "List orders, filtered in code.",
        "Reads every order Billit lists, keeps those matching the filters and prints id, number, date, party, total "
        "including VAT and status. The listing omits suppliers and lines; use orders get for those.",
        example="  billit orders list --direction cost --since 2026-09-01")
    lst.add_argument("--direction", choices=["cost", "income"], default=None,
                     help="Keep cost (purchase) or income (sales) orders (default: both).")
    lst.add_argument("--party", type=int, metavar="ID", default=None,
                     help="Keep orders of this counterparty party id (default: every party).")
    lst.add_argument("--status", metavar="S", default=None,
                     help="Keep orders with this OrderStatus, such as Paid (default: every status).")
    lst.add_argument("--since", type=day_arg, metavar="D", default=None,
                     help="Keep orders dated on or after D as YYYY-MM-DD (default: no lower bound).")
    lst.add_argument("--until", type=day_arg, metavar="D", default=None,
                     help="Keep orders dated on or before D as YYYY-MM-DD (default: no upper bound).")
    lst.add_argument("--number", metavar="N", default=None,
                     help="Keep the order with this exact number (default: every number).")
    lst.add_argument("--limit", type=int, metavar="N", default=0,
                     help="Stop after N matches (default: 0, no limit).")
    lst.set_defaults(handler=list_orders)

    get = new_command(
        sub, "get", "Read orders in full, with their category and project.",
        "Reads each order from the API and its edit form from the portal, and prints the order with the cost "
        "category code and project id only the form carries. With --json it prints a list holding one record per "
        "id, with CostCategoryCode and ProjectID added. A form that cannot be parsed exits 7.",
        example="  billit orders get 148812336 --json")
    get.add_argument("ids", nargs="+", type=int, metavar="ID", help="Order ids to read (required).")
    get.set_defaults(handler=get_orders)

    create = new_command(
        sub, "create", "Create an order from a JSON spec.",
        "Writes to Billit: reads a JSON order body, refuses a duplicate order number or lines that do not add up to "
        "the totals, posts the order, then reads it back and compares totals, lines, every ventilation code, the "
        "PDF's bytes and the cost category and project. OrderPDF and Attachments entries may be {\"path\": FILE}; "
        "the file is read and sent as base64. --dry-run prints the request and sends nothing.",
        example="  billit orders create --spec order.json --dry-run", write=True)
    create.add_argument("--spec", required=True, metavar="FILE",
                        help="JSON order body, or - for standard input (required).")
    create.set_defaults(handler=create_order)

    add_amend(sub, "orders", "order",
              "  billit orders amend 130356834 --set Comments=x --dry-run")
