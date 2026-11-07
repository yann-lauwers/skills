# Versions

| Major | Trap | Source |
| --- | --- | --- |
| 6 | `migrate diff` reads the live database through `--from-url` or `--from-schema-datasource`, a schema file through `--from-schema-datamodel`; a `--from-migrations` or `--to-migrations` side refuses without `--shadow-database-url` | Prisma 6.19.0 `migrate diff -h`; its schema engine's refusal text |
| 7 | `migrate diff` drops `--from-url`, `--to-url`, `--from-schema-datasource`, `--to-schema-datasource` and `--shadow-database-url`: the live database is `--from-config-datasource`, a schema file `--from-schema`, the shadow URL `shadowDatabaseUrl` in `prisma.config.ts` | Prisma 7.4.1 `migrate diff -h`; prisma.io upgrade guide to v7 |
| 6 | `migrate dev` and `db push` run `generate` when they finish; `migrate dev` and `migrate reset` run the seed script | prisma.io upgrade guide to v7 |
| 7 | neither runs `generate` nor the seed, and `--skip-generate` and `--skip-seed` are gone → run `generate` after each | prisma.io upgrade guide to v7; Prisma 7.4.1 `migrate dev -h`, `db push -h` |
| 7 | every datasource URL comes from `prisma.config.ts`, which `migrate dev` and `db push` override with `--url`; `.env` loads only where that file loads it; `db execute` takes no `--url` or `--schema` | Prisma 7.4.1 `migrate dev -h`, `db execute -h`; prisma.io upgrade guide to v7 |
| 6 | `migrate dev` on a drifted database prints the reason, names `migrate reset` and exits 130, resetting nothing | Prisma 6.19.0 `build/index.js` |
| 6 | in a non-interactive shell, `migrate dev` refuses once a step warns of data loss, and `migrate reset` refuses without `--force` | Prisma 6.19.0 `build/index.js` |
| 6.15+, 7 | `migrate reset` and `db push --force-reset` stop under an agent → SKILL.md § Consent guard | prisma.io 6.15.0 release post; Prisma 6.19.0 and 7.4.1 `build/index.js` |
