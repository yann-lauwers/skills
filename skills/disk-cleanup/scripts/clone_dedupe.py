import hashlib
import os
import subprocess
import sys
from collections import defaultdict

MIN_BYTES = 64 * 1024
apply = "--apply" in sys.argv
roots = [a for a in sys.argv[1:] if a != "--apply"]

by_size = defaultdict(list)
for root in roots:
    for dirpath, _, files in os.walk(root):
        for name in files:
            path = os.path.join(dirpath, name)
            if os.path.islink(path):
                continue
            size = os.path.getsize(path)
            if size >= MIN_BYTES:
                by_size[size].append(path)


def digest(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


saved = 0
replaced = 0
for size, paths in by_size.items():
    if len(paths) < 2:
        continue
    by_hash = defaultdict(list)
    for p in paths:
        by_hash[digest(p)].append(p)
    for group in by_hash.values():
        source = group[0]
        for target in group[1:]:
            saved += size
            replaced += 1
            if not apply:
                continue
            st = os.stat(target)
            tmp = target + ".clonetmp"
            subprocess.run(["cp", "-c", source, tmp], check=True)
            if digest(tmp) != digest(source):
                os.remove(tmp)
                raise SystemExit(f"clone mismatch: {target}")
            os.chmod(tmp, st.st_mode)
            os.utime(tmp, ns=(st.st_atime_ns, st.st_mtime_ns))
            os.replace(tmp, target)

mode = "cloned" if apply else "would clone"
print(f"{mode} {replaced} files, {saved / 1e9:.2f} GB shared")
