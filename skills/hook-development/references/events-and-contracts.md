# Events and contracts

The event table, matcher values, payload fields, handler fields and decision-control fields live in the Claude Code hooks reference and hooks guide (`docs.claude.com/en/docs/claude-code/hooks` and `/hooks-guide`); this file holds only what this setup decided or verified beyond them. Last full read of both: 2026-07-29.

- At the start of every hook cycle, fetch both documents and read the event's own section and the decision-control table: a remembered contract is not a contract.

## Wiring

- A settings file takes the `{"hooks": {...}}` wrapper, never the bare `{"PreToolUse": [...]}` form; plugin `hooks/hooks.json` takes the same wrapper.
- A path placeholder in the command → exec form (`args` present), `${CLAUDE_PROJECT_DIR}` as the placeholder; shell form where the command needs a shell — pipes, `&&`, an existence or root guard.
- A project hook wired in shell form through the bare `$CLAUDE_PROJECT_DIR` → the wiring's `command` tests the variable and the script before running it — `[ -n "$CLAUDE_PROJECT_DIR" ] || { echo '<id> did not run: CLAUDE_PROJECT_DIR empty' >&2; exit 1; }; [ -f "$CLAUDE_PROJECT_DIR/<path>" ] || exit 0;` — since under `python3` a script path that does not resolve exits 2 and blocks every matching call; exec form needs no variable test and cannot hold the script test → a script some checkout may lack takes shell form with both tests.
- `"*"`, `""` or an omitted matcher matches every call; a matcher string holding any character beyond letters, digits, `_`, `-`, space, `,` and `|` is an unanchored regex: `Edit.*` also matches `NotebookEdit` → `^Edit$`; a whole MCP server → `mcp__<server>__.*`, since a bare `mcp__memory` matches nothing.
- `if` fails open — an unparsable command runs the hook anyway — so it is an optimisation, never the enforcement boundary; one rule per handler; `Edit(src/**)` matches the working directory's `src` only → `Edit(**/src/**)` for any depth.
- Hooks run without a controlling terminal: `/dev/tty` is unwritable → `systemMessage` reaches the user.

## Prompt and agent hooks

- They return `{"ok": true}` or `{"ok": false, "reason": "..."}` and nothing else — never `hookSpecificOutput` or `permissionDecision`.
- The input JSON's placeholder is `$ARGUMENTS`; `$TOOL_INPUT` and `$TOOL_RESULT` do not exist.

## Permission verdicts

- Under `acceptEdits` or `bypassPermissions` the native prompt is no backstop, and an `allow` suppresses the host's own prompt → enumerate every code path that can emit `allow`, and justify each one.
- A `PreToolUse` hook exiting 0 with no output has no opinion: the call continues through the normal permission flow. Every path where the parser cannot tell what the action touches takes it.
- The `Read()` deny rules in `settings.json` stay, even where a hook covers the same path: every hook fails open, so a crashed hook tree leaves those rules as the whole credential guard. Write each one anchored — `~/…` or `//…` — never `/…`, which anchors at the settings file, and never `**/`: `permission-request.py` grants a recursive read only by proving no anchored pattern lies beneath the tree, and an unanchored one keeps every such read prompting.
- `auto-allow-bash.sh`'s `ALLOWED_RE` matches the first line of a command only, so each branch added to it allows a multi-statement command whatever follows that line; add one only to teach the guard a known-good command shape.
- A write to a permission-system file (`lib/permission_files.NAME_RE`) gets no grant from the layer's allowlists and goes to the host's own permission flow. Say what changes before writing it.

## Output

- Exit 2 blocks and feeds stderr back; JSON on stdout is read on exit 0 only; one signalling style per hook.
- Exit 1 does not block: a crashed hook lets the action it exists to prevent go ahead. `WorktreeCreate` alone aborts on any non-zero exit.
- An interactive session start hands over `additionalContext` and nothing else; `initialUserMessage` applies under `-p` only. Measured 2026-08-15, one-variable harness, interactive pty: `additionalContext` lands, `initialUserMessage` is not run; how `-p` orders it ahead of a supplied prompt is unverified.
- A hook needing an interactive session to perform a step — read a file, load a skill, run a command — pairs the injection with a `PreToolUse` gate that denies until the step's outcome is observable, gating on the outcome, never on the step having been requested; or reaches for `Stop`, the one event that re-invokes the model, whose `decision: "block"` continues the conversation.
- `additionalContext` text that never changes → /managing-harness § Where a fact goes · its phrasing → `messages.md` § The rules behind those verdicts.

## Instrumenting `SubagentStop` can destroy the subagent's deliverable

Measured on a real harness with real nested subagents.

- An `additionalContext` emitted at `SubagentStop` never reaches the parent: it lands in the stopping child's next input and re-invokes it, and the child's re-invoked final message becomes the Agent tool's return value. Unguarded, it overwrites the deliverable, loops the child (each re-invocation fires the event again), and hands text meant for the parent to a child that refuses to act on it.
- Emitting there takes all three guards:
  1. Address the text to the child, as a corrective it can act on.
  2. Once per `agent_id`, never once per session.
  3. Emit only when something is wrong; a clean stop gets nothing.
- Scope it by `agent_type` to the agent types meant; a blanket emission hits read-only scouts whose whole value is their returned text.
- `systemMessage` at `SubagentStop` appears in no transcript, sidechain, stream or recorded hook attachment: it reaches no one.
- A backgrounded Agent dispatch fires `PostToolUse` at launch, before the subagent runs, so an arm matching `Agent` cannot read its `tool_response` → read the result at `SubagentStop`, with the hazards above.

## Facts that fail silently

- A matcher scopes the whole handler: a script registered on `PostToolUse` with `"matcher": "Bash"` never reaches its branches for any other tool — dead code that never errors. Check it mechanically: diff the tools each script's branches handle against the matchers it is registered under.
- A failure classifier on `PostToolUseFailure` reads `is_interrupt` first: a command the user stopped with ESC failed because it was stopped, not because it was wrong.

## Lifecycle facts that bite

- Hook settings are usually picked up by the file watcher and scripts are read at invocation; whether new configuration is live → `/hooks`.
- The transcript file lags the in-memory conversation → a `Stop` or `SubagentStop` hook reads the turn's final text from `last_assistant_message`.
- A resumed session replays saved injected text rather than re-running mid-session hooks, so timestamps and SHAs in `additionalContext` go stale; `SessionStart` re-runs with `source: "resume"`.
- An HTTP hook blocks only through a 2xx carrying the decision JSON; a non-2xx status is a non-blocking error.
