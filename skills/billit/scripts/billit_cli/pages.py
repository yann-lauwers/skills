import base64
import re
import xml.etree.ElementTree as ET
from html import unescape
from html.parser import HTMLParser

from .errors import PRECONDITION, Fail

ATTR = re.compile(r"""([\w:.-]+)\s*=\s*(?:"([^"]*)"|'([^']*)')""")
TAG = re.compile(r"<[^>]*>")
TILE_SPLIT = re.compile(r"(?=\bbulkInputItemParent\b)")
TIME_PAGE = 20
NO_DESCRIPTION = "Aucune description"


def attrs_of(tag):
    return {m.group(1): unescape(m.group(2) if m.group(2) is not None else m.group(3)) for m in ATTR.finditer(tag)}


def text_of(fragment):
    return " ".join(unescape(TAG.sub(" ", fragment)).split())


def find_input(html, ident):
    for match in re.finditer(r"<input\b[^>]*>", html):
        attrs = attrs_of(match.group(0))
        if attrs.get("id") == ident:
            return attrs.get("value", "")
    return None


def number_or_text(value):
    if value == "":
        return None
    return int(value) if value.isdigit() else value


def order_form(html):
    found = {}
    for key, ident in (("CostCategoryCode", "Order_CostCategoryCode"), ("ProjectID", "ProjectID")):
        value = find_input(html, ident)
        if value is None:
            raise Fail(PRECONDITION, "the order form carries no %s input" % ident)
        found[key] = number_or_text(value)
    return found


def grid_tiles(html):
    tiles = []
    for block in TILE_SPLIT.split(html)[1:]:
        merge = re.search(r'data-document-merge-id="([^"]+)"', block)
        names = re.findall(r'title="([^"]*\.(?:pdf|jpg|jpeg|png|xml))"', block, re.I)
        if merge and names:
            tiles.append({"name": unescape(names[0]), "merge_id": merge.group(1)})
    return tiles


class Categories(HTMLParser):
    def __init__(self):
        super().__init__()
        self.found = {}

    def handle_starttag(self, tag, attrs):
        data = dict(attrs)
        code = data.get("data-costcategorycode")
        if code and code not in self.found:
            self.found[code] = {"code": int(code) if code.isdigit() else code, "name": data.get("data-name") or "",
                                "specification": data.get("data-specification") or ""}


def categories(html):
    parser = Categories()
    parser.feed(html)
    return list(parser.found.values())


def time_rows(html):
    rows = []
    for block in re.split(r"(?=<tr\b)", html):
        ident = re.search(r'TimeRegistrationEntries_\d+__TimeRegistrationID"[^>]*value="(\d+)"', block)
        if not ident:
            continue
        date = re.search(r"font-weight-bold w60px'>([^<]*)<", block)
        user = re.search(r"<div class='ml-3'>([^<]*)<", block)
        seconds = re.search(r'data-duration="(\d+)"', block)
        first = re.search(r"<td class='maxw300px[^>]*>([\s\S]*?)</td>", block)
        description = ""
        if first:
            rest = re.sub(r"<div class='text-muted d-flex'>[\s\S]*?</div></div>", "", first.group(1), count=1)
            description = text_of(rest)
            if description == NO_DESCRIPTION:
                description = ""
        cells = re.findall(r"<td class='text-nowrap d-none d-md-table-cell'>([\s\S]*?)</td>", block)
        cells = [text_of(c) for c in cells] + [""] * 3
        rows.append({
            "TimeRegistrationID": int(ident.group(1)),
            "Date": unescape(date.group(1)) if date else "",
            "User": unescape(user.group(1)) if user else "",
            "Description": description,
            "DurationSeconds": int(seconds.group(1)) if seconds else 0,
            "Client": cells[0],
            "Project": cells[1],
            "Invoiced": cells[2],
        })
    return rows


def embedded_documents(xml_bytes):
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError as error:
        raise Fail(PRECONDITION, "the UBL does not parse: %s" % error)
    found = []
    for node in root.iter():
        if node.tag.endswith("}EmbeddedDocumentBinaryObject") or node.tag == "EmbeddedDocumentBinaryObject":
            name = node.attrib.get("filename")
            if name and node.text:
                found.append((name, base64.b64decode(node.text.strip())))
    return found


def form_span(html, form_id):
    opening = None
    for match in re.finditer(r"<form\b[^>]*>", html):
        if attrs_of(match.group(0)).get("id") == form_id:
            opening = match
            break
    if opening is None:
        raise Fail(PRECONDITION, "the page carries no form with id %s" % form_id)
    depth = 1
    for match in re.finditer(r"<form\b[^>]*>|</form\s*>", html[opening.end():]):
        depth += 1 if match.group(0).startswith("<form") else -1
        if depth == 0:
            return html[opening.end(): opening.end() + match.start()]
    return html[opening.end():]


def option_value(tag, label):
    attrs = attrs_of(tag)
    return attrs["value"] if "value" in attrs else text_of(label)


def serialize_form(html, form_id):
    span = form_span(html, form_id)
    found = []
    pattern = re.compile(r"<input\b[^>]*>|<select\b[^>]*>[\s\S]*?</select\s*>|<textarea\b[^>]*>[\s\S]*?</textarea\s*>",
                         re.I)
    for match in pattern.finditer(span):
        chunk = match.group(0)
        opening = re.match(r"<[^>]*>", chunk).group(0)
        attrs = attrs_of(opening)
        name = attrs.get("name")
        disabled = re.search(r"\bdisabled\b", re.sub(r"""("[^"]*"|'[^']*')""", "", opening))
        if not name or disabled:
            continue
        kind = chunk[:7].lower()
        if kind.startswith("<input"):
            checkable = attrs.get("type", "text").lower() in ("checkbox", "radio")
            flags = re.sub(r"""("[^"]*"|'[^']*')""", "", opening)
            if attrs.get("type", "text").lower() in ("submit", "button", "image", "file", "reset"):
                continue
            if checkable and not re.search(r"\bchecked\b", flags):
                continue
            found.append((name, attrs.get("value", "on" if checkable else "")))
        elif kind.startswith("<select"):
            options = re.findall(r"(<option\b[^>]*>)([\s\S]*?)(?=<option\b|</select)", chunk, re.I)
            chosen = [o for o in options if re.search(r"\bselected\b", re.sub(r"""("[^"]*"|'[^']*')""", "", o[0]))]
            multiple = re.search(r"\bmultiple\b", re.sub(r"""("[^"]*"|'[^']*')""", "", opening))
            if not multiple:
                chosen = chosen[:1] or options[:1]
            found += [(name, option_value(tag, label)) for tag, label in chosen]
        else:
            body = re.sub(r"^<textarea[^>]*>|</textarea\s*>$", "", chunk, flags=re.I)
            found.append((name, unescape(body)))
    return found


PAYMENT_PARAMS = {"KeyWords": "Keywords", "IncludePaidInvoices": "IncludePaidInvoices",
                  "IncludeCounterPayments": "IncludeCounterPayments", "SortColumn": "sortColumn",
                  "SortDescending": "sortDescending", "SearchFrom": "SearchFromOrderDate",
                  "SearchUntil": "SearchUntilOrderDate"}
PAYMENT_DATE_PARAMS = ("SearchFrom", "SearchUntil")


def find_param(html, name):
    for match in re.finditer(r"<input\b[^>]*>", html):
        attrs = attrs_of(match.group(0))
        if attrs.get("id") == name or attrs.get("name") == name:
            return attrs.get("value", "")
    return ""


def payment_params(html):
    found = {query: find_param(html, field) for query, field in PAYMENT_PARAMS.items()}
    for query in PAYMENT_DATE_PARAMS:
        found[query] = found[query].split(" ")[0]
        if not found[query]:
            raise Fail(PRECONDITION, "the payment page carries no %s date" % PAYMENT_PARAMS[query])
    found["IncludePaidInvoices"] = "true"
    return list(found.items())


def payment_form(html):
    marker = html.find('id="pageform"')
    if marker < 0:
        raise Fail(PRECONDITION, "the payment page carries no pageform")
    start = html.rfind("<form", 0, marker)
    if start < 0:
        raise Fail(PRECONDITION, "the payment page carries no form around pageform")
    end = html.find("</form>", start)
    return html[start: end if end >= 0 else len(html)]


def payment_fields(html, order_id):
    pairs = []
    for match in re.finditer(r"<input\b[^>]*>", payment_form(html)):
        tag = match.group(0)
        attrs = attrs_of(tag)
        name = attrs.get("name")
        if not name:
            continue
        kind = attrs.get("type", "text").lower()
        if kind in ("checkbox", "radio") and not re.search(r"\bchecked\b", re.sub(r"""("[^"]*"|'[^']*')""", "", tag)):
            continue
        pairs.append((name, attrs.get("value", "")))
    names = [n for n, _ in pairs]
    for needed in ("ButtonActionType", "OrderIDManipulate"):
        if needed not in names:
            raise Fail(PRECONDITION, "the payment form carries no %s field" % needed)
    swap = {"ButtonActionType": "Add", "OrderIDManipulate": str(order_id)}
    return [(n, swap.get(n, v)) for n, v in pairs]


def candidate_present(html, order_id):
    return 'id="%s"' % order_id in html
