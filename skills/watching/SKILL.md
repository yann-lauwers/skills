---
name: watching
description: "Picks the instrument for anything waited on or driven to a target state — a deploy, job, queue, inbox, a Slack reply, a Linear ticket, a suite driven to green — arms a probe with `run_in_background`, and writes a new probe when none exists. Use when the turn would otherwise end on a promise to report back later, or on 'watch this', 'monitor it', 'keep an eye on', 'wake the session when', 'poll until'; also before hand-rolling a poll loop, sleep-and-check or `tail -F`. Not for one pull request — /watch-pr ."
allowed-tools: Read, Write(${CLAUDE_SKILL_DIR}/**), Edit(${CLAUDE_SKILL_DIR}/**), Grep, Glob, Skill, Monitor, TaskStop, PushNotification
---

# Watching

## Pick the instrument

| The wait | The instrument |
| --- | --- |
| a pull request · a Slack reply · a Linear ticket | its skill's arm step: /watch-pr · /slack `cookbook/watch-reply.md` · /linear `scripts/watch-ticket.py` |
| this session's own subagent or background command | nothing more: the harness reports its end |
| nothing but time | `ScheduleWakeup` at the estimate |
| a runner's wait verb exits with the job's verdict | that verb, `run_in_background` |
| a stream whose every line is news, ending inside thirty minutes | `Monitor` |
| anything else another party moves | a probe, § Write a probe |

- No instrument: the next move is the person's · the session was told not to chase · a daemon already reports it → the closing line names which.
- Close the turn naming the object, the verdicts that wake the session, and the interval.

## Arm a probe

- `run_in_background`, its `description` naming the object.
- The notice carries no output → the verdict is the last `{` line of the task's output file.
- After acting → re-arm with the line's `rearm` flags replacing their namesakes.
- An exit with no `{` line → re-arm once with the same command; a second → report the file's tail.
- A watch dies with its session → the closing line or handoff carries the arm command.
- Stop → `TaskStop <task id>`.

## Write a probe

- One script under the skill owning the object; read /watch-pr 's `scripts/watch-pr.py` first.
- Read, classify, sleep; print one JSON line — `verdict`, `reason`, `rearm`, the facts the act needs — and exit once `verdict:key` differs from `--seen`.
- A failed read — timeout, no status, an error body, an empty list → no line; back off doubling to 600 s, honouring retry-after.
- No read landed for `--blind-after` (3600 s) → `WATCHER_ERROR error=blind`, exit 7.
- A terminal state derived from an absence → two consecutive reads one interval apart; one the source asserts → one.
- A refused credential → `WATCHER_ERROR error=auth`, exit 4.
- One `fcntl.flock` on `~/.local/state/watch/<kind>/<id>.lock` for the process's life; refused → `WATCHER_ERROR error=duplicate`, exit 3.
- `--once` → one read, no lock, the line, exit.
- The verdict table lives in the owning skill, ending on a row that stops on an unknown verdict.
