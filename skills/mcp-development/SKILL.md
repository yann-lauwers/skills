---
name: mcp-development
description: "Designs, builds, tests, secures and retires Model Context Protocol servers, in any stack, and wires them into clients. Use on 'build an MCP server', 'add an MCP tool', 'expose this over MCP', 'which MCP transport', 'MCP Inspector'; on writing a tool's name, description, `inputSchema`, `outputSchema` or `isError` result, a `registerTool` / `@mcp.tool` handler, an `.mcp.json` or `claude mcp add` entry, or an `mcp__` permission rule. Not for a CLI's flags — /cli-patterns ; not for an HTTP API's contract — /api-design ."
---

# MCP development

## Every file here

- Fetch the spec, never recall it: read `references/spec-revisions.md` § Confirm the current revision before citing any revision. Revisions from 2026-07-28 on have no `initialize` handshake, which every earlier revision required; clients are split across both eras.
- Tier first in every tool name, one tier per tool: clients permission MCP tools by name — Claude Code matches `mcp__<server>__<tool>` globs and ignores `readOnlyHint` for approval — and annotations are untrusted hints.
- A tool's own failure → an `isError: true` result with the next step in words; a protocol error only for an unknown tool or a malformed request.
- Nothing is proven until it has crossed a transport, in every era it serves, with a real client.

## Routing table

| Intent | Read |
| --- | --- |
| IF designing a new server — what it exposes, era, SDK, how its tool list stays true to the code | THEN `cookbook/design-a-server.md` |
| IF adding or changing one tool — name, schema, description, annotations, result, errors | THEN `cookbook/add-a-tool.md`, with `references/tool-design.md` |
| IF choosing or building a transport, a Unix socket or a stdio bridge | THEN `cookbook/choose-a-transport.md`, with `references/transports.md` |
| IF testing a server — in process, schema snapshots, Inspector, conformance, evals | THEN `cookbook/test-a-server.md` |
| IF renaming, retiring or changing a tool's contract | THEN `cookbook/version-or-retire-a-tool.md` |
| IF writing an `.mcp.json` / client config entry or `mcp__` permission rules | THEN `cookbook/wire-a-client.md`, with `references/clients.md` |
| IF citing a spec revision, or asked what "MCP v2" means | THEN `references/spec-revisions.md` |
| IF writing a handler against the wire — discovery, lifecycle, pagination, progress, cancellation, MRTR, errors | THEN `references/protocol-surface.md` |
| IF choosing an SDK, or working in the Swift SDK | THEN `references/sdks.md` |
| IF securing a server — local socket, HTTP authorization, the named attacks | THEN `references/security.md` |
| IF a design choice has a "how do the best teams do it" answer | THEN `references/leaders.md` |
| IF calling a server done, or it works in one client and not another | THEN `references/failure-modes.md` |
| IF the request matches none of the above | THEN `references/protocol-surface.md`, say which row was closest |

## Done when

- A server → done when its tool list derives from the code and a test fails the build on an empty list, a missing annotation, a name outside the rule or an unreviewed schema change; every tool's failures return `isError` results naming their fix; a client in process, the Inspector in each era the design names, and one real client session have each called it over the real transport; each transport control has a test seen red; and the design records era, SDK, transport and naming.
- A tool change → done when its snapshot diff and its tests are in the same change.
- A rename → done when both names are listed and the removal condition is written.
