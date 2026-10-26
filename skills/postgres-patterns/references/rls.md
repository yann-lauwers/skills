# Row Level Security policies

- A caller lookup inside a policy's `USING` — the session's user id, a claim pulled from a JWT, a `current_setting()` → wrapped in a scalar subquery, which the planner hoists into an InitPlan and runs once per statement instead of once per row.

```sql
CREATE POLICY orders_owner ON orders
  USING ((SELECT auth.uid()) = user_id);   -- the SELECT wrapper is the whole trick
```

- `auth.uid()` — Supabase's helper; on a plain PostgreSQL install the same shape wraps whatever resolves the caller — `(SELECT current_setting('app.user_id', true)::bigint)` — where `true` returns NULL rather than erroring on a session with the setting unset.
- Index the column every policy compares against.
- `EXPLAIN` a query under the policy, as a role the policy applies to — the table owner, a superuser and a `BYPASSRLS` role skip it: the lookup under `InitPlan` holds; inside the `Filter` line → the wrapper is missing.
- `CREATE POLICY` and `ALTER TABLE … ENABLE ROW LEVEL SECURITY` → one migration file of their own, through /database-migrations ; each takes a brief `ACCESS EXCLUSIVE` lock on the table.
