#!/bin/bash
# Auto-approve safe Bash commands that can't be matched by settings.json patterns.
# Why: settings.json glob patterns don't match multi-line commands (heredocs).
# This hook finds the first non-comment, non-blank line and matches it.
#
# HOW TO ADD A BLOCKED PATTERN:
#   1. Add a `name|regex` entry to BLOCKED_PATTERNS below
#   2. Matched against the full command (not just first line)
#   3. Matching commands are hard-blocked — never allowed
#   4. The name is what reaches the decision log, so a pattern that never fires is
#      readable as zero rows for that name. Keep names stable; renaming one splits
#      its history into two populations. A pattern whose SCOPE changes is the one
#      exception: it retires its old name rather than keeping it, because a stable
#      name over a changed population reads as continuous history and is not.
#
# HOW TO ADD AN ALLOWED PATTERN:
#   1. Add an alternation branch to the ALLOWED_RE regex below
#   2. Pattern is matched against the first line of the command only
#   3. Uses extended regex (grep -E)
#
# WHAT THE LOG CARRIES, AND WHAT IT NEVER CARRIES:
#   Every verdict branch writes a decision row — the pattern name or the bare command
#   word, never the command itself. A blocked command is the one most likely to hold a
#   credential, and a row is a second copy of whatever it records. An environment
#   assignment (`FOO=… cmd`) is recorded as `env-assignment` for the same reason: the
#   first token there is a value, not a name.
#
# SISTER FILE: /hook-development's references/events-and-contracts.md documents what goes
#   WHERE (settings.json vs this hook)

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command')
SESSION=$(echo "$INPUT" | jq -r '.session_id // "unknown"' 2>/dev/null)
CALL_CWD=$(echo "$INPUT" | jq -r '.cwd // empty' 2>/dev/null)
# Skip comment lines and blank lines to find the first real command
FIRST_LINE=$(echo "$COMMAND" | grep -v '^[[:space:]]*#' | grep -v '^[[:space:]]*$' | head -1 | sed 's/^[[:space:]]*//')

# Sourced, never required. A telemetry file that has moved must not take the guard
# with it — a crashed hook is an absent hook, and this one decides permissions.
if [ -r "$HOME/.claude/hooks/lib/log-decision.sh" ]; then
  # shellcheck source=lib/log-decision.sh
  . "$HOME/.claude/hooks/lib/log-decision.sh"
fi
command -v log_decision >/dev/null 2>&1 || log_decision() { :; }

# Hard-block destructive commands — always require manual approval.
# `name|regex`: the name is the log's handle on this pattern, the regex is the test.
BLOCKED_PATTERNS=(
  "git-reset-hard|(^|[[:space:]])git\s+reset\s+--hard"            # discard all local changes
  "push-force|push[[:space:]]+(-f([[:space:]]|$)|--force([[:space:]]|$))"  # force push, not --force-with-lease
  "git-clean-force|clean\s+-[a-z]*f"                              # delete untracked files
  "branch-force-delete|branch\s+-D"                               # force delete branch
  "git-restore|(^|[[:space:]])git\s+restore\s"                    # discard ANY working tree changes
  "git-checkout-discard|(^|[[:space:]])git([[:space:]]+(-[cC][[:space:]]+[^[:space:]]+|--[a-z][a-z-]*(=[^[:space:]]+)?))*[[:space:]]+checkout[[:space:]]+(HEAD[[:space:]]+)?--([[:space:]]|$)"  # same discard as restore, older spelling
  "filter-branch|filter-branch"                                   # rewrite history
  "filter-repo|filter-repo"                                       # rewrite history
  "rm-rf-outside-scratch|rm\s+-rf"                                # recursive force delete, unless every target is below a temp root
  "kill-outside-session|(^|[^[:alnum:]_-])(kill|pkill|killall)([[:space:]]|$)"  # signal a process this session did not start; `lib/kill-scope` dry-runs the match
  "git-stash-destroy|(^|[[:space:]])git([[:space:]]+(-[cC][[:space:]]+[^[:space:]]+|--[a-z][a-z-]*(=[^[:space:]]+)?))*[[:space:]]+stash[[:space:]]+(drop|clear|branch|create|store)([[:space:]]|$)"  # destroys stashed work
)

# The raw match is the GATE, and it is necessary rather than sufficient. It is cheap,
# it runs on every call, and no spelling that passes it today starts denying — but it
# fires on text ABOUT one of these commands as readily as on the command. `lib/destructive-scan`
# decides which one it was, on the ACT VIEW, and it is reached only by the 0.3% of calls
# the gate already caught. Its own header carries the carrier set and the measurement.
#
# NO ANSWER IS A DENY. A missing helper, an unparseable command, a pattern the helper
# cannot translate — each exits non-zero and this denies, because an empty parse means
# "I don't know" and this guard's wrong direction is the one that loses work.
# Resolved from THIS script's own location, not from $HOME. A copy of the hooks tree —
# which is how a break-on-purpose proof runs, and how a second checkout runs — must reach its
# OWN helper: with `$HOME` hardcoded, every mutant of the helper was still answered by
# the installed one, and all seven mutations came back green against a suite that in
# fact catches every one.
SCAN="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/lib/destructive-scan"

for entry in "${BLOCKED_PATTERNS[@]}"; do
  name="${entry%%|*}"
  pattern="${entry#*|}"
  echo "$COMMAND" | grep -qE "$pattern" || continue

  verdict=$(printf '%s' "$COMMAND" | python3 "$SCAN" "$pattern" 2>/dev/null) || verdict="act"
  if [ "$verdict" = "mention" ]; then
    log_decision "bash-destructive-mention" "none" "pattern=$name" "$SESSION" "enforce"
    continue
  fi

  # A recursive force delete whose every target sits strictly below a temporary root
  # clears scratch, never work. `lib/rm-scratch` decides from the command's own words and
  # answers `other` for anything its text cannot prove — a variable, a glob, a relative
  # path, the root itself — and no answer at all keeps the refusal.
  if [ "$name" = "rm-rf-outside-scratch" ]; then
    RM_SCRATCH="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/lib/rm-scratch"
    where=$(printf '%s' "$COMMAND" | python3 "$RM_SCRATCH" 2>/dev/null) || where="other"
    if [ "$where" = "scratch" ]; then
      log_decision "bash-destructive-scratch" "none" "pattern=$name" "$SESSION" "enforce"
      continue
    fi
  fi

  # A branch force delete loses nothing when its tip is kept elsewhere. `lib/branch-archived`
  # answers `archived` only when no worktree has the branch checked out and its tip is either
  # held by `refs/archive/<name>` or found whole on `origin/main` by `git cherry`; anything
  # else, and no answer, keeps the refusal.
  if [ "$name" = "branch-force-delete" ]; then
    BRANCH_ARCHIVED="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/lib/branch-archived"
    kept=$(printf '%s' "$COMMAND" | HOOK_CWD="$CALL_CWD" python3 "$BRANCH_ARCHIVED" 2>/dev/null) || kept="other"
    if [ "$kept" = "archived" ]; then
      log_decision "bash-destructive-archived-branch" "none" "pattern=$name" "$SESSION" "enforce"
      continue
    fi
    log_decision "bash-destructive-deny" "deny" "pattern=$name" "$SESSION" "enforce"
    printf 'Blocked: this force delete names a branch whose tip is kept nowhere else.\n\nA branch force delete is allowed when no worktree has the branch checked out and its tip\nsurvives the delete: either every commit is on origin/main (git cherry origin/main <branch>\nprints only - lines), or refs/archive/<branch> points at it.\n\nKeep it first, then delete, as two separate commands: this guard reads the archive before\nany part of a command runs, so one command doing both is refused.\n  git update-ref refs/archive/<branch> refs/heads/<branch>\n  git branch -D <branch>\nThe archive ref brings it back with git branch <branch> refs/archive/<branch>.\n' >&2
    exit 2
  fi

  # A kill is destructive only by what its match reaches, and no regex sees that.
  # `lib/kill-scope` replays the match read-only and answers `own` when every process it
  # reaches descends from this session's client, `abstain` when a `kill $var` cannot be
  # resolved, and `outside` with the block message. No answer keeps the refusal.
  if [ "$name" = "kill-outside-session" ]; then
    KILL_SCOPE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/lib/kill-scope"
    scope=$(printf '%s' "$COMMAND" | python3 "$KILL_SCOPE" 2>/dev/null) || scope="unanswered"
    case "${scope%%$'\n'*}" in
      own)
        log_decision "bash-destructive-own-process" "none" "pattern=$name" "$SESSION" "enforce"
        continue ;;
      abstain)
        log_decision "bash-destructive-own-process" "abstain" "pattern=$name class=unresolved-operand" "$SESSION" "enforce"
        continue ;;
      outside)
        log_decision "bash-destructive-deny" "deny" "pattern=$name" "$SESSION" "enforce"
        printf 'Blocked: %s\n' "${scope#*$'\n'}" >&2
        exit 2 ;;
    esac
    log_decision "bash-destructive-deny" "deny" "pattern=$name class=unanswered" "$SESSION" "enforce"
    printf 'Blocked: this command signals processes, and lib/kill-scope could not establish which ones it would reach.\nA kill whose match is unknown is refused: on 2026-10-06 `pkill -f '"'"'cat'"'"' -n` reached every app under /Applications and took down the terminal and every session in it.\nKill a process this session started by the PID it got ($!, or TaskStop); stop a dev server where it was started (its worktrunk dev alias, or Ctrl-C in its terminal); anything else, say what and why, and Yann runs it himself with `! <command>`.\n' >&2
    exit 2
  fi

  log_decision "bash-destructive-deny" "deny" "pattern=$name" "$SESSION" "enforce"
  # Law 6: a block message is a prompt, not an error code. The old one named the
  # pattern and stopped, so the reader's only move was to guess. Naming the routes
  # out is what turns a refusal into a step.
  printf 'Blocked: the command matches the destructive pattern %s.\n\nThis tree may hold the only copy of the work. These patterns discard uncommitted\nchanges, delete untracked files, or rewrite pushed history, and none of that is\nrecoverable afterwards. Settings carry an empty deny list under bypassPermissions,\nso nothing else asks before it runs.\n\nThe pattern was found where it would RUN, not merely where it is written. Text about\none of these commands — a here-doc body going into a file, a sed pattern, a quoted\nmessage — is not one, and does not reach this. What still counts as running it: a\nstring handed to a shell (bash -c, eval, a here-doc fed to a shell), a wrapper that\nruns it elsewhere or later (trap, ssh, watch, timeout, nohup), an interpreter\nhere-doc that shells out, and a script authored into a file that this same command\nthen executes.\n\nActually needing the destructive command? Run it yourself, or narrow it: a named\npath instead of a glob, one file rather than the tree, --force-with-lease over\n--force.\n' "'$name'" >&2
  exit 2
done

# `git stash list` / `show` read; `pop` / `apply` restore, and git aborts rather
# than overwriting a modified file. None of the four destroys stashed work.
#
# Allowed only as the WHOLE command — one line, one statement, no substitution.
# The line test is done in bash, not in the regex: grep anchors ^ and $ to a
# LINE, so a two-line command whose second line is `git stash list` would match
# here and clear every pattern in the loop above.
#
# The verb is the token after `stash`, read by position rather than by column:
# `git -C <path> stash list` moves it, and reading a fixed field silently
# recorded the path instead. A `-m "then pop it"` message cannot reach it,
# because the regex above has already constrained what may sit there.
STASH_SAFE_RE='^[[:space:]]*git([[:space:]]+(-[cC][[:space:]]+[^[:space:]]+|--[a-z][a-z-]*(=[^[:space:]]+)?))*[[:space:]]+stash[[:space:]]+(list|show|pop|apply)([[:space:]]+[^;&|<>$`()]*)?[[:space:]]*$'
if [ "$(printf '%s' "$COMMAND" | wc -l | tr -d ' ')" = "0" ] \
   && printf '%s' "$COMMAND" | grep -qE "$STASH_SAFE_RE"; then
  verb=$(printf '%s' "$COMMAND" | awk '{for(i=1;i<NF;i++) if($i=="stash"){print $(i+1); exit}}')
  log_decision "stash-safe-allow" "allow" "verb=$verb" "$SESSION" "enforce"
  echo '{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "allow"}}'
  exit 0
fi

# The files that reconfigure the permission system: settings.json, settings.local.json,
# the guards that decide permissions — this script and `permission-request.py`, which
# GRANTS. A bare `settings.json` is
# deliberately NOT a target: it would match every project's own settings file. The guard
# files are also named as bare basenames, because a `cd` into hooks/ makes the rest of
# the command relative and the path spelling then never appears in it.
GUARD_TARGET='(\.claude/settings(\.local)?\.json|(^|[^[:alnum:]_.-])auto-allow-bash\.sh|(^|[^[:alnum:]_.-])permission-request\.py)'

# A command NAMING a permission-system file gets no BLANKET allow from either
# allowlist below, whatever its verb: both were granting writes this side cannot see
# — measured 2026-09-09, a `python3 -c "… json.dump(d, open(p,'w'))"` over
# settings.json was ALLOWED by the `.claude/` branch, and an allow suppresses the
# host's own prompt rather than merely staying quiet.
#
# Silence, not a refusal: the host decides as it would for any unclaimed command.
# There is no prompt cost, because the host's own prompt is raised by its `Read()`
# deny patterns and none of them names a settings file.
if echo "$COMMAND" | grep -qE "$GUARD_TARGET"; then
  log_decision "guarded-name-no-grant" "none" "target=permission-system-file" "$SESSION" "enforce"
  exit 0
fi

# Auto-allow commands targeting .claude/ directories (reports, learnings, missions, etc.)
# Runs AFTER blocked patterns, so destructive ops are still gated
if echo "$COMMAND" | grep -qE '\.claude/'; then
  log_decision "claude-path-allow" "allow" "path=.claude" "$SESSION" "enforce"
  echo '{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "allow"}}'
  exit 0
fi

# Single joined regex — one fork instead of 29 separate grep calls
ALLOWED_RE="^(cat [>/]|mkdir -p |which |ls |gh (pr (create|view|list|checks|diff|status|comment|edit|ready)|api|issue|repo|run) |git (log|show|diff|branch|rev-parse|describe|tag|remote|ls-files|status)|grep |command -v |for |echo |wc |node -e |rev-dep |find |python3 -c |pnpm |npx |head |tail |sort |uniq |sed |jq |basename |dirname |curl -s |[A-Z_]+=)|(^|\s)playwright"

if echo "$FIRST_LINE" | grep -qE "$ALLOWED_RE"; then
  # The bare command word, and only when it IS a bare word. The `[A-Z_]+=` branch
  # matches an environment assignment whose first token carries a VALUE, so that
  # branch is recorded by its shape instead.
  word=$(printf '%s' "$FIRST_LINE" | awk '{print $1}')
  case "$word" in
    [a-z]*[!a-zA-Z0-9_-]*|"") word="other" ;;
    *=*) word="env-assignment" ;;
    [a-z]*) : ;;
    *) word="env-assignment" ;;
  esac
  log_decision "bash-allowlist-allow" "allow" "cmd=$word" "$SESSION" "enforce"
  echo '{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "allow"}}'
  exit 0
fi

# No match — let normal permission flow handle it (settings.json patterns).
# Deliberately unlogged: this branch renders no verdict and fires on every Bash call
# the other branches did not claim, so a row here would be the log's largest
# population and its least informative one.
exit 0
