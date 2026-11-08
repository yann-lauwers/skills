import argparse
import contextlib

from .client import Billit
from .commands import account, bank, catalogue, files, orders, parties, queue, raw, timereg
from .errors import AUTH, USAGE, Fail
from .render import Out
from .runtime import Runtime
from .surface import CommitVersion, EXIT_CODES, global_flags, wrap

MODULES = (account, orders, parties, bank, queue, files, timereg, catalogue, raw)

DESCRIPTION = wrap(
    "Operates the Billit account whose API key BILLIT_API_KEY holds, through its JSON API and its web portal. "
    "Reads print a table or, with --json, Billit's records; writes send unless --dry-run asks for the exact "
    "requests instead. The key is never printed.")

EXAMPLES = """\
Examples:
  # Prove the key and list the enabled features
  billit whoami

  # Cost orders since September, as JSON
  billit orders list --direction cost --since 2026-09-01 --json

  # Preview a header change on a booked order, sending nothing
  billit orders amend 130356834 --set Comments=x --dry-run

"""


def build_parser():
    parser = argparse.ArgumentParser(
        prog="billit", description=DESCRIPTION, epilog=EXAMPLES + EXIT_CODES, allow_abbrev=False,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--version", action=CommitVersion, help="Print the commit of the skill checkout, then exit.")
    global_flags(parser, None)
    commands = parser.add_subparsers(title="commands", metavar="<command>", dest="command", required=True)
    for module in MODULES:
        module.register(commands)
    return parser


def main(argv, rt):
    parser = build_parser()
    try:
        with contextlib.redirect_stdout(rt.stdout), contextlib.redirect_stderr(rt.stderr):
            ns = parser.parse_args(argv)
    except SystemExit as stop:
        return stop.code if isinstance(stop.code, int) else USAGE
    out = Out(rt.stdout, rt.stderr, getattr(ns, "json", False))
    try:
        key = rt.env.get("BILLIT_API_KEY")
        if not key:
            raise Fail(AUTH, "BILLIT_API_KEY is unset")
        app = Billit(rt, key, out, getattr(ns, "dry_run", False))
        return ns.handler(ns, app, out) or 0
    except Fail as fail:
        out.note("billit: %s" % fail.message)
        return fail.code


def run(argv):
    return main(argv[1:], Runtime.live())
