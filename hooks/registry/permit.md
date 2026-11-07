# PERMIT — these answer the permission question

Entry requirement for this tier: the row names which branch of the decision it records, because a permission handler with several branches is several checks.

| id | component | event | fires when | class | rollout |
| --- | --- | --- | --- | --- | --- |
| `guarded-name-no-grant` | `auto-allow-bash.sh` | PreToolUse (Bash) | the command names a permission-system file — `.claude/settings.json`, `.claude/settings.local.json`, `auto-allow-bash.sh` or `permission-request.py` — and reached the allowlists. It emits no verdict; the row makes a withheld grant countable | ANNOT | `ENFORCING` |
| `claude-path-allow` | `auto-allow-bash.sh` | PreToolUse (Bash) | the command names a `.claude/` path, matched no destructive pattern, and names no permission-system file | PERMIT (allow) | `ENFORCING` |
| `bash-allowlist-allow` | `auto-allow-bash.sh` | PreToolUse (Bash) | the command's first real line matches `ALLOWED_RE`; `detail` carries the bare command word, or `env-assignment` | PERMIT (allow) | `ENFORCING` |
| `stash-safe-allow` | `auto-allow-bash.sh` | PreToolUse (Bash) | the whole command, on one line, is `git stash list` / `show` / `pop` / `apply`; `detail` carries the verb | PERMIT (allow) | `ENFORCING` |
| `cd-relative-read-allow` | `permission-request.py` | PermissionRequest (Bash) | the host raised the prompt itself — the payload carries a `permission_suggestions` list, which a hook's or rule's `ask` never does — and every file operand, resolved through the `cd` chain (the cwd when there is none), can reach no `Read()` deny or ask rule in force by its lexical path or its `realpath`, a directory read by a descending verb tested by reachability, and no `Bash()` ask rule's words appear in the command. Rules are read from `~/.claude/`, `$CLAUDE_CONFIG_DIR`, managed settings and every `.claude/settings{,.local}.json` up from `$CLAUDE_PROJECT_DIR`, the payload cwd and both repo roots; never from `--settings`, `--disallowedTools`, a configuration profile or server-managed settings. Every ambiguity resolves toward a match; a link-following walk, a non-reader naming a permission-system file, and anything unresolvable are no opinion. `detail` carries counts, never a path | PERMIT (allow) | `ENFORCING` |

- The fall-through — no branch claimed the call, so the host's own flow decides — writes no row on purpose.
