import subprocess

GIT_TIMEOUT = 5


def git(repo, *args):
    try:
        done = subprocess.run(("git", "-C", str(repo)) + args, capture_output=True, text=True, timeout=GIT_TIMEOUT)
    except Exception:
        return None
    return done.stdout if done.returncode == 0 else None


def lines(out):
    return [line for line in (out or "").splitlines() if line.strip()]


def head_paths(repo):
    return set(lines(git(repo, "ls-tree", "-r", "--full-tree", "--name-only", "HEAD")))


def blobs_at(repo, rev):
    blobs = {}
    for row in lines(git(repo, "ls-tree", "-r", "--full-tree", rev)):
        meta, _, path = row.partition("\t")
        parts = meta.split()
        if path and len(parts) >= 3:
            blobs[path] = parts[2]
    return blobs
