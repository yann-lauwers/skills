#!/usr/bin/env python3
import json
import os
import re
import subprocess
import sys
from typing import Dict, List, NamedTuple, Optional

import config_levels

TOP_LEVEL = ("status", "secret")
MISSING = object()
SYSTEM_INTERPRETERS = ("/opt/homebrew/bin/python3", "/usr/local/bin/python3", "/usr/bin/python3")
REEXEC_MARK = "_AGENTS_CONFIG_REEXEC"


class FrontmatterInvalid(Exception):
    def __init__(self, path, error):
        super().__init__(path, error)
        self.path, self.error = path, error


class DefaultsInvalid(Exception):
    def __init__(self, path, kind):
        super().__init__(path, kind)
        self.path, self.kind = path, kind


class Merged(NamedTuple):
    values: Dict[str, object]
    origin: Dict[str, str]
    role: Optional[str]


def die(verb, msg, code):
    print("agents-config %s: %s" % (verb, msg), file=sys.stderr)
    sys.exit(code)


def version_order(name):
    parts = name.split(".")
    if all(p.isdigit() for p in parts):
        return (1, tuple(int(p) for p in parts), "")
    return (0, (), name)


def interpreter_candidates(environ, home, system=SYSTEM_INTERPRETERS) -> List[str]:
    found = [environ.get("AGENTS_CONFIG_PYTHON", "")]
    pyenv_root = environ.get("PYENV_ROOT") or os.path.join(home, ".pyenv")
    try:
        with open(os.path.join(pyenv_root, "version"), encoding="utf-8") as f:
            found += [os.path.join(pyenv_root, "versions", v.strip(), "bin", "python3")
                      for v in f.read().split() if v.strip()]
    except OSError:
        pass
    versions = os.path.join(pyenv_root, "versions")
    if os.path.isdir(versions):
        found += [os.path.join(versions, v, "bin", "python3")
                  for v in sorted(os.listdir(versions), key=version_order, reverse=True)]
    found += list(system)
    seen, out = set(), []
    for p in found:
        if p and os.access(p, os.X_OK) and p != sys.executable and p not in seen:
            seen.add(p)
            out.append(p)
    return out


def ensure_yaml(script_path, argv, verb, system=SYSTEM_INTERPRETERS):
    try:
        __import__("yaml")
        return
    except ImportError:
        pass
    tried = [sys.executable]
    if not os.environ.get(REEXEC_MARK):
        for py in interpreter_candidates(os.environ, config_levels.HOME, system):
            tried.append(py)
            if subprocess.run([py, "-c", "import yaml"], capture_output=True).returncode == 0:
                os.environ[REEXEC_MARK] = "1"
                os.execv(py, [py, os.path.abspath(script_path)] + list(argv))
    die(verb, "needs PyYAML, and no interpreter tried has it: " + ", ".join(tried)
        + " (AGENTS_CONFIG_PYTHON names one)", 2)


def frontmatter(path, strict):
    import yaml
    try:
        text = open(path, encoding="utf-8").read()
    except OSError:
        return None
    m = re.match(r"^---\n(.*?)\n---", text, re.S)
    if not m:
        return None
    try:
        data = yaml.safe_load(m.group(1))
    except yaml.YAMLError as e:
        if strict:
            raise FrontmatterInvalid(path, e)
        return None
    return data if isinstance(data, dict) else None


def merged(tool, project_path, strict=False):
    floor_path = os.path.join(config_levels.FLOOR_DIR, tool + ".md")
    floor = frontmatter(floor_path, strict)
    proj = frontmatter(project_path, strict) if project_path else None
    if floor is None and proj is None:
        return None
    values, origin = {}, {}
    for level, fm, path in (("floor", floor, floor_path), ("project", proj, project_path)):
        if not fm:
            continue
        for k in TOP_LEVEL:
            if k in fm:
                values[k], origin[k] = fm[k], level
        defaults = fm.get("defaults")
        if defaults is None:
            defaults = {}
        if not isinstance(defaults, dict):
            raise DefaultsInvalid(path, type(defaults).__name__)
        for k, v in defaults.items():
            values.setdefault("defaults", {})[k] = v
            origin["defaults." + k] = level
    return Merged(values, origin, (proj or {}).get("role") or (floor or {}).get("role"))


def lookup(found, dotted, nested=True):
    parts = dotted.split(".") if nested else [dotted]
    first = parts[0]
    if first in TOP_LEVEL:
        if first not in found.origin:
            return MISSING, None
        cur, origin = found.values[first], found.origin[first]
    else:
        path = "defaults." + first
        if path not in found.origin:
            return MISSING, None
        cur, origin = found.values["defaults"][first], found.origin[path]
    for part in parts[1:]:
        if not isinstance(cur, dict) or part not in cur:
            return MISSING, None
        cur = cur[part]
    return cur, origin


def render(value):
    return value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, default=str)
