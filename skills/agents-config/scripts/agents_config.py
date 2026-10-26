#!/usr/bin/env python3
import argparse
import functools
import json
import os
import subprocess
import sys
import textwrap

import config_levels
import config_merge
from config_levels import Foreign, RoleUnresolved, declares
from config_merge import MISSING, TOP_LEVEL

VERSION = "1.0.0"
PROG = "agents-config"
ISSUES = "https://github.com/yann-lauwers/skills/issues"


def version_line():
    checkout = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
    try:
        done = subprocess.run(["git", "-C", checkout, "rev-parse", "--short", "HEAD"], capture_output=True,
                              text=True, stdin=subprocess.DEVNULL, timeout=5)
    except (OSError, subprocess.SubprocessError):
        return "%s %s" % (PROG, VERSION)
    sha = done.stdout.strip()
    if done.returncode != 0 or not sha:
        return "%s %s" % (PROG, VERSION)
    return "%s %s (skills %s)" % (PROG, VERSION, sha)


class CommitVersion(argparse._VersionAction):
    def __call__(self, parser, namespace, values, option_string=None):
        print(version_line())
        parser.exit()


def wrap(text):
    return textwrap.fill(text, 78)


TOP_DESCRIPTION = wrap(
    "Answers which tool fills a role in this repo, and what that tool's settings are: the repo's "
    "config read over the user's floor, key by key. It reads no credentials and writes nothing; "
    "it only reads the config files under docs/agents/integrations/ in the repo and "
    "~/.claude/skills/agents-config/integrations/.")

TOP_EPILOG = """\
Examples:
  # The branch git work in this repo is based on
  agents-config get git base_branch

  # One setting of whichever tool fills the vault role
  agents-config get --role vault vault_root

  # Which config declares the tracker role, read from another checkout
  agents-config role tracker --root ~/Code/x

  # Every tool that sets home.url, as JSON
  agents-config list --key home.url --json

Exit codes:
  0  answered
  1  unset: the tool or key is set at neither level, or no config declares the role
  2  usage error, malformed config, or no PyYAML found
  3  --role resolves to no single tool
  4  refused: the repo config is tracked by git, or git could not say

Support: %s
Config shape and resolution: ~/.claude/skills/agents-config/SKILL.md
""" % ISSUES

RESOLVE_EPILOG = """\
Exit codes:
  0  printed
  2  usage error
  4  refused: the repo config is tracked by git, or git could not say

Example:
  agents-config resolve git --root ~/Code/x
"""

ROLE_EPILOG = """\
Exit codes:
  0  printed, repo configs first
  1  no config declares the role
  2  usage error
  4  refused: the repo config is tracked by git, or git could not say

Example:
  agents-config role tracker --root ~/Code/x
"""

GET_EPILOG = """\
Exit codes:
  0  printed
  1  the key is set at neither level, or the tool has no config at either
  2  usage error, malformed config, or no PyYAML found
  3  --role resolves to no single tool
  4  refused: the repo config is tracked by git, or git could not say

Example:
  agents-config get git base_branch
"""

LIST_EPILOG = """\
Exit codes:
  0  scanned, whether or not any tool matched; a config whose defaults is not a map is skipped and named on stderr
  2  usage error, or no PyYAML found
  4  refused: the repo config is tracked by git, or git could not say

Example:
  agents-config list --key home.url --json
"""


def add_level_flags(sub):
    sub.add_argument("--root", metavar="DIR", default=None,
                     help="Directory whose repo config is read (default: the current directory).")
    sub.add_argument("--floor-only", action="store_true",
                     help="Ignore the repo's config and read only the user floor (default: off).")


def new_command(commands, name, summary, description, epilog):
    sub = commands.add_parser(name, help=summary, description=wrap(description), epilog=epilog,
                              formatter_class=argparse.RawDescriptionHelpFormatter, allow_abbrev=False)
    sub.set_defaults(page=sub)
    return sub


def build_parser():
    parser = argparse.ArgumentParser(
        prog=PROG, description=TOP_DESCRIPTION, epilog=TOP_EPILOG, allow_abbrev=False,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--version", action=CommitVersion, help="Print the version and the commit of this checkout, then exit.")
    commands = parser.add_subparsers(title="commands", metavar="<command>", dest="command", required=True)

    resolve = new_command(
        commands, "resolve", "Print where a tool's config files are.",
        "Print the config paths for a tool, the repo's first and then the user floor's, each marked "
        "present or absent.", RESOLVE_EPILOG)
    resolve.add_argument("tool", nargs="?", help="Tool name, such as git (required).")
    resolve.add_argument("--explicit", metavar="VALUE", default=None,
                         help="A config path the caller already chose, echoed on the explicit= line "
                              "(default: none).")
    add_level_flags(resolve)

    role = new_command(
        commands, "role", "Print the configs that declare a role.",
        "Print every config that declares the given role, the repo's first and then the user floor's, "
        "one project= or floor= line each.", ROLE_EPILOG)
    role.add_argument("role", nargs="?", help="Role name, such as tracker (required).")
    add_level_flags(role)

    get = new_command(
        commands, "get", "Print a tool's merged settings.",
        "Print a tool's effective config: the repo's keys over the user floor's, key by key. With a key it "
        "prints that one value, a string as it is and anything else as JSON; without one it prints the "
        "whole config as JSON. With --json a key prints one JSON object that also names the tool, its role "
        "and the level that supplied the value. With --role the one positional is the key, since --role names the "
        "tool.", GET_EPILOG)
    get.add_argument("tool", nargs="?", help="Tool name, such as git (required unless --role is given; with --role it is not allowed).")
    get.add_argument("key", nargs="?",
                     help="Setting to print: status, secret or a defaults key (default: the whole config).")
    get.add_argument("--role", metavar="ROLE", default=None,
                     help="Use the tool that fills this role instead of naming one (default: none, "
                          "name the tool).")
    output = get.add_mutually_exclusive_group()
    output.add_argument("--show-origin", action="store_true",
                        help="Prefix the value with the level that supplied it and a tab (default: off).")
    output.add_argument("--json", action="store_true",
                        help="Print the value as one JSON object with tool, role, key, value and origin "
                             "(default: off, print the value as it is).")
    add_level_flags(get)

    listing = new_command(
        commands, "list", "Print every tool whose config carries a key.",
        "Print one row for every tool whose merged config carries the key, sorted by tool name: tool, "
        "role and value, tab-separated, or a JSON array with --json.", LIST_EPILOG)
    listing.add_argument("--key", metavar="KEY", default=None,
                         help="Dotted key to look for, such as status or home.url (required).")
    listing.add_argument("--json", action="store_true",
                         help="Print a JSON array of rows instead of tab-separated text (default: off).")
    add_level_flags(listing)
    return parser


def positionals(sub, ns, extras, names):
    words = [getattr(ns, n) for n in names if getattr(ns, n) is not None]
    words += [e for e in extras if not e.startswith("-")]
    flags = [e for e in extras if e.startswith("-")]
    if flags:
        sub.error("unrecognized arguments: " + " ".join(flags))
    return words


def run_resolve(ns, extras, argv):
    words = positionals(ns.page, ns, extras, ("tool",))
    if len(words) != 1:
        ns.page.error("exactly one tool is required")
    return config_levels.resolve(
        {"key": words[0], "root": ns.root, "explicit": ns.explicit, "floor_only": ns.floor_only})


def run_role(ns, extras, argv):
    words = positionals(ns.page, ns, extras, ("role",))
    if len(words) != 1:
        ns.page.error("exactly one role is required")
    return config_levels.role({"key": words[0], "root": ns.root, "explicit": None, "floor_only": ns.floor_only})


def run_get(ns, extras, argv):
    die = functools.partial(config_merge.die, "get")
    words = positionals(ns.page, ns, extras, ("tool", "key"))
    role = ns.role
    if role:
        if len(words) > 1:
            ns.page.error("--role names the tool; drop <tool> or --role")
        tool, key = None, (words[0] if words else None)
        extra = []
    else:
        tool, key = (words + [None, None])[:2]
        extra = words[2:]
    if extra:
        ns.page.error("unexpected argument " + extra[0])
    if not tool and not role:
        ns.page.error("a tool or --role is required")
    config_merge.ensure_yaml(os.path.abspath(__file__), argv, "get")

    try:
        configs = config_levels.project(ns.root or os.getcwd(), ns.floor_only).configs
        if role:
            tool = config_levels.pick_role(role, configs)
        found = configs.get(tool)
        if found and role and not declares(found.path, role):
            found = None
        if isinstance(found, Foreign):
            raise found
    except Foreign as f:
        config_levels.refuse("get", f)
    except RoleUnresolved as r:
        if r.hits:
            die("%d %s configs declare role %s: %s — name the tool" % (
                len(r.hits), r.level, role, ", ".join(r.hits)), 3)
        die("no config declares role %s" % role, 3)

    try:
        found_config = config_merge.merged(tool, found.path if found else None, strict=True)
    except config_merge.FrontmatterInvalid as e:
        die("%s: frontmatter is not valid YAML: %s" % (e.path, e.error), 2)
    except config_merge.DefaultsInvalid as e:
        die("%s: defaults is a %s, want a map" % (e.path, e.kind), 2)
    if found_config is None:
        die("%s has no config at either level" % tool, 1)

    if key is None:
        out = {"tool": tool, "role": found_config.role,
               **{k: found_config.values[k] for k in TOP_LEVEL if k in found_config.values},
               "defaults": found_config.values.get("defaults", {}), "origin": found_config.origin}
        print(json.dumps(out, indent=2, ensure_ascii=False, default=str))
        return 0

    value, where = config_merge.lookup(found_config, key, nested=False)
    if value is MISSING:
        die("%s sets no %s at either level" % (tool, key), 1)
    if ns.json:
        print(json.dumps({"tool": tool, "role": found_config.role, "key": key, "value": value, "origin": where},
                         ensure_ascii=False, default=str))
        return 0
    print(("%s\t" % where if ns.show_origin else "") + config_merge.render(value))
    return 0


def run_list(ns, extras, argv):
    words = positionals(ns.page, ns, extras, ())
    if words:
        ns.page.error("unexpected argument " + words[0])
    if not ns.key:
        ns.page.error("--key is required")
    config_merge.ensure_yaml(os.path.abspath(__file__), argv, "list")

    try:
        configs = config_levels.project(ns.root or os.getcwd(), ns.floor_only).configs
    except Foreign as f:
        config_levels.refuse("list", f)
    tools = sorted(set(config_levels.floor_tools()) | set(configs))

    rows = []
    for tool in tools:
        found = configs.get(tool)
        if isinstance(found, Foreign):
            config_levels.refuse("list", found)
        try:
            found_config = config_merge.merged(tool, found.path if found else None)
        except config_merge.DefaultsInvalid as e:
            print("agents-config list: %s: defaults is a %s, want a map; skipped" % (e.path, e.kind),
                  file=sys.stderr)
            continue
        if found_config is None:
            continue
        value, origin = config_merge.lookup(found_config, ns.key)
        if value is MISSING:
            continue
        rows.append({"tool": tool, "role": found_config.role, "key": ns.key, "value": value, "origin": origin})

    if ns.json:
        print(json.dumps(rows, ensure_ascii=False, default=str))
    else:
        for row in rows:
            print("%s\t%s\t%s" % (row["tool"], row["role"] or "", config_merge.render(row["value"])))
    return 0


HANDLERS = {"resolve": run_resolve, "role": run_role, "get": run_get, "list": run_list}


def main(argv):
    argv = list(argv)
    ns, extras = build_parser().parse_known_args(argv)
    return HANDLERS[ns.command](ns, extras, argv)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
