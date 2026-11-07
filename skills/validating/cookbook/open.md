# Open a run

1. Resolve the slice: the id named, else the ticket id in the branch name, else the slug the request states; none → ask. Its base is `git merge-base HEAD <ref>`, `<ref>` the one named, else `origin/HEAD`. Whether it is owed comes from the ticket and `git diff --stat <base>..HEAD`.
   Done when the slice, HEAD's hash and the base's hash are noted.
2. Check the tree: `git status --porcelain` prints nothing, and `git log <base>..HEAD` holds the slice's commits. Otherwise name what is uncommitted or missing, and stop.
3. Dispatch the run as a background subagent. Its brief opens `Skills: validating`, then carries the slice, the worktree, the commit, the base, the report directory, every standing owner criterion in the owner's words, and what this conversation knows that the ticket does not.
   Standing owner criteria: the `owner` rows of the newest `run.md` with a verdict line, plus this conversation's, less any the owner withdrew.
4. Hold the tree: no edit, commit, setup or test run in the worktree until the agent returns.
5. Relay the verdict line at the head of the run's `run.md`, then the agent's final reply whole. No verdict line → report the run unfinished.
   - Each ask → the owner. The answer → a ticket comment naming the criterion it settles; no ticket → it joins the next brief's owner criteria.
   - Stop every process the reply names as still running.
6. Blocked on a dev server the repo's `AGENTS.md` declares → start it once by the command it names. Its health check answers within 5 minutes → dispatch again from step 3; otherwise stop it and relay. Every later relay names each server this step left running.
7. A fix lands as a new commit → again from step 2; the new run proves every criterion at that commit.
