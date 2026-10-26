# Snapshots

## The name-keyed warm pool

- Warm pool — pre-provisioned sandboxes Daytona keeps warm per snapshot name; undocumented by the vendor.
- A snapshot has no in-place update: a new version deletes the name and recreates it under the same name, and the pool re-warms against it.
- A renamed snapshot starts with a cold, empty pool → never a dynamic, versioned or blue-green name; bridge the delete→recreate window with a standby snapshot.

## Inactivity

- A snapshot unused for two weeks goes `inactive` and boots no sandbox until activated (vendor snapshot docs).
- Use is a create from it: `lastUsedAt` moves on each create and is the clock the sweep reads, so a fallback snapshot deactivates two weeks after its bake, however busy its sibling.
- An inactive snapshot still exists — the listing and `snapshot.get` return it with `state: "inactive"` — so a check keyed on existence passes and one keyed on `active` fails; neither revives it.

## Reactivation

- Activate before booting: the dashboard's Activate action, `snapshot.activate(...)`, or `POST /api/snapshots/{name}/activate`.
- `snapshot.activate(...)` → read the installed signature first: the TypeScript SDK types the argument as the `Snapshot` object `snapshot.get(name)` returns, the vendor's example passes the name.
- None of the three activation routes has been run here, and the delay before a create succeeds is unmeasured.
- A service keeping a fallback snapshot activates it on `inactive` or boots it often enough to stay active, and its probe reports `inactive` as its own state, never as missing.
- Recreating an inactive snapshot also yields an active one, at the cost of a full bake.
