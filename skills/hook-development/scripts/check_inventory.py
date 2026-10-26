#!/usr/bin/env python3
"""Enumerate every check id from source by AST, and reconcile against the registry.

WHY AN AST WALK AND NOT A GREP. A regex inventory over one real hook estate reported a
clean bill of health -- 58 found, 1 missing -- while 115 ids were undocumented. The recipe
matched `[ID]` literals and `log(..., "LITERAL")`, so every check reporting through a
VARIABLE was structurally invisible, and that was the dominant emission shape in that
codebase. The audit was blind to exactly the class it existed to find.

This resolves each logging call's id argument back to the literals that can reach it:
literals, names bound to literals (including names bound in several branches), ternaries,
and the elements of a literal collection being iterated. Anything it cannot resolve is
reported SEPARATELY as a dynamic sink -- that population is the honest measure of what the
inventory does not know.

Usage:
    python3 check_inventory.py --src <dir> [--registry <file.md>] \\
                               [--sink log_decision] [--arg 2] [--entry main]

Exit codes:
    0  inventory produced
    1  a reconciliation problem was found and --strict was passed
"""
import argparse
import ast
import os
import re
import sys


# ---------------------------------------------------------------- resolution
class IdResolver(ast.NodeVisitor):
    """Collect string literals that can reach a given argument of a sink call."""

    def __init__(self, sink, arg_index):
        self.sink = sink
        self.arg_index = arg_index
        self.bindings = {}        # name -> set of literals it can hold
        self.static = set()       # ids resolved to literals
        self.dynamic = []         # (lineno, unparsed expression)
        self.calls = 0

    # -- pass 1: learn what names can hold ------------------------------
    def collect_bindings(self, tree):
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                lits = self._literals(node.value)
                if not lits:
                    continue
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        self.bindings.setdefault(target.id, set()).update(lits)
            elif isinstance(node, ast.For):
                # `for cid in ("A", "B"):` binds cid to both
                lits = self._literals(node.iter)
                if lits and isinstance(node.target, ast.Name):
                    self.bindings.setdefault(node.target.id, set()).update(lits)

    def _literals(self, node):
        """Every string literal this expression can evaluate to, best effort."""
        out = set()
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            out.add(node.value)
        elif isinstance(node, (ast.Tuple, ast.List, ast.Set)):
            for e in node.elts:
                out |= self._literals(e)
        elif isinstance(node, ast.IfExp):
            out |= self._literals(node.body) | self._literals(node.orelse)
        elif isinstance(node, ast.BoolOp):
            for v in node.values:
                out |= self._literals(v)
        elif isinstance(node, ast.Dict):
            for v in node.values:
                out |= self._literals(v)
        return out

    # -- pass 2: resolve the sink calls ---------------------------------
    def visit_Call(self, node):
        name = _callee_name(node.func)
        if name == self.sink:
            self.calls += 1
            if len(node.args) > self.arg_index:
                arg = node.args[self.arg_index]
                lits = self._literals(arg)
                if not lits and isinstance(arg, ast.Name):
                    lits = self.bindings.get(arg.id, set())
                if lits:
                    self.static |= lits
                else:
                    self.dynamic.append((node.lineno, _unparse(arg)))
        self.generic_visit(node)


def _callee_name(func):
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        return func.attr
    return None


def _unparse(node):
    try:
        return ast.unparse(node)
    except Exception:
        return "<unparseable>"


# ---------------------------------------------------------------- reachability
def _referenced_names(node):
    """Every function name this subtree CALLS or merely MENTIONS.

    Mentions matter: a check registered in a table and dispatched by iteration
    (`CHECKS = [check_a, check_b]` … `for c in CHECKS: c(ctx)`) is reachable, but a
    call-graph walk that only follows `Call` nodes reports it dead. That false positive is
    worse than no reachability check at all, because the obvious response to it is to
    delete a live check.
    """
    out = set()
    for n in ast.walk(node):
        if isinstance(n, ast.Call):
            name = _callee_name(n.func)
            if name:
                out.add(name)
        elif isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load):
            out.add(n.id)
        elif isinstance(n, ast.Attribute):
            out.add(n.attr)
    return out


def reachable_functions(tree, entries):
    """Functions transitively reachable from the named entry points, module level, or a
    registration table."""
    defs, refs = {}, {}
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            defs[node.name] = node
            refs[node.name] = _referenced_names(node)

    # Seeds: declared entry points, plus everything named at module level (which covers
    # registration tables and decorator application).
    module_level = ast.Module(
        body=[n for n in tree.body
              if not isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))],
        type_ignores=[])
    stack = [e for e in entries if e in defs]
    stack.extend(n for n in _referenced_names(module_level) if n in defs)

    seen = set()
    while stack:
        fn = stack.pop()
        if fn in seen:
            continue
        seen.add(fn)
        stack.extend(c for c in refs.get(fn, ()) if c in defs and c not in seen)
    return seen, set(defs)


# ---------------------------------------------------------------- registry
def registry_ids(path):
    """Ids named in a markdown registry: the first backticked token of a table row."""
    if not path or not os.path.isfile(path):
        return None
    ids = set()
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if not line.lstrip().startswith("|"):
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if not cells:
                continue
            for tok in re.findall(r"`([A-Za-z][\w.-]*)`", cells[0]):
                ids.add(tok)
    return ids


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True, help="directory of hook sources")
    ap.add_argument("--registry", help="markdown registry to reconcile against")
    ap.add_argument("--sink", default="log_decision", help="the logging function name")
    ap.add_argument("--arg", type=int, default=2, help="0-based index of the id argument")
    ap.add_argument("--entry", action="append", default=["main"], help="entry point name")
    ap.add_argument("--exclude", default="tests", help="comma-separated dir names to skip")
    ap.add_argument("--strict", action="store_true", help="exit 1 on any problem")
    args = ap.parse_args()

    skip = {s for s in args.exclude.split(",") if s}
    files = []
    for root, dirs, names in os.walk(args.src):
        dirs[:] = [d for d in dirs if d not in skip and not d.startswith(".")]
        files.extend(os.path.join(root, n) for n in names if n.endswith(".py"))

    all_static, all_dynamic, unreachable, total_calls = set(), [], [], 0

    for path in sorted(files):
        try:
            tree = ast.parse(open(path, encoding="utf-8", errors="replace").read())
        except SyntaxError as e:
            print("  !! %s: syntax error line %s" % (path, e.lineno))
            continue
        r = IdResolver(args.sink, args.arg)
        r.collect_bindings(tree)
        r.visit(tree)
        total_calls += r.calls
        all_static |= r.static
        all_dynamic.extend((path, ln, src) for ln, src in r.dynamic)

        seen, defined = reachable_functions(tree, args.entry)
        for fn in sorted(defined - seen):
            if fn.startswith("_") or fn.startswith("test"):
                continue
            unreachable.append("%s:%s" % (os.path.basename(path), fn))

    print("== inventory ==")
    print("  files scanned          : %d" % len(files))
    print("  %-22s : %d" % ("sink calls", total_calls))
    print("  ids resolved statically : %d" % len(all_static))
    print("  dynamic sinks (invisible to a regex recipe) : %d" % len(all_dynamic))
    for path, ln, src in all_dynamic:
        print("      %s:%s  %s" % (os.path.basename(path), ln, src[:70]))

    print()
    print("  ids: %s" % (", ".join(sorted(all_static)) or "(none)"))

    problems = 0
    reg = registry_ids(args.registry)
    if reg is not None:
        missing = sorted(all_static - reg)
        stale = sorted(reg - all_static)
        print()
        print("== reconciliation ==")
        print("  MISSING from registry (%d): %s" % (len(missing), ", ".join(missing) or "(none)"))
        print("  In registry, NOT found in code (%d): %s" % (len(stale), ", ".join(stale) or "(none)"))
        problems += len(missing) + len(stale)
    else:
        print()
        print("== reconciliation ==  (no --registry given, skipped)")

    print()
    print("== dead checks ==")
    print("  unreachable functions (%d): %s"
          % (len(unreachable), ", ".join(unreachable) if unreachable else "(none)"))
    problems += len(unreachable)

    if args.strict and problems:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
