import urllib.parse

from . import pages
from .errors import DISAGREES, NOT_FOUND, PRECONDITION, Fail


def find_transaction(app, tx_id):
    for tx in app.pages("/v1/financialTransactions"):
        if tx.get("BankAccountTransactionID") == tx_id:
            return tx
    raise Fail(NOT_FOUND, "bank transaction %d not found" % tx_id)


def assign_one(app, tx_id, order_id):
    detail = app.portal_get("/Payment/%d/Detail" % tx_id)
    query = urllib.parse.urlencode(pages.payment_params(detail))
    candidates = app.portal_get("/Payment/%d/DetailPossibleInvoice?%s" % (tx_id, query))
    if not pages.candidate_present(candidates, order_id):
        raise Fail(PRECONDITION, "order %d is not a candidate for transaction %d in the portal's search window"
                   % (order_id, tx_id))
    fields = pages.payment_fields(detail, order_id)
    app.portal_post("/Payment/%d/Detail" % tx_id, fields)
    if app.dry_run:
        return "order %d: assignment to transaction %d previewed; nothing sent" % (order_id, tx_id)
    tx = find_transaction(app, tx_id)
    named = [e.get("EntityID") for e in tx.get("AssignedEntities") or [] if e.get("EntityType") == "Order"]
    order = app.get("/v1/orders/%d" % order_id)
    problems = []
    if order_id not in named:
        problems.append("the transaction does not name the order")
    if float(order.get("ToPay") or 0) != 0:
        problems.append("the order still owes %s" % order.get("ToPay"))
    if problems:
        raise Fail(DISAGREES, "transaction %d: %s" % (tx_id, "; ".join(problems)))
    return "order %d: assigned to transaction %d, verified" % (order_id, tx_id)
