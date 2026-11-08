# Commit

## Subject

- Subject form → the project's, where it names one; else `type(scope): description`, lowercase imperative.
- **Subject at most 72 chars**, counted before committing.
- `type` → `feat` · `fix` · `refactor` · `docs` · `style` · `test` · `chore` · `perf`; never `build`, `ci` or `revert`.
- Always a `scope` naming the area touched, narrow and lowercase; the project's own scopes, where it lists them, else the ones history uses:

```sh
git log --oneline -200 --pretty=%s | grep -oE '\(([a-z0-9/-]+)\)' | sort | uniq -c | sort -rn
```

## Body

- Subject only by default; a change coordinating several files or carrying a non-obvious why → up to 3 bullets.
- Prose → the pull-request description, never the commit body.
