import os
import sys

ROOT = "/System/Volumes/Data"
HOME = ROOT + os.path.expanduser("~")
GB = 1048576

sizes = {}
for line in open(sys.argv[1]):
    kb, path = line.rstrip("\n").split("\t", 1)
    sizes[path] = int(kb)

scan_roots = {line.strip() for line in open(sys.argv[2]) if line.strip()}
for root in scan_roots:
    kb = sizes.get(root, 0)
    parent = os.path.dirname(root)
    while parent.startswith(ROOT):
        if parent not in scan_roots:
            sizes[parent] = sizes.get(parent, 0) + kb
        if parent == ROOT:
            break
        parent = os.path.dirname(parent)

shown = {path: kb for path, kb in sizes.items() if kb >= GB}
children = {path: [] for path in shown}
for path in shown:
    if path == ROOT:
        continue
    parent = os.path.dirname(path)
    while parent not in shown:
        parent = os.path.dirname(parent)
    children[parent].append(path)


def gb(kb):
    return f"{kb / GB:6.1f}"


def label(path, parent):
    if parent is None:
        return "/ (Data volume)"
    if path.startswith(HOME) and not parent.startswith(HOME):
        return "~" + path[len(HOME):]
    return path[len(parent):]


row = 0


def walk(path, parent, depth):
    global row
    while len(children[path]) == 1 and shown[path] - shown[children[path][0]] < GB // 10:
        path = children[path][0]
    row += 1
    kids = sorted(children[path], key=lambda kid: -shown[kid])
    other = shown[path] - sum(shown[kid] for kid in kids)
    other_col = gb(other) if kids else " " * 6
    print(f"{row:4d} {gb(shown[path])} {other_col}  {'  ' * depth}{label(path, parent)}")
    for kid in kids:
        walk(kid, path, depth + 1)


print("   #     GB  other  folder   (other = files outside its 1 GB+ subfolders)")
walk(ROOT, None, 0)
