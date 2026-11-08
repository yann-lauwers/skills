---
name: trigger-dev
description: "Runs and deploys Trigger.dev v4 background tasks. Use on \"trigger.dev\", \"background job\", \"scheduled task\", \"deploy the tasks\", a schedule that did not fire, `trigger.config.ts`, a `schedules.task` cron, or the `trigger.dev` CLI's `dev` or `deploy`."
---

# Trigger.dev (v4)

## Project config

- Config: the repo's `docs/agents/integrations/trigger-dev.md` over the floor, read merged: `~/.claude/skills/agents-config/scripts/agents-config get trigger-dev <key> --root "$CLAUDE_PROJECT_DIR"`.
- `secret: null` → the CLI authenticates through its own browser login, cached on this machine, against the project `trigger.config.ts` names.
- No `docs/agents/integrations/trigger-dev.md` in the repo → ask the user; on their yes, write it per /managing-harness , `references/skills.md` § A tool's skill and its config; then continue.

## Running

- The CLI run at `@latest` prompts to bump the pinned `@trigger.dev/*` packages to its own version, and a mismatch fails deploys → that prompt is the user's: accepting it edits `package.json`.
- A schedule fires in dev only while the CLI's `dev` worker runs, and in staging or production only for tasks in the latest deployment.
- A declarative `cron` on `schedules.task` syncs on dev and deploy; its pattern is UTC unless the `cron` object names a `timezone`.
- Build extensions apply to the deployed build only, never to local dev.
