# Failure modes that look like success

Each row is a state that passes a casual check and is still broken.

| Looks fine | Is broken | Caught by |
| --- | --- | --- |
| Unit tests green | handlers were called directly; nothing crossed a transport | a client in process (`cookbook/test-a-server.md` § Step 1) |
| Works in the client you tried | the eras served leave out a client the design names — Claude Code negotiates Modern over HTTP, VS Code and Zed send `initialize`, and a dual-era client reaches a Legacy-only server only through its fallback | the design's client list against each client's era (`references/clients.md` § The matrix), then the Inspector per era served |
| stdio server runs locally | one `print`/`console.log` on stdout; the client reads garbage before the first reply | parse every stdout line in a test |
| Socket server answers `nc` | the Swift `NetworkTransport` heartbeat (`F0 9F 92 93`, no newline) corrupts every non-Swift peer | a non-Swift client in the wire test |
| "Every reply ends its connection" | fine for Modern; a Legacy client loses its `initialize` capabilities after the first reply | a Legacy client making two calls on one bridge |
| `tools/list` returns every tool | a tool with an invalid schema or a root `anyOf` is dropped or flattened by Claude Code | `tools/list --strict` and a schema-validity test |
| Tool fails and the client shows an error | it was thrown as a protocol error; the model never saw why and cannot self-correct | a test asserting `isError: true` on each domain failure |
| Annotations present | set on some tools; an unset boolean reads as `false` or defaults to destructive | a test over the whole list requiring all hints |
| `readOnlyHint: true` on the safe tools | Claude Code approves by name, not by hint; users still get prompted | a tier prefix in every name |
| One allow rule for "all reads" | a noun-first tool (`issue_read`) escapes `mcp__srv__get_*` | a naming test enforcing one order |
| `mcp__srv__*` in allow | every tool added later is auto-approved, destructive ones included | reviewing rules per tier |
| Rename shipped with release notes | every saved allow rule stopped matching | an alias window (`cookbook/version-or-retire-a-tool.md`) |
| `list_changed` sent | under 2026-07-28 only subscribed clients hear it; others keep a cached list until `ttlMs` | a short `ttlMs` during rollouts |
| Big result returned whole | past 25k tokens Claude Code writes it to a file; past 10k it warns on every call | a size test with a realistic dataset |
| Description reads well | past the description budget in `references/clients.md` a client truncates it | a length test |
| Registry check passes | it ran over zero rows | assert the population is non-empty |
| Snapshot test green | the snapshot was regenerated in the same change without review | snapshot diffs reviewed as contract changes |
| Socket at `0600` | a peer running as the same user is not stopped by anything — the design implies more than it enforces | the honest-floor sentence in the design |
| HTTP bound to 127.0.0.1 | a web page reaches it through DNS rebinding; binding is not the fix | an `Origin` test expecting 403 |
| OAuth works | the server accepts any valid token, including ones minted for another audience, or forwards it upstream | an audience-mismatch test expecting 401 |
| Conformance run green | it ran the npm `latest` (0.1.x), which has no 2026-07-28 scenarios | the suite pinned to an exact 0.2 alpha, once per era served (`cookbook/test-a-server.md` § Step 3) |
