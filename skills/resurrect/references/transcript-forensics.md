# Transcript forensics

## The five artifact locations

- Four are keyed by the session id; the task list by the session's team name.

| Location | Holds |
| --- | --- |
| `~/.claude/projects/<project-dir>/<id>.jsonl` | The transcript — one JSON object per line, the only complete record of the conversation |
| `~/.claude/tasks/<team>/*.json` | The `TaskCreate` list, one numbered file per task, as the user last saw it |
| `~/.claude/projects/<project-dir>/<id>/` | `subagents/` (per-agent transcript + `.meta.json`) and `tool-results/` — the overflow the transcript points at |
| `~/.claude/session-env/<id>` | Environment captured for the session |
| `~/.claude/file-history/<id>` | Snapshots backing the session's edits |

- `<team>` → the `@session-<hex>` suffix of an `agent_id` in the transcript's tool results; none → the `~/.claude/tasks/*/` whose `*.json` `subject` matches a `TaskCreate` input in the transcript; neither → no task list survived.

## Transcript line types

| `type` | What it gives you |
| --- | --- |
| `assistant` / `user` | The conversation itself. `message.content` is a block list — `text`, `thinking`, `tool_use`, `tool_result` (with `is_error`) |
| `ai-title` | The session's generated title, rewritten as the session evolves — the last one is the current name |
| `pr-link` | `prNumber`, `prUrl`, `prRepository`, `timestamp` — the cheapest way to find which PRs the session drove |
| `system` | `subtype` names a lifecycle event |
| `last-prompt` | `lastPrompt`, the most recent prompt's text, and `leafUuid`, its entry |

- Every other `type` rarely changes a handoff.
- User and assistant entries also carry `cwd`, `gitBranch`, `version`, `timestamp`, `permissionMode` and `isSidechain`.

## Resolving the project directory

- Project directory — the cwd with every non-alphanumeric character replaced by `-`.
- Encode a cwd forward to find its sessions; never decode a directory name back to a path, since a dot and a slash both become `-`.
- Take the repo path and branch from the transcript's per-entry `cwd` and `gitBranch`.

## Death markers

- Classify the ending from the tail; the script prints it as `ended as`.

| Classification | Signature | What it implies |
| --- | --- | --- |
| context-limit | A `Prompt is too long` marker at the tail | The session stopped between deciding and acting — its last stated intention probably never ran |
| crash mid-action | The final entry is an errored `tool_result` | Something was half-applied. The erroring tool call is the first thing to re-check live |
| context-limit or interrupt | The last assistant turn is empty | Same posture as a context-limit death |
| no death marker | The tail ends on a completed turn | A deliberate hand-off. The transcript's last claims are likelier to hold, and still go through Step 4 |

- A death marker sets how far to distrust the tail, never whether Step 4 runs.

## Traps in the parse

- Flatten every `message.content` block — `text`, `thinking`, `tool_use`, `tool_result` — before grepping or printing; `content` is a plain string only in the simplest entries, and a crash's errored `tool_result` sits in a block.
- Tracker-key grep → at least two digits, skipping the document prefixes `AC`, `ADR`, `RFC`, `ISO`, `UTF`, `SHA`, `RGB`, `CVE`, `HTTP`.
- Rank tracker keys and worktree paths by frequency across the whole transcript and take the top.
