# Wire a client

Register a server with a client — an `.mcp.json` entry, a `claude mcp add`, another client's config — and the permission rules that go with it; the scope and the rules are decisions, the syntax is fixed per client and `references/clients.md` carries every client's shape.

## Step 1: Pick the scope

1. Everyone who clones the repo needs it → project scope, `.mcp.json` at the repo root, committed.
2. Only this machine, this repo → local scope (`claude mcp add` default).
3. Every repo on this machine → user scope.
4. A command that embeds a path or account of this machine never goes in a committed `.mcp.json`; use `${VAR:-default}` or local scope.

Done when the scope is named and a committed file carries nothing machine-specific.

## Step 2: Write the entry

1. stdio: `claude mcp add <name> --scope <s> --env K=V -- <command> <args…>`.
2. Remote: `claude mcp add --transport http <name> <url>`. OAuth needs nothing in the entry unless the server's metadata is non-standard.
3. Secrets: never inline. `${VAR}` in `env` or `headers`, with the value injected into the environment Claude Code starts in.
4. Name the server short and without `_`, inside the name budget in `references/clients.md` § What a server can rely on: the name prefixes every tool.
5. Another client → `references/clients.md` § The matrix.

Done when `claude mcp get <name>` shows the entry at the intended scope.

## Step 3: Write the permission rules

1. Allow the read tier with one prefix glob — `mcp__<name>__read_*`.
2. Put destructive tools under `ask`, or `deny` — `mcp__<name>__remove_*`; deny beats ask beats allow across every scope (`references/clients.md` § Claude Code in detail).
3. Never `mcp__<name>` or `mcp__<name>__*` in `allow` for a server that has writes: it approves every current and future tool, including ones added after the rule was written.
4. Arguments cannot be matched in settings; a tool that needs per-argument policy is two tools.

Done when each tier's rule is written and a tool of each tier was called to confirm it prompted, ran or was refused as intended.

## Step 4: Prove it connects

1. `claude mcp list` shows it connected; `/mcp` in a session shows its tools and any error.
2. A project server shows as pending until approved in an interactive session.
3. Call one tool from a real session.

Done when a real session called a tool on the server and the permission rule behaved as written.
