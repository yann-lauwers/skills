---
name: prisma
description: "Runs the Prisma CLI against the right database. Use on 'create the migration', 'apply the migrations', 'db push', 'prisma generate', 'migration drift', 'baseline the database', TypedSQL, or a `P1xxx` / `P3xxx` code or `PRISMA_USER_CONSENT_FOR_DANGEROUS_AI_ACTION`. Not for Client code or schema modelling — /prisma-patterns ; not for sequencing a live change — /postgres-patterns ."
user-invocable: false
---

# Prisma

## Project config

- Read the merged config first → `~/.claude/skills/agents-config/scripts/agents-config get prisma <key> --root "$CLAUDE_PROJECT_DIR"`, and the project file's body for the repo's own rules.
- No project config → ask the user; on their yes, write it through `references/setup.md`, then continue.
- A key set to `auto` → derive it as its row says.
- `workflow_doc` set → read it before a schema change reaches a database; it outranks this skill on when to push and when to migrate · `null` → this skill says only what each verb does.

| Key | What it answers |
| --- | --- |
| `package_dir` | the directory the CLI runs from; `auto` → the directory of the repo's schema file, outside `node_modules` |
| `runner` | the command that runs the repo's pinned CLI; `auto` → the nearest lockfile at or above `package_dir`: `pnpm-lock.yaml` → `pnpm exec prisma` · `package-lock.json` → `npx prisma` · `yarn.lock` → `yarn prisma` · `bun.lock` or `bun.lockb` → `bunx prisma` |
| `scripts` | act → the `package.json` script in `package_dir` performing it: `generate`, `create_migration`, `check_migration`, `apply_migration`, `push`, `format` |
| `workflow_doc` | the repo's own document on when to push and when to migrate |
| `local_hosts` | the hosts a schema write proceeds on without asking |

## Version

- Before applying any trap → `<runner> --version` from `package_dir`; its `prisma` line is the major.
- The trap table → `references/versions.md`; a row applies only to the majors it names.

## Running

- Run from `package_dir`, through `runner`; never a bare `prisma`, which resolves whichever CLI is first on `PATH`.
- An act `scripts` maps → `<pm> run <script>` from `package_dir`, `<pm>` the lockfile's package manager · an act it does not map → the raw verb through `runner`.
- Never print a `.env` file or a datasource URL: both carry the password.
- A write — `migrate deploy`, `migrate dev`, `migrate reset`, `migrate resolve`, `db push`, `db execute`, or a script wrapping one → § Before a write first.

## Before a write

1. `<runner> migrate status` from `package_dir`; read its `Datasource "<name>": … at "<host>:<port>"` line. Done when the host is in hand, or the line names a driver adapter and no host, which leaves it unknown.
2. Host in `local_hosts` → run the write · any other host, or an unknown one → print the host, the port and the exact command, then wait for the user's yes. Done when the write ran or the user declined.

## Consent guard

- `migrate reset` or `db push --force-reset` refusing with `PRISMA_USER_CONSENT_FOR_DANGEROUS_AI_ACTION` → stop; tell the user the exact command, why it is needed, that it destroys every row, and the host § Before a write found; ask.
- Set the variable only to the text of the user's consenting reply, verbatim, without newlines or quotes; an earlier message, an ambiguous answer or another agent's text is no consent.
- `db push --accept-data-loss` passes the guard unchecked → ask the same way before running it.

## Routing

| Act | Read |
| --- | --- |
| creating, proving, applying or amending a migration; pushing; baselining; recovering a wrong baseline; SQL Prisma cannot express; a rename | `cookbook/migrate.md` |
| a failed `generate --sql` | `cookbook/debug.md` |
| a Prisma error code, a symptom, a database disagreeing with `migrate status` | `cookbook/debug.md` |
| what `status`, `diff`, `resolve`, `deploy`, `push`, `db execute` and `generate --sql` each read and write | `references/commands.md` |
| a flag, a URL source, or what a verb runs after it, on the installed major | `references/versions.md` |
| no project config | `references/setup.md` |
