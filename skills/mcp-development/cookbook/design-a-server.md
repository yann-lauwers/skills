# Design a server

What a new MCP server exposes, which protocol era it speaks, which SDK carries it, and how its tool list stays true to the code — decided before the first handler exists; every step is a decision the design owes, and Step 2's era is the one that is expensive to change later.

## Step 1: Who calls it, for what

1. Name the clients (`references/clients.md` § The matrix) and the three to five workflows they must complete.
2. Ask whether MCP is the right primitive (`references/tool-design.md` § Which tools to build).
3. Name the transport now — `cookbook/choose-a-transport.md` — since it decides the era's cost.

Done when the clients, the workflows and the transport are written in one paragraph.

## Step 2: Pick the era

1. Confirm the current revision (`references/spec-revisions.md` § Confirm the current revision).
2. Dual-era is the default today (`references/clients.md` § What a server can rely on). A Modern-only server loses every Legacy client. A Legacy-only server keeps today's clients — dual-era clients probe `server/discover` and fall back to `initialize` — and loses only clients that speak Modern alone, which grow with every SDK release.
3. Modern-only is right where every caller is known and modern (an internal fleet on current SDKs). Legacy-only is right only when the SDK chosen in Step 3 cannot yet do better — and then the design names the migration: `server/discover`, `_meta` per request, no per-connection state.
4. Whatever the era, write handlers as if stateless: no state tied to a connection, cross-call state as explicit handles. That code survives the move to Modern unchanged.

Done when the eras served — one of Modern, Legacy, or both — are written down with the client list that decided them, and any Legacy-only choice names its migration trigger; every later step, test and Done-when reads that set rather than restating a default.

## Step 3: Pick the SDK

1. Read `references/sdks.md` § The matrix. Prefer a Tier 1 SDK that speaks both eras.
2. Swift is Tier 3 and Legacy-only (`references/sdks.md` § The matrix) → one of three options, decided by the clients from Step 1 and who maintains the protocol code:
   - The official SDK, Legacy era, with a hand-built registry generating `Tool` values and hand-built schema validation — least code now, a migration later when the SDK catches up.
   - A thin JSON-RPC layer of the server's own over the transport, dual-era from day one — a tools-only server implements a small part of `references/protocol-surface.md` (discovery and the Legacy lifecycle, `tools/list` and `tools/call` with their required result fields, errors), and the conformance suite checks it behind an HTTP wrapper; every spec change is the server's to carry.
   - The official SDK plus the community `@Schemable` macro for schemas — adds a pre-1.0 dependency to the build.
3. TypeScript: `@modelcontextprotocol/server` 2.x, not `@modelcontextprotocol/sdk` 1.x, for new code. Python: `mcp` 2.x `MCPServer`.

Done when the SDK and version are named, and what the SDK leaves to the server (schema derivation, validation, eras) is listed as work.

## Step 4: Shape the surface

1. Tools by workflow, one risk tier each, tier first in the name (`references/tool-design.md`).
2. Budget the count, and route a large API, per `references/tool-design.md` § The surface budget.
3. A surface switch that wins over everything: a read-only mode, tools hidden when the caller lacks the scope.
4. Irreversible acts get a person in the loop, through a mechanism in `cookbook/add-a-tool.md` § Step 5: Annotations.
5. Resources and prompts only where a client will use them; tools alone must complete every workflow.
6. Server `instructions`: what the server is for and when to search for its tools, inside the description budget in `references/clients.md` § What a server can rely on.

Done when every workflow from Step 1 maps to named tools, each with a tier.

## Step 5: The tool list derives from the code

1. One registry is the population: `tools/list`, the dispatcher and any CLI help render from it. The dispatcher switches over it with no default case.
2. Schemas derive from the handler's typed input; annotations derive from the tier; names are checked against the naming rule — all in a test over the whole registry (`cookbook/test-a-server.md` § Step 2).
3. Commit a manifest of names and schemas; the build fails when the code and the manifest differ, and when the registry is empty.

Done when adding a tool is one file and one manifest diff, and forgetting either fails the build.

## Step 6: Name the controls

1. Transport controls from `cookbook/choose-a-transport.md` § Step 3.
2. The honest floor, in a sentence: what the transport enforces and what it does not.
3. What never goes in a read tool: credentials, secrets, content carrying either.
4. Response bounds and the truncation message.

Done when each control is named with the test that will prove it.

## Step 7: Record the design

1. In a repo that keeps decision records → era, SDK, transport and naming are one record each.
2. The custom transport's connection, framing and cancellation → written per `cookbook/choose-a-transport.md` § Step 4: Write it down.

Done when the four decisions are written where the next implementer reads them.
