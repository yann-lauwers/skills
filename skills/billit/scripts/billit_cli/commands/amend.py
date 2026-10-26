from .. import records
from ..errors import DISAGREES, USAGE, Fail
from ..surface import new_command


def set_pairs(texts):
    pairs = []
    for text in texts:
        path, sep, value = text.partition("=")
        if not sep or not path:
            raise Fail(USAGE, "--set takes PATH=VALUE, got %r" % text)
        pairs.append((path, value))
    return pairs


def report(out, outcome):
    if outcome is None:
        return 0
    out.say(str(outcome.record_id))
    if not outcome.problems:
        out.say("verified")
        return 0
    for problem in outcome.problems:
        out.say(problem)
    return DISAGREES


def make_handler(kind):
    def amend(ns, app, out):
        return report(out, records.replace(app, kind, ns.id, set_pairs(ns.set)))
    return amend


def add_amend(sub, kind, noun, example):
    command = new_command(
        sub, "amend", "Change fields of one %s by replacing the whole record." % noun,
        "Writes to Billit: reads the full %(n)s, changes only the named paths, posts the whole record back, reads it "
        "again and compares every key. A key lost or changed outside the named paths exits 5 with the diff; "
        "--dry-run prints the full request and sends nothing." % {"n": noun},
        example=example, write=True)
    command.add_argument("id", type=int, metavar="ID", help="Id of the %s to amend (required)." % noun)
    command.add_argument("--set", action="append", required=True, metavar="PATH=VALUE",
                         help="Dotted path and new value, repeatable; a number segment indexes a list, and the value "
                              "takes the type the field has now (required).")
    command.set_defaults(handler=make_handler(kind))
