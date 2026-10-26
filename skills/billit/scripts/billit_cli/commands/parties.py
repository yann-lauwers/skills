import re

from .. import creation
from ..batch import each
from ..records import read_party
from .amend import add_amend, report
from ..surface import group, new_command


def squash(vat):
    return re.sub(r"[\s.]", "", vat or "").upper()


def match_party(party, ns):
    if ns.vat and squash(party.get("VATNumber")) != squash(ns.vat):
        return False
    if ns.name and ns.name.lower() not in ("%s %s" % (party.get("Name"), party.get("DisplayName"))).lower():
        return False
    if ns.type and (party.get("PartyType") or "").lower() != ns.type:
        return False
    return True


def list_parties(ns, app, out):
    found = [p for p in app.pages("/v1/parties") if match_party(p, ns)]
    if ns.json:
        out.dump(found)
    elif not found:
        out.say("No party matches.")
    else:
        out.table(["id", "nr", "name", "type", "vat", "country"], [
            [p.get("PartyID"), p.get("Nr"), p.get("DisplayName") or p.get("Name"), p.get("PartyType"),
             p.get("VATNumber"), p.get("CountryCode")] for p in found])
    return 0


def show_party(out, party):
    out.say("party %s  %s  nr %s" % (party.get("PartyID"), party.get("PartyType"), party.get("Nr")))
    out.say("name: %s" % (party.get("DisplayName") or party.get("Name")))
    out.say("vat: %s  country: %s" % (party.get("VATNumber"), party.get("CountryCode")))
    out.say("category: %s  ventilation: %s" % (party.get("CostCategoryCode"), party.get("VentilationCode")))
    out.say("email: %s" % party.get("Email"))


def get_parties(ns, app, out):
    found, code = each(out, ns.ids, lambda party_id: read_party(app, party_id))
    if ns.json:
        out.dump(found)
    else:
        for party in found:
            show_party(out, party)
            out.say()
    return code


def create_party(ns, app, out):
    return report(out, creation.create_party(app, creation.load_spec(app.rt, ns.spec)))


def register(commands):
    _, sub = group(commands, "parties", "List, read, create and amend parties.",
                   "Reads and writes the account's suppliers and customers. Pick a command below.")

    lst = new_command(
        sub, "list", "List parties, filtered in code.",
        "Reads every party Billit lists, keeps those matching the filters and prints id, number, name, type, VAT "
        "number and country.",
        example="  billit parties list --vat \"BE 0425.258.688\"")
    lst.add_argument("--vat", metavar="V", default=None,
                     help="Keep the party with this VAT number, spaces and dots ignored (default: any).")
    lst.add_argument("--name", metavar="TEXT", default=None,
                     help="Keep parties whose name contains TEXT, case-insensitive (default: any).")
    lst.add_argument("--type", choices=["supplier", "customer"], default=None,
                     help="Keep suppliers or customers (default: both).")
    lst.set_defaults(handler=list_parties)

    get = new_command(
        sub, "get", "Read parties in full.",
        "Reads each party from the API. With --json it prints a list holding one record per id, verbatim.",
        example="  billit parties get 53911563")
    get.add_argument("ids", nargs="+", type=int, metavar="ID", help="Party ids to read (required).")
    get.set_defaults(handler=get_parties)

    create = new_command(
        sub, "create", "Create a party from a JSON spec.",
        "Writes to Billit: reads a JSON party body, refuses a VAT number a party already holds, posts the party, then "
        "reads it back and compares every key sent. --dry-run prints the request and sends nothing.",
        example="  billit parties create --spec party.json --dry-run", write=True)
    create.add_argument("--spec", required=True, metavar="FILE",
                        help="JSON party body, or - for standard input (required).")
    create.set_defaults(handler=create_party)

    add_amend(sub, "parties", "party",
              "  billit parties amend 53911563 --set Email=a@example.test --dry-run")
