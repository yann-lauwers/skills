---
name: prisma
description: "Runs the Prisma CLI against the right database — derives the installed major and its traps, checks which database a schema write reaches, stops at Prisma's AI consent guard, drives `migrate`, `diff`, `resolve`, `db push`, `generate` and TypedSQL. Use on 'create the migration', 'apply the migrations', 'db push', 'prisma generate', 'migration drift', 'baseline the database', or a `P1xxx` / `P3xxx` code or `PRISMA_USER_CONSENT_FOR_DANGEROUS_AI_ACTION`. Not for Client code or schema modelling — /prisma-patterns ; not for sequencing a live change — /database-migrations ."
user-invocable: false
---

# Prisma

Running the Prisma CLI — which major, through what, against which database — and what each of its verbs reads and writes.

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
- A row applies only to the majors it names.

| Major | Trap | Source |
| --- | --- | --- |
| 6 | `migrate diff` reads the live database through `--from-url` or `--from-schema-datasource`, a schema file through `--from-schema-datamodel`; a `--from-migrations` or `--to-migrations` side refuses without `--shadow-database-url` | Prisma 6.19.0 `migrate diff -h`; its schema engine's refusal text |
| 7 | `migrate diff` drops `--from-url`, `--to-url`, `--from-schema-datasource`, `--to-schema-datasource` and `--shadow-database-url`: the live database is `--from-config-datasource`, a schema file `--from-schema`, the shadow URL `shadowDatabaseUrl` in `prisma.config.ts` | Prisma 7.4.1 `migrate diff -h`; prisma.io upgrade guide to v7 |
| 6 | `migrate dev` and `db push` run `generate` when they finish; `migrate dev` and `migrate reset` run the seed script | prisma.io upgrade guide to v7 |
| 7 | neither runs `generate` nor the seed, and `--skip-generate` and `--skip-seed` are gone → run `generate` after each | prisma.io upgrade guide to v7; Prisma 7.4.1 `migrate dev -h`, `db push -h` |
| 7 | every datasource URL comes from `prisma.config.ts`, which `migrate dev` and `db push` override with `--url`; `.env` loads only where that file loads it; `db execute` takes no `--url` or `--schema` | Prisma 7.4.1 `migrate dev -h`, `db execute -h`; prisma.io upgrade guide to v7 |
| 6 | `migrate dev` on a drifted database prints the reason, names `migrate reset` and exits 130, resetting nothing | Prisma 6.19.0 `build/index.js` |
| 6 | in a non-interactive shell, `migrate dev` refuses once a step warns of data loss, and `migrate reset` refuses without `--force` | Prisma 6.19.0 `build/index.js` |
| 6.15+, 7 | `migrate reset` and `db push --force-reset` stop under an agent → § Consent guard | prisma.io 6.15.0 release post; Prisma 6.19.0 and 7.4.1 `build/index.js` |

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
| no project config | `references/setup.md` |
