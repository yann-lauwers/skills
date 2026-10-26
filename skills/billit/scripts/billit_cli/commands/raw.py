import json

from ..errors import USAGE, Fail
from ..surface import new_command

API_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE"]


def field_pairs(fields):
    pairs = []
    for field in fields or []:
        key, sep, value = field.partition("=")
        if not sep or not key:
            raise Fail(USAGE, "-F takes key=value, got %r" % field)
        pairs.append((key, value))
    return pairs


def typed(text):
    try:
        return json.loads(text)
    except ValueError:
        return text


def body_of(ns, rt_stdin):
    if ns.body and ns.field:
        raise Fail(USAGE, "give --body or -F, not both")
    if ns.body:
        try:
            handle = rt_stdin if ns.body == "-" else open(ns.body)
            return json.loads(handle.read())
        except (OSError, ValueError) as error:
            raise Fail(USAGE, "cannot read the JSON body %s: %s" % (ns.body, error))
    if ns.field:
        return {k: typed(v) for k, v in field_pairs(ns.field)}
    return None


def api(ns, app, out):
    if ns.method == "GET":
        if ns.body:
            raise Fail(USAGE, "a GET carries no body; use -F for query parameters")
        params = ["%s=%s" % (k, v) for k, v in field_pairs(ns.field)]
        out.dump(app.all(ns.path, params) if ns.paginate else app.get(ns.path, params))
        return 0
    if ns.paginate:
        raise Fail(USAGE, "--paginate reads pages and applies to GET only")
    data = app.write(ns.method, ns.path, body_of(ns, app.rt.stdin))
    if app.dry_run:
        return 0
    if data is None:
        out.say("done")
    else:
        out.dump(data)
    return 0


def portal(ns, app, out):
    pairs = field_pairs(ns.field)
    if ns.method == "GET":
        out.say(app.portal_get(ns.path, ["%s=%s" % (k, v) for k, v in pairs]))
        return 0
    text = app.portal_post(ns.path, pairs)
    if not app.dry_run:
        out.say(text)
    return 0


def register(commands):
    sub = new_command(
        commands, "api", "Call the Billit JSON API directly.",
        "Sends one request to the Billit JSON API and prints the JSON answer. GET reads; every other method writes "
        "to Billit, and --dry-run prints the exact request instead. For GET, -F adds query parameters and --paginate "
        "prints every page as one list; for the others, -F builds the JSON body and --body reads it from a file.",
        example="  billit api GET /v1/orders --paginate", write=True)
    sub.add_argument("method", choices=API_METHODS, metavar="METHOD",
                     help="HTTP method, GET POST PUT PATCH or DELETE (required).")
    sub.add_argument("path", metavar="PATH", help="API path such as /v1/projects (required).")
    sub.add_argument("-F", "--field", action="append", metavar="KEY=VALUE", default=None,
                     help="Query parameter on GET, top-level JSON body field otherwise, repeatable; a value that is "
                          "valid JSON is sent typed (default: none).")
    sub.add_argument("--body", metavar="FILE", default=None,
                     help="JSON file, or - for standard input, sent as the body of a write (default: none).")
    sub.add_argument("--paginate", action="store_true",
                     help="On GET, read pages of 120 until a short page and print one list (default: off, one request).")
    sub.set_defaults(handler=api)

    sub = new_command(
        commands, "portal", "Call a page of the Billit web portal.",
        "Opens a portal session with the API key's SSO token and sends one request through it. GET prints the page; "
        "POST writes to the portal as a urlencoded form built from -F, and --dry-run prints the form instead. The "
        "token and the cookies are never printed.",
        example="  billit portal GET /TimeRegistration/Index", write=True)
    sub.add_argument("method", choices=["GET", "POST"], metavar="METHOD", help="HTTP method, GET or POST (required).")
    sub.add_argument("path", metavar="PATH", help="Portal path such as /Payment/Index (required).")
    sub.add_argument("-F", "--field", action="append", metavar="KEY=VALUE", default=None,
                     help="Query parameter on GET, form field on POST, repeatable (default: none).")
    sub.set_defaults(handler=portal)
