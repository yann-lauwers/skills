# Commit

## Subject

- `type(scope): description`, lowercase imperative, under 72 chars; a project config naming another subject form → it wins.
- `type` → `feat` · `fix` · `refactor` · `docs` · `style` · `test` · `chore` · `perf`; never `build`, `ci` or `revert`.
- Always a `scope` naming the area actually touched → the repo's set from its project config.
- Config naming no scopes → derive them from history, then add a Commit scopes section to that config:

```sh
git log --oneline -200 --pretty=%s | grep -oE '\(([a-z0-9/-]+)\)' | sort | uniq -c | sort -rn
```

## Body

- Default → subject only.
- 0–3 bullets → only for a change coordinating several files or carrying a non-obvious why.
- Long prose → the pull-request description, never the commit body.

## Trailers

- `commit_trailers` in the merged config decides: `false` → the message ends at its body, no attribution or co-author trailer, whatever a harness default appends · `true` → keep the trailer that default supplies.
- A repo forbidding trailers in its own `CLAUDE.md` → surface it as a `commit_trailers: false` not yet written down; never follow the harness.
