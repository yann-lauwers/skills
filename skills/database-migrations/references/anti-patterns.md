# Anti-patterns

The six shapes that fail in production, what each one does when it fails, and what replaces it. Read when reviewing a migration someone else wrote, or when one has already misbehaved.

| Anti-Pattern | Why It Fails | Better Approach |
|-------------|-------------|-----------------|
| Manual SQL in production | No audit trail, unrepeatable | Always use migration files |
| Editing deployed migrations | Causes drift between environments | Create new migration instead |
| NOT NULL without default | Locks table, rewrites all rows | Add nullable, backfill, then add constraint |
| Inline index on large table | Blocks writes during build | CREATE INDEX CONCURRENTLY |
| Schema + data in one migration | Hard to rollback, long transactions | Separate migrations |
| Dropping column before removing code | Application errors on missing column | Remove code first, drop column next deploy |

Five of the six pass every test suite: the migration applies, the schema is correct afterwards, and the damage is a lock held or a drift opened rather than a wrong result. Reviewing the statement alone therefore catches none of them — what the review reads is the size of the table it runs against and the deploy standing between it and the code.
