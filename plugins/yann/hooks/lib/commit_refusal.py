import os

from guard_output import CHECK_ID, CHECK_ID_POINTER, acting, emit, log

MAX_SHOWN_PATHS = 6
MAX_SHOWN_LINES = 12
MAX_PATHS_IN_COMMAND = 20


def shown_paths(paths):
    return ", ".join(paths[:MAX_SHOWN_PATHS]) + (" …" if len(paths) > MAX_SHOWN_PATHS else "")


def unstage_command(repo, paths):
    return "`git -C %s restore --staged -- %s`" % (repo, " ".join(paths[:MAX_PATHS_IN_COMMAND]))


def abort_merge_command(repo):
    return "`git -C %s merge --abort`" % repo


def file_section(repo, refused, merged):
    own = [p for p in refused if p not in merged]
    theirs = [p for p in refused if p in merged]
    ways = ""
    if own:
        ways += "  - Unstage them and commit the rest: %s.\n" % unstage_command(repo, own)
    if theirs:
        ways += ("  - The other parent of this merge changed these, so unstaging them here undoes its change: %s. "
                 "Never unstage them inside the merge → abort it (%s). Taking them out of git is the owner's call "
                 "on the branch being merged in: hand them the `git rm --cached` commit for those files, copying "
                 "the files aside first so they stay on disk — landed where this merge reads it, pushed where that "
                 "is a remote's; then merge again.\n" % (shown_paths(theirs), abort_merge_command(repo)))
    return ("[%s] This commit would record this machine's tool configs in %s's history: %s. They are never "
            "committed, whatever the repo.\n\n%s" % (CHECK_ID, os.path.basename(repo), shown_paths(refused), ways))


def pointer_section(repo, pointers, merged):
    named = sorted(pointers)
    at = ["%s:%d" % (p, n) for p in named for n in pointers[p]]
    pointed = ", ".join(at[:MAX_SHOWN_LINES]) + (" …" if len(at) > MAX_SHOWN_LINES else "")
    own = [p for p in named if p not in merged]
    if own == named:
        other = ", or unstage the file and commit the rest: %s" % unstage_command(repo, own)
    elif own:
        other = ("; unstage only a file the other parent of this merge did not change, since unstaging one it "
                 "changed undoes that change: %s" % unstage_command(repo, own))
    else:
        other = "; the other parent of this merge changed the file, so unstaging it would undo that change"
    return ("[%s] This commit records a line in %s that points into this machine's tool configs, which no "
            "teammate has.\n\n"
            "  - Rewrite each such line to name the service filling the role, as `<role> → <service>.`, keeping the rest of the line%s.\n"
            "  - The full rule: /managing-harness , a tool's skill and its config.\n"
            % (CHECK_ID_POINTER, pointed, other))


def log_denial(check, session, repo, shown):
    detail = "%s :: %s" % (os.path.basename(repo), shown)
    if acting(check):
        log(check, session, "deny", detail)
        return True
    log(check, session, "would-deny", detail)
    return False


def deny_commit(session, repo, refused, pointers, merged):
    sections = []
    if refused and log_denial(CHECK_ID, session, repo, shown_paths(refused)):
        sections.append(file_section(repo, refused, merged))
    if pointers and log_denial(CHECK_ID_POINTER, session, repo, shown_paths(sorted(pointers))):
        sections.append(pointer_section(repo, pointers, merged))
    if sections:
        emit("deny", "\n".join(sections))
