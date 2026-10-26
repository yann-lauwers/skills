import argparse
import os
import re
import subprocess
import textwrap

EXIT_CODES = """\
Exit codes:
  0  done
  1  Billit or the portal failed
  2  usage or config: no repo, no agents-config, unknown entity
  3  not found
  4  auth: item unresolved, key refused, no portal session
  5  written, but the read-back disagrees (the id is printed)
  6  Billit refused the payload
  7  precondition not met, nothing written
"""


def wrap(text):
    return textwrap.fill(text, 78)


def skill_commit():
    skill = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir, os.pardir)
    try:
        done = subprocess.run(["git", "-C", skill, "rev-parse", "--short", "HEAD"], capture_output=True, text=True,
                              stdin=subprocess.DEVNULL, timeout=5)
    except (OSError, subprocess.SubprocessError):
        return "unknown"
    return done.stdout.strip() if done.returncode == 0 and done.stdout.strip() else "unknown"


class CommitVersion(argparse._VersionAction):
    def __call__(self, parser, namespace, values, option_string=None):
        print("billit %s" % skill_commit())
        parser.exit()


def epilog(example=None):
    head = "Example:\n%s\n\n" % example if example else ""
    return head + EXIT_CODES


def new_command(commands, name, summary, description, example=None, write=False, leaf=True):
    sub = commands.add_parser(name, help=summary, description=wrap(description), epilog=epilog(example),
                              formatter_class=argparse.RawDescriptionHelpFormatter, allow_abbrev=False)
    if leaf:
        common(sub, write)
    return sub


def group(commands, name, summary, description):
    sub = new_command(commands, name, summary, description, leaf=False)
    return sub, sub.add_subparsers(title="commands", metavar="<command>", dest=name + "_command", required=True)


def global_flags(sub, default):
    sub.add_argument("--entity", metavar="KEY", default=default or None,
                     help="Entity whose Billit account is used (default: the index's default entity).")
    sub.add_argument("--root", metavar="DIR", default=default or None,
                     help="Repo root holding the entity register (default: git top level of the current directory).")
    sub.add_argument("--json", action="store_true", default=default or False,
                     help="Print Billit's records as JSON (default: off, print a table).")


def common(sub, write):
    global_flags(sub, argparse.SUPPRESS)
    if write:
        sub.add_argument("--dry-run", action="store_true",
                         help="Print the exact requests and send nothing (default: off, send).")


def day_arg(text):
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", text):
        raise argparse.ArgumentTypeError("%r is not a date as YYYY-MM-DD" % text)
    return text
