# Push

## No-op guard

- Level with upstream and a clean tree, per the status in hand or `git status -sb` → skip the push and report the no-op.

## On push failure

- Non-fast-forward on a plain push → § Non-fast-forward rejection; never auto-pull, auto-rebase or auto-force.
- `--force-with-lease` refused (`stale info`) → the remote moved; report the refusal with the diverging commits (`git log --oneline HEAD..origin/<branch>`) and let the user decide.
- `Connection to <host> closed by remote host.`, then exit 141, remote head unmoved → § A slow pre-push hook over SSH.

## Force push policy

- Every authorized rewrite → `--force-with-lease`; approval to rewrite is approval for the lease form, never the bare `--force`.
- A rebase this session performed, verified per /git § Rewrites → `git push --force-with-lease` in the same turn; the instruction authorizing the rebase authorizes this push.
- Any other rewrite, a lease-push of history this session did not rewrite → explicit user approval each occurrence.
- `base_branch` and `production_branch` → force-pushed only on an instruction naming that branch.

## Pushing to the base branch

- A plain push to `base_branch` or `production_branch` → only on the user's instruction naming that push; the instruction runs past a repo's pull-request flow, and each protection the remote reports bypassing is reported once.

## A slow pre-push hook over SSH

- An SSH push holds its connection idle while the pre-push hook runs → a hook outliving the remote's idle timeout ends in exit 141 and an unmoved remote head, even when the hook's summary reads as a pass.
- Judge a push by the remote head afterwards → `git ls-remote --heads origin <branch>`, never by the hook's summary.
- Slow hook → push to the HTTPS URL: `git push https://github.com/<owner>/<repo>.git HEAD:<branch>`; once per machine, `gh auth setup-git` wires `gh` as git's credential helper.
- The HTTPS push sets no upstream → `git branch --set-upstream-to=origin/<branch>` where one is needed.
- Never make the hook do more work to get past it.

## Non-fast-forward rejection

- Read both sides (`git log --oneline origin/<branch>..HEAD` and `HEAD..origin/<branch>`); local-ahead commits also on the base (subjects carrying `(#NNN)`) are base history, not work; report which side holds the real work, then offer rebase · force-push · manual; the user picks.
