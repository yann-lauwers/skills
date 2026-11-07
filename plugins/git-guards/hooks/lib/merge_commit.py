import os

from git_reads import blobs_at, git


def merge_head_blobs(repo):
    if not os.path.isfile(os.path.join(repo, ".git", "MERGE_HEAD")) and git(
        repo, "rev-parse", "--verify", "--quiet", "MERGE_HEAD"
    ) is None:
        return {}
    return blobs_at(repo, "MERGE_HEAD")


def merge_base_blobs(repo):
    rev = (git(repo, "merge-base", "HEAD", "MERGE_HEAD") or "").strip()
    return blobs_at(repo, rev) if rev else {}


def other_parent_changes(repo, merge_head, base):
    if not merge_head:
        return set()
    head = blobs_at(repo, "HEAD")
    paths = set(merge_head) | set(head) | set(base)
    if base:
        changed = {p for p in paths if merge_head.get(p) != base.get(p) and merge_head.get(p) != head.get(p)}
    else:
        changed = {p for p in merge_head if merge_head[p] != head.get(p)}
    return changed

