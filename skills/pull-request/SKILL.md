---
name: pull-request
description: "Governs opening, retargeting, readying, describing and merging a pull request — its base, assignee, draft state, body and who merges. Use on 'open a PR', 'PR my changes', 'update the PR description', 'retarget the PR', 'mark ready for review', 'approve PR', 'merge the PR', 'wrap up <ticket>'; also before a `gh pr create|edit|ready|merge`, or a rebase or force-push of a branch other PRs merge into. Not for the `git` and `gh` invocations — /git and /github ; not for a watcher verdict — /watch-pr ."
---

# Pull requests

- Every value → the merged git config /git , § Project config resolves, never `git config`; `auto` → /git , § Project config.
- A project git config that omits a key → the floor answers it; never ask the user for it.
- No project git config → /git , § Project config.
- Approving, commenting, requesting changes → the commands are the model's own; load /voice before drafting a comment (unavailable → say so, and match the thread's voice).

## Routing

| Task | Read |
| --- | --- |
| The merged config names `cluster_base_source` or `integration_bases` — which base a new pull request takes, founding or retiring an integration base | /pr-cluster |
| Merging — the actor for this pull request's base, and what a person-held merge hands over | `references/merge-preflight.md` |
| Rules 5 and 6 asked as data | `scripts/pr_policy.py --help` |
| Anything else about a pull request | the rules below; none fits → name the closest row |

## The rules

1. Assigned to whoever opens it, opened ready for review → `pr_assignee` and `pr_draft` carry the values, a draft the invoking skill asks for opening as a draft; pass `@me`, never a handle; omit the assignee only where it is `null`; an unassigned one found → repair it; no reviewer unless the user names one.
2. A stack base the invoking skill passes → that branch; else the config names `cluster_base_source` → /pr-cluster , `references/child-base.md`; else `base_branch`; an integration base only while live (/pr-cluster , `references/child-base.md` § Liveness), a spent one falls to the next route.
   - `production_branch` is a base only where the user names it — by name, "production" or "release", never another branch sharing the word; a ticket naming it names no branch; ambiguous → `base_branch` · `production_branch` equal to `base_branch` → this bullet changes nothing.
3. Consent to a production deploy is given at the merge, never at opening, retargeting or naming a reviewer; rule 5's actor decides whether the run merges; `agent` → the config value is the deploy's only consent.
4. A ticket's pull request opens only for work that ticket describes → check the diff against the ticket's stated scope; mismatch → surface it and stop.
5. Who merges depends on the target base → `merge_actor_by_base`, then `merge_actor`, per `references/merge-preflight.md`.
6. An integration base — any branch several children merge into before the trunk, in `integration_bases` or not — takes its base by merge, never rebase or force push → `scripts/pr_policy.py may-rewrite --repo <checkout> --branch <branch>`: only `allow` rebases; `refuse` · `unknown` take the merge; merging the base retires it → /pr-cluster , `cookbook/retire.md`.
7. A stack lands bottom-up, one pull request at a time; each branch above is rebased onto the trunk once the one below merges.
8. Who acts on each watcher verdict → /watch-pr 's verdict table.
9. A body cites no local path — reports, vault, a local file, a workspace artifact → copy useful content inline.
10. Retarget only onto a base that exists and somebody chose — an integration base cut after its children opened, a stack's tip once the branch below merged; a pull request open when its integration base is cut → retarget it.
11. The body → invoke /pr before drafting and follow its template whole; the title stays under 70 characters, Conventional Commits welcome, never required.
   - The ticket, where one exists → cited on the body's first line, in the form the repo's pull request template uses on its line naming an issue identifier; no template, or none naming one → the bare identifier.
   - A note another skill or rule sends into the body → inside the template section its subject belongs to; none fits → one `##` section per sending skill or rule, headed by the note's subject, after `## Merge Danger`.
12. A draft is flipped ready → asking for it green, merge-ready, reviewed or watched authorizes the flip, except a promotion pull request, which only /pr-cluster 's ship readies; a skill the user typed readies it at its own step; otherwise a draft stays one until the user asks.
13. A branch with an open pull request is updated, never opened again → `gh pr list --head <branch> --state open` before drafting a body or pushing; a merged one is no hit; a hit → refuse, naming its number, base and draft state, then update it.
14. Asked to update a pull request and its ticket together → draft the body once, per rule 11, and write the two in parallel:
   - The ticket → the one the request names, else the one the branch's identifier matches; neither → ask.
   - Its tracker's skill → the `tool:` of the config whose `project=` line `~/.claude/skills/agents-config/scripts/agents-config role tracker --root <the parent of git rev-parse --git-common-dir>` prints; no `project=` line → the body alone, and say the repo's tracker is unwired.
   - The body, without its ticket line and with each `##` heading demoted to `###`, forms one `## Implementation summary` section, running to the next line opening `# ` or `## `, or the description's end.
   - That section replaces its earlier copy in the ticket's description, else goes below its `---` at the end; no `---` → a `---` and the section after the description's last line; the rest of the description stays byte for byte.
