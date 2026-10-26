from collections import namedtuple
from datetime import date

from .render import day

WINDOW_DAYS = 60
Result = namedtuple("Result", "unique ambiguous none orders_without_row already_assigned")


def cents(value):
    return int(round(abs(float(value or 0)) * 100))


def as_date(text):
    return date.fromisoformat(day(text))


def named_orders(rows):
    return {e.get("EntityID") for r in rows for e in r.get("AssignedEntities") or [] if e.get("EntityType") == "Order"}


def expected_type(order):
    cost = (order.get("OrderDirection") or "").lower() == "cost"
    credit_note = (order.get("OrderType") or "").lower() == "creditnote"
    return "Debet" if cost != credit_note else "Credit"


def fits(row, order):
    return (cents(row.get("TotalAmount")) == cents(order.get("TotalIncl"))
            and row.get("TransactionType") == expected_type(order)
            and abs((as_date(order.get("OrderDate")) - as_date(row.get("ValueDate"))).days) <= WINDOW_DAYS)


def reconcile(rows, orders, since=None):
    taken = named_orders(rows)
    horizon = None
    if since:
        horizon = date.fromordinal(date.fromisoformat(since).toordinal() - WINDOW_DAYS)
    candidates = [o for o in orders if o.get("OrderID") not in taken
                  and (horizon is None or as_date(o.get("OrderDate")) >= horizon)]
    unassigned = [r for r in rows if not r.get("AssignedEntities") and (not since or day(r.get("ValueDate")) >= since)]
    assigned = [r for r in rows if r.get("AssignedEntities")]
    unique, ambiguous, none, matched = [], [], [], set()
    for row in unassigned:
        found = [o for o in candidates if fits(row, o)]
        matched.update(o["OrderID"] for o in found)
        if len(found) == 1:
            unique.append((row, found[0]))
        elif found:
            ambiguous.append((row, found))
        else:
            none.append(row)
    leftover = [o for o in candidates if o["OrderID"] not in matched]
    return Result(unique, ambiguous, none, leftover, assigned)
