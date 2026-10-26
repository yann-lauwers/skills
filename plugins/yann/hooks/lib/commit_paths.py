from git_reads import git, head_paths, lines


def carried(repo, scope, added, unstaged):
    if scope.everything:
        in_head = head_paths(repo)
        unstaged = [p for p in unstaged if p not in in_head]
    staged = [p for p in lines(git(repo, "diff", "--cached", "--name-only", "--no-renames")) if p not in unstaged]
    if scope.paths and not scope.include:
        named = set(lines(git(repo, "diff", "HEAD", "--name-only", "--no-renames", "--", *scope.paths))) \
            | set(lines(git(repo, "diff", "--cached", "--name-only", "--no-renames", "--", *scope.paths)))
        return sorted(named), named
    recorded = set(staged) | set(added)
    from_worktree = set(added)
    if scope.everything:
        swept = set(lines(git(repo, "diff", "--name-only", "--no-renames")))
        recorded |= swept
        from_worktree |= swept
    if scope.paths:
        named = set(lines(git(repo, "diff", "HEAD", "--name-only", "--no-renames", "--", *scope.paths)))
        recorded |= named
        from_worktree |= named
    return sorted(recorded), from_worktree


def recorded_deletions(repo, scope):
    def deleted(*args):
        return {l.split("\t", 1)[1] for l in lines(git(repo, *args)) if l.startswith("D\t")}

    if scope.paths and not scope.include:
        return deleted("diff", "HEAD", "--name-status", "--no-renames", "--", *scope.paths)
    out = deleted("diff", "--cached", "--name-status", "--no-renames")
    if scope.everything:
        out |= deleted("diff", "--name-status", "--no-renames")
    if scope.paths:
        out |= deleted("diff", "HEAD", "--name-status", "--no-renames", "--", *scope.paths)
    return out

