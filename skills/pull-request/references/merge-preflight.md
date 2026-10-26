# Before merging — resolving who closes this pull request

## The actor is a lookup, per target base

- Read it with `~/.claude/skills/pull-request/scripts/pr_policy.py merge-actor --repo <checkout> --base <base>`, which reads the repo's project git config first, then the user-level floor — never from `git config`, where a same-named key answers with a different value.
- The base is the pull request's own target base, its `baseRefName` → never the branch the work was cut from.
- The script resolves `merge_actor_by_base` patterns and the per-level order → take its answer as given, never re-derive it.
- A project file the config gate refuses, an unreadable one included → the actor is `unknown`, never the floor's, `--floor-only` included: report the gate's refusal with no packet; Yann decides on the file · a base read and `unknown` with nothing on stderr → the value the script resolved is not `agent`, `agent-after-approval` or `person` — a misspelt actor or a literal `null` included — no file names one, or the script failed: report each file's `merge_actor` / `merge_actor_by_base` lines as written, no packet; Yann decides on the files.
- No base comes back → the actor is unestablished, never the scalar's: re-read it; still unread → the merge is the person's, per § What each value does.

## Merging an integration base

- The pull request's head is an integration base → its merge retires it: /pr-cluster , `cookbook/retire.md`, whose steps run around this merge.

## A merge onto the production branch

- The base is the merged config's `production_branch` → the merge is the deploy.
- Before merging it itself, the run prints the line read off the pull request at merge time, never off the worktree or the request: `<baseRefName> ← <headRefName>: merging it deploys to production` — then the project config's release warning where its body carries one.

## What each value does

- `agent` → the session that opened the pull request merges it unasked.
- `agent-after-approval` · `person` → the merge is the person's: hand over the packet below as its one-sender line says, a statement, never a question; end the turn and leave the pull-request watcher armed; its `MERGED` line is how the merge is observed; a session ending first → the next re-arms it from the handoff; settle the ticket once it arrives.
- A reply that reads like approval is not the merge → the merge hook refuses this session's own merge on both values, whatever came back.
- `agent-after-approval` → the person decides on the packet · `person` → they read the diff itself · an actor unestablished by an unread base → as `person`. The packet says which.
- The person is the user these sessions run for → a repo whose config gives the merge to someone else (a contribution to a remote the user does not own) still hands the packet to the user, per the one-sender line, naming whose merge it is.

## The packet a person-held merge hands over

- Six items, in the turn that hands over: the resolved actor (or "unestablished") and what it asks of them · the proof's verdict · the criteria carrying it · the report's directory · the pull request's URL · the merge command written out; /validating never ran on this head → the three proof items each read `not validated`.
- A seventh where the base is `production_branch` → the deploy line from § A merge onto the production branch.
- An eighth where the head is an integration base → /pr-cluster , `cookbook/retire.md`: step 1's child list read now, step 3's delete written out, and that the next founding's backstop retires whatever they leave standing.
- One sender per pull request: a detached session sends it through the messaging role's self-notification channel · an attended session hands it over in its turn.

## The machine loop closed first

- The current head is clean before any of the above → checks green, zero unresolved review-bot threads on it, and the pull request reports itself mergeable with a clean merge state → `~/.claude/skills/watch-pr/scripts/watch-pr.py --repo <owner/name> --pr <N> --once` answers `CLEAN`.
- A red or pending check is the finding → never route around it.
