# Add a tool

One tool, from name to a test that proves it, in any SDK; every step is owed, its wording is judgement.

## Step 1: A tool, and its tier

1. The model decides to call it → a tool · context the host attaches → a resource · a template the person picks → a prompt.
2. Tier — read: changes nothing · write: changes, recoverably · remove: loses something. A tool that returns a secret, or content carrying one, is a write whatever it does to state (`references/security.md` § Every server).
3. One tier per tool: an operation that is a read for one argument and a delete for another is two tools.

Done when the tier is named, with the effect that decided it.

## Step 2: Name it

1. Tier first, then the resource (`references/tool-design.md` § Names carry the risk tier), or the server's existing convention where it already puts one tier word first; one order across the whole server.
2. Snake case, `[A-Za-z0-9_-]`, inside the length budget in `references/clients.md` § What a server can rely on.
3. Grep the existing list for the same verb: two tools that sound alike get picked at random.

Done when the name passes the server's naming test (`cookbook/test-a-server.md` § Step 2).

## Step 3: The schema

1. Derive it from the typed input where the SDK can (TypeScript Standard Schema, Python type hints, a Swift schema macro or generator); hand-write it only where nothing derives.
2. `type: "object"` at the root, `additionalProperties: false`, required fields listed, enums for closed sets, a description on every property, small defaults for limits.
3. No root-level `anyOf`/`oneOf`/`allOf`.
4. An `outputSchema` when the result has a shape a caller will parse.

Done when the schema validates as JSON Schema 2020-12 and every property has a description.

## Step 4: The description

1. First sentence: what it does. Then when to use it and when not, what it returns and what it leaves out, limits and how to get past them, related tools.
2. Inside the description budget in `references/clients.md` § What a server can rely on; the point first.
3. Read it as a model that has never seen the server: the description alone picks this tool over its neighbours.

Done when the description names its limits and at least one neighbouring tool it is not.

## Step 5: Annotations

1. Set all four explicitly — `readOnlyHint`, `destructiveHint`, `idempotentHint`, `openWorldHint` — plus `title`; some SDKs cannot tell an unset boolean from `false`.
2. Derive the first two from the tier, never by hand per tool: read → `readOnlyHint: true`; write → `readOnlyHint: false, destructiveHint: false`; remove → `readOnlyHint: false, destructiveHint: true`.
3. Set `openWorldHint` and `idempotentHint` per tool, each with its reason carried by a test named for the reason: `openWorldHint` is whether the tool reaches anything outside the server's own domain, `idempotentHint` whether the same arguments twice leave the same state.
4. A remove-tier tool needs a person in the loop through a mechanism, never through a hint: the server-set `_meta["anthropic/requiresUserInteraction"]: true` in Claude Code (with the cases where it refuses instead — `references/clients.md` § Claude Code in detail), or an out-of-band approval the tool returns before it acts — an approval URL, or elicitation.

Done when all four hints are set, the first two agree with the tier in the name, and the other two carry their reason.

## Step 6: The result and the errors

1. Return what the next step needs: meaningful identifiers, no noise fields, `structuredContent` plus its text copy.
2. Bound the size: a default limit, a cursor or `hasMore`, a truncation notice that says how to get the rest.
3. Every domain failure — not found, not allowed, invalid argument, upstream down — is `isError: true` with what went wrong and the next call; never a protocol error.

Done when each failure the tool can meet has a message naming its fix.

## Step 7: Test it

1. Through a client, in process: the happy path and each failure (`cookbook/test-a-server.md` § Step 1).
2. Update the schema snapshot and see the invariant tests pass.
3. Where a selection eval exists, add a task that should pick this tool and one that should not.

Done when the tool's cases pass through a real client transport and the snapshot diff is in the change.
