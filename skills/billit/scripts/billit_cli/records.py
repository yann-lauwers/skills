import base64
import copy
import json
import re
from collections import namedtuple

from . import pages
from .errors import PRECONDITION, USAGE, WriteRefused, Fail

STRIP = frozenset()
RENEWED = (
    re.compile(r"(^|\.)LastModified$"),
    re.compile(r"^OrderLines\.\d+\.OrderLineID$"),
    re.compile(r"^OrderPDF\.FileID$"),
)
PAID_DATE = "PaidDate"

Kind = namedtuple("Kind", "path id_key")
KINDS = {"orders": Kind("/v1/orders", "OrderID"), "parties": Kind("/v1/parties", "PartyID")}
Outcome = namedtuple("Outcome", "record_id problems")


def read_order(app, order_id):
    record = app.get("/v1/orders/%s" % order_id)
    form = pages.order_form(app.portal_get("/Order/a/a/%s/Redirect" % order_id))
    return dict(record, **form)


def read_party(app, party_id):
    return app.get("/v1/parties/%s" % party_id)


READERS = {"orders": read_order, "parties": read_party}


def coerce(existing, text, path):
    if isinstance(existing, bool):
        if text.lower() not in ("true", "false"):
            raise Fail(USAGE, "%s is true or false, got %r" % (path, text))
        return text.lower() == "true"
    if isinstance(existing, str):
        return text
    try:
        value = json.loads(text)
    except ValueError:
        if existing is None:
            return text
        raise Fail(USAGE, "%s takes JSON of its current type, got %r" % (path, text))
    if isinstance(existing, (int, float)) and not isinstance(value, (int, float)):
        raise Fail(USAGE, "%s is a number, got %r" % (path, text))
    if isinstance(existing, (dict, list)) and type(value) is not type(existing):
        raise Fail(USAGE, "%s is %s, got %r" % (path, type(existing).__name__, text))
    return value


def step(container, part, path, leaf=False):
    if isinstance(container, list):
        if not part.isdigit() or int(part) >= len(container):
            raise Fail(USAGE, "%s: no item %s" % (path, part))
        return int(part)
    if isinstance(container, dict):
        if not leaf and part not in container:
            raise Fail(USAGE, "%s: no key %s" % (path, part))
        return part
    raise Fail(USAGE, "%s: cannot descend into a value that is not a record or a list" % path)


def patch(record, changes, id_key):
    body = copy.deepcopy(record)
    for path, text in changes:
        parts = path.split(".")
        if parts[0] == id_key:
            raise Fail(USAGE, "%s names the record and cannot be set" % id_key)
        container = body
        for part in parts[:-1]:
            slot = step(container, part, path)
            container = container[slot]
            if container is None:
                raise Fail(USAGE, "%s: %s is empty" % (path, part))
        last = step(container, parts[-1], path, leaf=True)
        existing = container[last] if (isinstance(container, list) or last in container) else None
        container[last] = coerce(existing, text, path)
    return body


def file_entry(app, entry):
    if not isinstance(entry, dict) or not entry.get("FileID"):
        return entry
    name, mime, raw = app.file(entry["FileID"])
    return {"FileName": name, "MimeType": mime, "FileContent": base64.b64encode(raw).decode()}


def sendable(app, kind, body):
    send = {k: v for k, v in body.items() if k not in STRIP}
    if kind == "orders":
        if send.get("OrderPDF"):
            send["OrderPDF"] = file_entry(app, send["OrderPDF"])
        if send.get("Attachments"):
            send["Attachments"] = [file_entry(app, a) for a in send["Attachments"]]
    return send


def leaves(value, prefix=""):
    if isinstance(value, dict) and value:
        for key, inner in value.items():
            yield from leaves(inner, "%s.%s" % (prefix, key) if prefix else key)
    elif isinstance(value, list) and value:
        for index, inner in enumerate(value):
            yield from leaves(inner, "%s.%d" % (prefix, index))
    else:
        yield prefix, value


def covered(path, named):
    return any(path == n or path.startswith(n + ".") for n in named)


def attachment_problems(before, after):
    old = {a.get("FileName") for a in before.get("Attachments") or []}
    new = after.get("Attachments") or []
    names = {a.get("FileName") for a in new}
    problems = ["lost Attachments %s" % name for name in sorted(n or "" for n in old - names)]
    for extra in new:
        if extra.get("FileName") not in old and not (
                str(extra.get("FileName", "")).lower().endswith(".json") or extra.get("MimeType") == "application/json"):
            problems.append("unexpected Attachments %s" % extra.get("FileName"))
    return problems


def differences(before, after, named, skip=()):
    seen = dict(leaves(after))
    problems = []
    for path, value in leaves(before):
        if path.startswith("Attachments") or covered(path, named) or path in skip:
            continue
        if any(rule.search(path) for rule in RENEWED):
            continue
        if path not in seen:
            problems.append("lost %s: %r -> absent" % (path, value))
        elif seen[path] != value:
            problems.append("changed %s: %r -> %r" % (path, value, seen[path]))
    return problems + attachment_problems(before, after)


def paid_date_moved(before, after, named):
    return bool(before.get(PAID_DATE)) and PAID_DATE not in named and before.get(PAID_DATE) != after.get(PAID_DATE)


def portal_day(iso):
    return "%s/%s/%s" % (iso[8:10], iso[5:7], iso[0:4])


def restore_paid_date(app, record_id, iso):
    page = "/Order/Cost/Invoice/%s/EditOrder" % record_id
    fields = pages.serialize_form(app.portal_get(page), "orderform")
    if not any(name == "Order.PaidDate" for name, _ in fields):
        raise Fail(PRECONDITION, "the order form carries no Order.PaidDate field")
    done, swapped = [], False
    for name, value in fields:
        if name == "Order.PaidDate" and not swapped:
            value, swapped = portal_day(iso), True
        done.append((name, value))
    text = app.portal_post("/Order/Cost/Invoice/%s/EditOrderUpdate" % record_id, done,
                           {"X-Requested-With": "XMLHttpRequest"})
    try:
        ok = json.loads(text).get("Success") is True
    except (ValueError, AttributeError):
        ok = False
    if not ok:
        raise Fail(PRECONDITION, "the portal did not accept the restored paid date")


def verify(app, kind, record_id, before, named):
    read = READERS[kind]
    after = read(app, record_id)
    if kind == "orders" and paid_date_moved(before, after, named):
        restore_paid_date(app, record_id, before[PAID_DATE])
        after = read(app, record_id)
    return differences(before, after, named)


def changed_at_all(before, after):
    return bool(differences(before, after, (), skip=("LastModified",)))


def replace(app, kind, record_id, changes):
    spec = KINDS[kind]
    before = READERS[kind](app, record_id)
    named = [path for path, _ in changes]
    body = patch(before, changes, spec.id_key)
    send = sendable(app, kind, body)
    try:
        data = app.write("POST", spec.path, send)
    except WriteRefused as refused:
        if refused.status < 500:
            raise
        after = READERS[kind](app, record_id)
        if not changed_at_all(before, after):
            raise WriteRefused(refused.status, "Billit answered its generic 500 and a re-read shows nothing was written")
        return Outcome(record_id, ["Billit answered 500 yet the record changed"] + differences(before, after, named))
    if app.dry_run:
        return None
    new_id = data.get(spec.id_key) if isinstance(data, dict) and data.get(spec.id_key) else record_id
    return Outcome(new_id, verify(app, kind, new_id, before, named))
