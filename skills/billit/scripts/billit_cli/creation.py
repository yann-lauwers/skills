import base64
import json
import os
import re

from .errors import DISAGREES, PRECONDITION, USAGE, Fail, WriteRefused
from .records import Outcome, read_order, read_party
from .render import digest

MISSING = object()
MIME = {".pdf": "application/pdf", ".xml": "text/xml", ".png": "image/png", ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg"}


def load_spec(rt, source):
    try:
        handle = rt.stdin if source == "-" else open(source)
        spec = json.loads(handle.read())
    except (OSError, ValueError) as error:
        raise Fail(USAGE, "cannot read the JSON spec %s: %s" % (source, error))
    if not isinstance(spec, dict):
        raise Fail(USAGE, "the spec is not a JSON object")
    return spec


def read_file(entry):
    path = entry["path"]
    try:
        with open(path, "rb") as handle:
            raw = handle.read()
    except OSError as error:
        raise Fail(USAGE, "cannot read %s: %s" % (path, error))
    suffix = os.path.splitext(path)[1].lower()
    return {"FileName": os.path.basename(path), "MimeType": MIME.get(suffix, "application/octet-stream"),
            "FileContent": base64.b64encode(raw).decode()}, raw


def inline_files(spec):
    body = dict(spec)
    sent = {}
    if isinstance(body.get("OrderPDF"), dict) and "path" in body["OrderPDF"]:
        body["OrderPDF"], sent["OrderPDF"] = read_file(body["OrderPDF"])
    elif isinstance(body.get("OrderPDF"), dict) and body["OrderPDF"].get("FileContent"):
        sent["OrderPDF"] = base64.b64decode(body["OrderPDF"]["FileContent"])
    attachments, raws = [], []
    for entry in body.get("Attachments") or []:
        if isinstance(entry, dict) and "path" in entry:
            entry, raw = read_file(entry)
        elif isinstance(entry, dict) and entry.get("FileContent"):
            raw = base64.b64decode(entry["FileContent"])
        else:
            raw = None
        attachments.append(entry)
        if raw is not None:
            raws.append(raw)
    if attachments:
        body["Attachments"] = attachments
        sent["Attachments"] = raws
    return body, sent


def cents(value):
    return int(round(float(value or 0) * 100))


def totals_problems(spec):
    lines = spec.get("OrderLines") or []
    if not lines:
        return ["the spec carries no OrderLines"]
    problems = []
    sums = {"TotalExcl": 0, "TotalVAT": 0, "TotalIncl": 0}
    for index, line in enumerate(lines):
        for key in sums:
            sums[key] += cents(line.get(key))
        if cents(line.get("TotalExcl")) + cents(line.get("TotalVAT")) != cents(line.get("TotalIncl")):
            problems.append("line %d: TotalExcl plus TotalVAT is not TotalIncl" % index)
    for key, total in sums.items():
        if key in spec and cents(spec[key]) != total:
            problems.append("header %s %s is not the lines' sum %.2f" % (key, spec[key], total / 100))
    for group in spec.get("VatGroups") or []:
        same = [l for l in lines if str(l.get("VentilationCode")) == str(group.get("VentilationCode"))
                and float(l.get("VATPercentage") or 0) == float(group.get("VATPercentage") or 0)]
        for key in ("TotalExcl", "TotalVAT", "TotalIncl"):
            if cents(group.get(key)) != sum(cents(l.get(key)) for l in same):
                problems.append("VatGroup %s/%s: %s is not the lines' sum" % (
                    group.get("VentilationCode"), group.get("VATPercentage"), key))
    return problems


def counterparty_id(spec):
    side = "Supplier" if (spec.get("OrderDirection") or "").lower() == "cost" else "Customer"
    party = spec.get(side)
    return party.get("PartyID") if isinstance(party, dict) else None


def normal(number):
    return str(number or "").strip().lower()


def same_number(app, spec):
    number = normal(spec.get("OrderNumber"))
    direction = (spec.get("OrderDirection") or "").lower()
    party = None if direction == "income" else counterparty_id(spec)
    return [o for o in app.pages("/v1/orders")
            if normal(o.get("OrderNumber")) == number
            and (o.get("OrderDirection") or "").lower() == direction
            and (party is None or (o.get("CounterParty") or {}).get("PartyID") == party)]


def ventilation_gaps(spec):
    gaps = [] if spec.get("VentilationCode") not in (None, "") else ["the header"]
    gaps += ["line %d" % index for index, line in enumerate(spec.get("OrderLines") or [])
             if line.get("VentilationCode") in (None, "")]
    gaps += ["VatGroup %d" % index for index, group in enumerate(spec.get("VatGroups") or [])
             if group.get("VentilationCode") in (None, "")]
    return gaps


def check_preconditions(app, spec):
    if not normal(spec.get("OrderNumber")):
        raise Fail(PRECONDITION, "the spec carries no OrderNumber to check for a duplicate")
    missing = ventilation_gaps(spec)
    if missing:
        raise Fail(PRECONDITION, "VentilationCode missing on " + ", ".join(missing))
    twins = same_number(app, spec)
    if twins:
        raise Fail(PRECONDITION, "order number %s already exists as order %s" % (spec["OrderNumber"],
                                                                                  twins[0].get("OrderID")))
    problems = totals_problems(spec)
    if problems:
        raise Fail(PRECONDITION, "totals do not reconcile: " + "; ".join(problems))


def new_id(data):
    if isinstance(data, dict):
        data = data.get("OrderID") or data.get("PartyID")
    if isinstance(data, int) and not isinstance(data, bool):
        return data
    if isinstance(data, str) and data.isdigit():
        return int(data)
    return None


def expected_totals(spec):
    lines = spec.get("OrderLines") or []
    return {key: spec[key] if key in spec else sum(cents(l.get(key)) for l in lines) / 100
            for key in ("TotalExcl", "TotalVAT", "TotalIncl")}


def readback_problems(app, spec, sent, after):
    problems = []
    for key, want in expected_totals(spec).items():
        if cents(after.get(key)) != cents(want):
            problems.append("%s: sent %.2f, read back %s" % (key, float(want), after.get(key)))
    lines, got = spec.get("OrderLines") or [], after.get("OrderLines") or []
    if len(lines) != len(got):
        problems.append("OrderLines: sent %d, read back %d" % (len(lines), len(got)))
    for index, (line, back) in enumerate(zip(lines, got)):
        if cents(line.get("TotalExcl")) != cents(back.get("TotalExcl")):
            problems.append("line %d TotalExcl: sent %s, read back %s" % (index, line.get("TotalExcl"), back.get("TotalExcl")))
        if "VentilationCode" in line and str(line["VentilationCode"]) != str(back.get("VentilationCode")):
            problems.append("line %d VentilationCode: sent %s, read back %s" % (
                index, line["VentilationCode"], back.get("VentilationCode")))
    for group in spec.get("VatGroups") or []:
        back = [g for g in after.get("VatGroups") or []
                if float(g.get("VATPercentage") or 0) == float(group.get("VATPercentage") or 0)
                and str(g.get("VentilationCode")) == str(group.get("VentilationCode"))]
        if not back:
            problems.append("VatGroup %s/%s missing on read-back" % (group.get("VentilationCode"),
                                                                     group.get("VATPercentage")))
    for key in ("VentilationCode", "CostCategoryCode", "ProjectID"):
        if key in spec and str(spec[key]) != str(after.get(key)):
            problems.append("%s: sent %s, read back %s" % (key, spec[key], after.get(key)))
    problems += file_problems(app, sent, after)
    return problems


def file_problems(app, sent, after):
    problems = []
    if "OrderPDF" in sent:
        pdf = after.get("OrderPDF") or {}
        if not pdf.get("FileID"):
            problems.append("OrderPDF missing on read-back")
        elif digest(app.file(pdf["FileID"])[2]) != digest(sent["OrderPDF"]):
            problems.append("OrderPDF bytes differ from the file sent")
    if sent.get("Attachments"):
        held = {digest(app.file(a["FileID"])[2]) for a in after.get("Attachments") or [] if a.get("FileID")}
        for raw in sent["Attachments"]:
            if digest(raw) not in held:
                problems.append("an attachment's bytes are missing on read-back")
    return problems


def create_order(app, spec):
    body, sent = inline_files(spec)
    check_preconditions(app, spec)
    try:
        data = app.write("POST", "/v1/orders", body)
    except WriteRefused as refused:
        if refused.status < 500:
            raise
        twins = same_number(app, spec)
        if not twins:
            raise WriteRefused(refused.status, "Billit answered its generic 500 and a re-read shows nothing was written")
        order_id = twins[0]["OrderID"]
        return Outcome(order_id, ["Billit answered 500 yet the order exists"]
                       + readback_problems(app, spec, sent, read_order(app, order_id)))
    if app.dry_run:
        return None
    order_id = new_id(data)
    if order_id is None:
        twins = same_number(app, spec)
        if not twins:
            raise Fail(DISAGREES, "Billit named no id and no order carries number %s" % spec["OrderNumber"])
        order_id = twins[0]["OrderID"]
    return Outcome(order_id, readback_problems(app, spec, sent, read_order(app, order_id)))


def subset_problems(sent, got, path=""):
    if isinstance(sent, dict):
        if not isinstance(got, dict):
            return ["%s: sent a record, read back %r" % (path or "party", got)]
        return [p for key, value in sent.items()
                for p in subset_problems(value, got.get(key, MISSING), "%s.%s" % (path, key) if path else key)]
    if isinstance(sent, list):
        if not isinstance(got, list) or len(got) < len(sent):
            return ["%s: sent %d items, read back %r" % (path, len(sent), got)]
        return [p for i, value in enumerate(sent) for p in subset_problems(value, got[i], "%s.%d" % (path, i))]
    if got is MISSING:
        return ["%s: sent %r, absent on read-back" % (path, sent)]
    if sent != got:
        return ["%s: sent %r, read back %r" % (path, sent, got)]
    return []



def squash(vat):
    return re.sub(r"[\s.]", "", vat or "").upper()


def party_twins(app, spec):
    vat = squash(spec.get("VATNumber"))
    if not vat:
        return []
    return [p for p in app.pages("/v1/parties") if squash(p.get("VATNumber")) == vat]


def create_party(app, spec):
    twins = party_twins(app, spec)
    if twins:
        raise Fail(PRECONDITION, "VAT number %s already belongs to party %s" % (spec["VATNumber"], twins[0].get("PartyID")))
    data = app.write("POST", "/v1/parties", spec)
    if app.dry_run:
        return None
    party_id = new_id(data)
    if party_id is None:
        found = party_twins(app, spec)
        if not found:
            raise Fail(DISAGREES, "Billit named no id for the created party")
        party_id = found[0]["PartyID"]
    return Outcome(party_id, subset_problems(spec, read_party(app, party_id)))
