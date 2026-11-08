# Push

## Refused push

- Non-fast-forward, or `--force-with-lease` refused with `stale info` → never auto-pull, auto-rebase or auto-force: read both sides (`git log --oneline origin/<branch>..HEAD` and `HEAD..origin/<branch>`); local-ahead commits also on the base (subjects carrying `(#NNN)`) are base history, not work; report which side holds the real work, then offer rebase · force-push · manual; the user picks.
- `Connection to <host> closed by remote host.`, then exit 141 → the SSH connection idled out behind a slow pre-push hook, whatever the hook's summary reads; judge the push by `git ls-remote --heads origin <branch>`.
- Remote head unmoved behind a slow hook → push over HTTPS: `git push https://github.com/<owner>/<repo>.git HEAD:<branch>`, then `git branch --set-upstream-to=origin/<branch>` where an upstream is needed; once per machine, `gh auth setup-git` wires `gh` as git's credential helper.

## Who authorizes it

- A rebase this session performed, verified per SKILL.md § Rewrites → `git push --force-with-lease` in the same turn; the instruction authorizing the rebase authorizes this push.
- Any other rewrite, a lease-push of history this session did not rewrite → explicit user approval each occurrence.
- A plain push to the trunk or a branch that deploys → only on the user's instruction naming that push; the instruction runs past a repo's pull-request flow, and each protection the remote reports bypassing is reported once.
