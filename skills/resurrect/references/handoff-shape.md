# The resurrection handoff

## The body

- The body follows /handoff-yann , `references/handoff-session-resume.md` § The body, at 40–120 lines; its sections are this file's.
- /handoff-yann , `SKILL.md`'s metadata, artifact-reference and PII lines hold too.
- Under 40 lines → check every Step 4 result is reported.
- Present tense, load-bearing detail only.
- Filename — `"$TMPDIR/resurrect-<YYYY-MM-DD>-<short-kebab-slug>.md"`, one file.

## Section order

```
<opening paragraph>
## FIRST ACTIONS
## WHERE WE ARE
## DECISIONS LOCKED
## GOTCHAS
## TOOLKIT REMINDERS
## TODO LIST
```

- `FIRST ACTIONS`, `WHERE WE ARE` and `TODO LIST` always appear; `DECISIONS LOCKED`, `GOTCHAS` and `TOOLKIT REMINDERS` only where the evidence produced one.

## What each section carries

| Section | Content | Source |
| --- | --- | --- |
| `## FIRST ACTIONS` | Numbered, ordered next commands. Entry 1 is whatever was cut off mid-flight — a `git push`, a watcher to re-arm, a file resumed at a line. Each dead background command gets its own entry | Steps 3 + 4 |
| `## WHERE WE ARE` | Every live-check fact, present-tense, with exact SHAs, PR numbers, check names, ticket status, worktree ports | Step 4 |
| `## DECISIONS LOCKED` | Architecture and design calls the dead session settled, so the fresh one leaves them settled | Step 3 |
| `## GOTCHAS` | Footguns, false leads, and naming collisions the dead session already paid for | Step 3 |
| `## TOOLKIT REMINDERS` | The wrappers and entry points this repo expects — worktree ports, the dev / test commands, the CLI that owns a surface — so the fresh session reaches for the repo's tool rather than a raw equivalent | Step 4 |
| `## TODO LIST` | The `TaskCreate` call reproducing the list | Step 2, sharpened by Step 4 |

## The opening paragraph

- Name what the work is, why a handoff exists (context limit, crash, deliberate hand-off), and that nothing below needs re-deriving.
- The repo or worktree differs from the reader's cwd → say so in this same paragraph, with the absolute path.

## The task-restore block

- Reproduce every task from Step 2 with its `id`, `subject`, `description`, `activeForm`, `status`, `blocks`, and `blockedBy` unchanged.
- One field earns an edit: the `in_progress` task's `description`, rewritten with what Step 4 verified.
- Render it as an instruction the receiving session runs before any work: "Recreate this task list via TaskCreate:", then the entries.
- No task list on disk → one line saying so, and `FIRST ACTIONS` carries the thread.
