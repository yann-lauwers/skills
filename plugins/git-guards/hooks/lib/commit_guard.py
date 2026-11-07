import os

from commit_command import commit_scope, would_add, would_unstage
from commit_paths import carried, recorded_deletions
from commit_refusal import deny_commit
from git_reads import git, head_paths
from merge_commit import merge_base_blobs, merge_head_blobs, other_parent_changes
from pointer_lines import added_pointers
from tool_config_paths import POINTER, is_tool_config


def index_edits_earlier_on_line(repo, calls):
    added, unstaged, removed = [], set(), set()
    for other, sub, other_args in calls:
        if os.path.realpath(other) != os.path.realpath(repo):
            continue
        if sub == "add":
            added += would_add(repo, other_args) or []
        elif sub in ("restore", "rm", "reset"):
            gone = would_unstage(repo, sub, other_args)
            if gone is None:
                unstaged = set()
            elif sub == "rm":
                in_head = head_paths(repo)
                added += [p for p in gone if p in in_head]
                removed |= {p for p in gone if p in in_head}
                unstaged |= {p for p in gone if p not in in_head}
            else:
                unstaged |= set(gone)
    return added, unstaged, removed


def judge_commit(session, repo, args, calls):
    top = (git(repo, "rev-parse", "--show-toplevel") or "").strip()
    if not top:
        return False
    scope = commit_scope(args)
    if scope.dry_run:
        return False
    added, unstaged, removed = index_edits_earlier_on_line(repo, calls)
    merge_head = merge_head_blobs(repo)
    leaving = removed | recorded_deletions(repo, scope)
    in_head = head_paths(repo)
    walked, from_worktree = carried(repo, scope, added, sorted(unstaged))
    walked = [p for p in walked if p not in leaving]
    refused = [p for p in walked if is_tool_config(p)]
    pool = [p for p in walked if p not in refused and POINTER.governs(p)]
    pointers = added_pointers(top, POINTER, pool, from_worktree, in_head, set(merge_head))
    if not (refused or pointers):
        return False
    base = merge_base_blobs(top) if merge_head else {}
    deny_commit(session, repo, refused, pointers, other_parent_changes(repo, merge_head, base))
    return True


def judge_commits(session, commits, calls):
    return any(judge_commit(session, repo, args, calls) for repo, args in commits)
