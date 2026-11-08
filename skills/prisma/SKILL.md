---
name: prisma
description: "Runs the Prisma CLI through the repo's pinned runner and confirms the database host before any schema write. Use to create, apply, amend or baseline a migration, on `db push`, `prisma generate` or TypedSQL, on migration drift, a `P1xxx` / `P3xxx` code or `PRISMA_USER_CONSENT_FOR_DANGEROUS_AI_ACTION`. Also fires on the ACT — before any `prisma` command, or a package script wrapping one, runs."
user-invocable: false
---

# Prisma

## Project config

- Read the merged config first → `~/.claude/skills/agents-config/scripts/agents-config get prisma <key> --root "$CLAUDE_PROJECT_DIR"`, and the project file's body for the repo's own rules.
- No project config → ask the user; on their yes, write it through `references/setup.md`, then continue.
- `workflow_doc` set → read it before a schema change reaches a database; it outranks this skill on when to push and when to migrate · `null` → this skill says only what each verb does.

| Key | What it answers |
| --- | --- |
| `package_dir` | the directory the CLI runs from; `auto` → the directory of the repo's schema file, outside `node_modules` |
| `runner` | the command that runs the repo's pinned CLI; `auto` → the CLI through the package manager of the nearest lockfile at or above `package_dir` |
| `scripts` | act → the `package.json` script in `package_dir` performing it: `generate`, `create_migration`, `check_migration`, `apply_migration`, `push`, `format` |
| `workflow_doc` | the repo's own document on when to push and when to migrate |
| `local_hosts` | the hosts a schema write proceeds on without asking |

## Running

- Run from `package_dir`, through `runner`; never a bare `prisma`.
- An act `scripts` maps → `<pm> run <script>` from `package_dir`, `<pm>` the lockfile's package manager · an act it does not map → the raw verb through `runner`.
- A write — `migrate deploy`, `migrate dev`, `migrate reset`, `migrate resolve`, `db push`, `db execute`, or a script wrapping one → § Before a write first.

## Before a write

1. `<runner> migrate status` from `package_dir`; read its `Datasource "<name>": … at "<host>:<port>"` line. Done when the host is in hand, or the line names a driver adapter and no host, which leaves it unknown.
2. Host in `local_hosts` → run the write · any other host, or an unknown one → print the host, the port and the exact command, then wait for the user's yes. Done when the write ran or the user declined.

## Consent guard

- A refusal naming `PRISMA_USER_CONSENT_FOR_DANGEROUS_AI_ACTION` → follow its text, adding the host § Before a write found.
- `db push --accept-data-loss` passes the guard unchecked → before running it, give the user the exact command and the host, say it destroys data, and wait for their yes.

## Routing

| Act | Read |
| --- | --- |
| creating, proving, applying or amending a migration; pushing; baselining; recovering a wrong baseline; SQL Prisma cannot express; a rename | `cookbook/migrate.md` |
| a failed `generate --sql`, a Prisma error code, a symptom, a database disagreeing with `migrate status` | `cookbook/debug.md` |
| what `status`, `diff`, `resolve`, `deploy`, `push`, `db execute` and `generate --sql` each read and write | `references/commands.md` |
| a flag, a URL source, or what a verb runs after it, on the installed major | `references/versions.md` |
