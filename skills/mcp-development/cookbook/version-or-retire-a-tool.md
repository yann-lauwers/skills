# Version or retire a tool

Change a tool's contract, rename it, or remove it, without breaking the clients and permission rules built on it. The order is fixed — alias before removal, signal before relying on the new list. The protocol defines no tool versioning and no `deprecated` field: everything below is the server's own convention, built from what the protocol does carry.

## Step 1: Classify the change

1. Compatible — a new optional argument, a new tool, a new field in `structuredContent`, a looser constraint, a clearer description.
2. Breaking — a renamed or removed tool; a new required argument; a removed or retyped output field; a tighter constraint; a tool moving to another risk tier.
3. A rename is breaking even when the behaviour is identical. Clients key on the exact name: Claude Code's `mcp__<server>__<tool>` allow and deny rules, VS Code's per-tool toggles, saved prompts, scripts. A renamed tool stops matching every one of them — users get prompted again, or a deny rule stops covering it.
4. A tier change is the worst breaking change: a tool that becomes destructive under a name users already auto-approve.

Done when the change is labelled compatible or breaking, with the clause above that decided it.

## Step 2: Ship additively

1. Add, never repurpose: a new optional argument with a default that keeps today's behaviour; a new output field beside the old one.
2. A tool whose tier changes gets a new name in the new tier; the old name keeps its old behaviour.
3. Keep the text mirror of `structuredContent` for older clients.
4. Update the schema snapshot test in the same change (`cookbook/test-a-server.md` § Step 2).

Done when the change is compatible, or Step 3 is needed.

## Step 3: Deprecation window

1. List both names. The old one delegates to the new handler with the identical schema.
2. Mark the old one where MCP allows it: its description opens with `Deprecated — use <new_name>.`; a machine signal wanted → a vendor-prefixed `_meta` key (`com.example/deprecated`), never under a reserved prefix — a second label of `modelcontextprotocol` or `mcp`. No client acts on the key; it is documentation.
3. Count calls to the old name. Remove it when that count reaches zero or the stated date passes, whichever was promised. The spec's own tool-naming proposal sets the precedent for renamed tools: keep aliases "for at least one major version, with a deprecation warning".
4. Publish the permission-rule change with the release: the new `mcp__<server>__<new>` rule, and that the old rule can go once the alias is removed.
5. Removal: the name leaves `tools/list`; a later call gets the protocol error `-32602` "Unknown tool". Hard-coded `--tools` lists can keep resolving through a server-side alias map, the way GitHub's server keeps `DeprecatedToolAliases`.

Done when both names are listed, the old one is marked in its description, and a removal condition is written down.

## Step 4: Signal the change

1. Advertise `tools: { listChanged: true }` in server capabilities — `references/protocol-surface.md` § Utilities carries the notification mechanics and which clients see the change as a push versus on next cache expiry.
2. Set `ttlMs` on `tools/list` results short (minutes) while the change is rolling out, longer once stable — `references/protocol-surface.md` § Utilities carries the caching fields.
3. Keep `tools/list` order deterministic.

Done when a client that never subscribes still sees the new list within one `ttlMs`.
