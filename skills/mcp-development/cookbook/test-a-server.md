# Test a server

Four layers are all owed — the handlers, the contract, the wire, and a real model using it; which harness runs each follows the SDK.

## Step 1: Handlers, in process

1. Connect a client to the server with no socket: TypeScript `createMcpHandler(factory)` plus a client whose `fetch` calls `handler.fetch` (both eras; `InMemoryTransport.createLinkedPair()` is Legacy only); Python `Client(server)`; Swift `InMemoryTransport.createConnectedPair()`.
2. Per tool: the happy path; each domain failure returns `isError: true` with an actionable message; a schema-invalid argument returns `isError: true`, not a protocol error; an unknown tool returns `-32602`.
3. `structuredContent` validates against `outputSchema` — assert it, since the Swift SDK does not.
4. Cancellation: a cancelled call sends no result.

Done when every tool has a happy-path case and a failure case, run through a client, not by calling the handler function directly.

## Step 2: Snapshot the contract

1. Snapshot every tool's `name`, `description`, `inputSchema`, `outputSchema` and `annotations` to a committed file; fail the build on any difference, and regenerate only on purpose — GitHub's `toolsnaps` (`UPDATE_TOOLSNAPS=true go test ./...`) is the model.
2. Assert invariants over the whole list, not per tool: every tool sets `readOnlyHint`, `destructiveHint`, `idempotentHint` and `openWorldHint` explicitly; the name matches the naming rule and its tier prefix agrees with its annotations; names and descriptions stay inside the budgets in `references/clients.md` § What a server can rely on; the tool count stays under a cap (`references/tool-design.md` § The surface budget); no root-level `anyOf`/`oneOf`/`allOf`.
3. Where a registry generates the list, assert its population is non-empty — a check over zero rows passes.
4. Mutation-prove the invariants: delete one annotation, watch the test go red, restore.

Done when the snapshot file is committed and each invariant has been seen red once.

## Step 3: The wire

1. Smoke with the Inspector CLI, version pinned, once per era served: `npx --yes @modelcontextprotocol/inspector@<exact> --cli <server cmd> --method tools/list` and `--method tools/call --tool-name <t> --tool-arg k=v`. `--protocol-era legacy|modern` picks the era; exit 5 means the call returned `isError`; `tools/list --strict` lints schema portability (exit 6). It is not a JSON Schema validator.
2. Conformance: `npx @modelcontextprotocol/conformance@<exact 0.2 alpha> server --url <http url> --requirements <revision>` checks every message against the spec schema. Run it once per era served (`cookbook/design-a-server.md` § Step 2: Pick the era) — `2026-07-28` for Modern, `2025-11-25` for Legacy — each with its own baseline and its own CI job. The suite covers the `dns-rebinding`, `stateless`, `caching` and `input-required-result` scenarios. The npm `latest` (0.1.x) has none of the 2026-07-28 scenarios, so an unpinned run passes having tested nothing of the current revision. It takes an HTTP URL only — a stdio or socket server needs a thin HTTP wrapper to be scored. CI: the `modelcontextprotocol/conformance` action pinned to the same alpha, with an `expected-failures` baseline.
3. A custom transport gets its own wire tests: framing (one message per line, no embedded newline), EOF handling, a malformed line answered with `-32700` without killing the connection, the access controls from `cookbook/choose-a-transport.md` § Step 3 (a foreign uid refused, file modes, the path-length refusal).
4. stdio: assert nothing but JSON-RPC reaches stdout — run the server, send one request, parse every stdout line.

Done when the Inspector lists and calls a tool over the real transport with `--protocol-era` set to each era served, conformance has run once per era served, and each transport control has a test that has been seen red.

## Step 4: A real client and a real model

1. Wire the server into Claude Code (`cookbook/wire-a-client.md`) and drive one tool from a real session; this is what proves the name, the description and the permission rule together.
2. Tool-selection evals: give a model the real `tools/list` and realistic tasks, and score whether it picks the right tool with the right arguments — Sentry's `toolPredictionScorer` does this without executing anything, so it is cheap to run on every description change.
3. Task evals, per Anthropic's "Writing effective tools for agents": realistic multi-call tasks with verifiable outcomes; track tool calls, errors, tokens and runtime; read the transcripts; hold out a test set.

Done when one real client session has called the server, and the selection eval runs in CI or on demand with a recorded score.
