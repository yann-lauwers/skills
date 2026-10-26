import os
import subprocess

GLOSSARY_FILE = "GLOSSARY.md"
MAP_FILE = "GLOSSARY-MAP.md"
ADR_DIRNAME = os.path.join("docs", "adr")
ADR_INDEX_FILE = "README.md"
GIT_DIRNAME = ".git"
MAX_WALK_DEPTH = 40


def repo_root(start_dir):
    current = start_dir
    for _ in range(MAX_WALK_DEPTH):
        if os.path.exists(os.path.join(current, ".git")):
            return current
        parent = os.path.dirname(current)
        if parent == current:
            return None
        current = parent
    return None


def place(abs_path):
    if not abs_path or GIT_DIRNAME in abs_path.split(os.sep):
        return None
    root = repo_root(os.path.dirname(abs_path))
    return (root, abs_path) if root else None


def is_decision_record(name):
    return name.endswith(".md") and name != ADR_INDEX_FILE


def is_owed_canon(rel):
    return (os.path.basename(rel) == GLOSSARY_FILE
            or (is_decision_record(os.path.basename(rel)) and os.path.dirname(rel).endswith(ADR_DIRNAME)))


def is_canon_file(rel):
    return os.path.basename(rel) in (GLOSSARY_FILE, MAP_FILE) or os.path.dirname(rel).endswith(ADR_DIRNAME)


def governing_canon_outermost_first(root, abs_path):
    rel = os.path.relpath(abs_path, root)
    if rel.startswith(".."):
        return []
    directories = [""]
    for part in os.path.dirname(rel).split(os.sep) if os.path.dirname(rel) else []:
        directories.append(os.path.join(directories[-1], part))
    found = []
    for directory in directories:
        glossary = os.path.join(directory, GLOSSARY_FILE)
        if os.path.isfile(os.path.join(root, glossary)):
            found.append(glossary)
        records = os.path.join(directory, ADR_DIRNAME)
        try:
            names = sorted(f for f in os.listdir(os.path.join(root, records)) if is_decision_record(f))
        except OSError:
            names = []
        found.extend(os.path.join(records, name) for name in names)
    return found


def required_canon(root, abs_path):
    if is_canon_file(os.path.relpath(abs_path, root)):
        return []
    return governing_canon_outermost_first(root, abs_path)


def nearest_glossary(root, abs_path):
    glossaries = [c for c in governing_canon_outermost_first(root, abs_path)
                  if os.path.basename(c) == GLOSSARY_FILE]
    return glossaries[-1] if glossaries else "<root>"


def is_ignored(root, abs_path):
    try:
        return subprocess.run(
            ["git", "-C", root, "check-ignore", "-q", abs_path],
            capture_output=True, timeout=5,
        ).returncode == 0
    except Exception:
        return False


def owed_unless_ignored(root, abs_path, missing):
    return [] if missing and is_ignored(root, abs_path) else missing
