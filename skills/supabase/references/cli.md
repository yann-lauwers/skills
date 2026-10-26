# CLI

## Authenticate

- `keyless run -s T=<SECRET> -- sh -c 'supabase login --token="$T"'` — later commands inherit the cached login until it is cleared or the token rotates.

## Traps

- `supabase link --project-ref <project-ref>` keeps the link in `supabase/.temp/`, which a repo ignores → every checkout links on its own; a fresh worktree has no link.
- `link` goes through the shared pooler unless `--skip-pooler`, so it works from an IPv4-only network.
- `db push` refuses a migration older than the newest one recorded unless `--include-all`; `--dry-run` prints what would apply.
- `db dump` reads `--linked` by default → an unlinked checkout reads nothing.

Flags read from `supabase <command> --help` on CLI 2.75.0, 2026-10-02.
