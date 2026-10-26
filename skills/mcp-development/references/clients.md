# Clients

Each row was read from the client's own docs or source on 2026-09-22; clients move monthly, so re-read the row a decision depends on.

## What a server can rely on

- Serve both eras. 2026-07-28 is on by default only in Claude Code (remote HTTP; stdio stays on the handshake unless `MCP_PROTOCOL_NEGOTIATION=auto`) and verified in goose; Codex has it behind an off flag; VS Code and Zed send `2025-11-25`. Implement `server/discover` and keep answering `initialize`. A modern client may probe `server/discover` first on stdio.
- Transports — stdio plus Streamable HTTP is the common set; ChatGPT takes remote only, at `/mcp`.
- Primitives — tools everywhere; resources, prompts and elicitation are enhancements some clients lack (Zed has no resources or elicitation). Always keep a path that uses tools alone.
- Name budget — `[A-Za-z0-9_-]` only (the Claude API regex has no `.`). The tool name itself at most 64 characters (the claude.ai directory's cap). The prefixed name at most 63: Gemini truncates `mcp_<server>_<tool>` past 63, so server name + tool name + 5 ≤ 63. Claude Code's own limit on `mcp__<server>__<tool>` is undocumented; Codex caps its prefixed name at 128. Gemini splits on the first `_`, so the server name carries none.
- Description budget — 1,024 characters, the point first. Claude Code truncates descriptions and server `instructions` at 2KB; Sentry's test records 1,024 as the VS Code (via OpenAI) limit and caps its own at 2,048.
- Count — well under 100 tools per server (Devin's cap across all servers; VS Code refuses above 128 per request).
- Size — under ~25k tokens per result (Claude Code's cap); paginate; send `structuredContent` plus a text copy.
- Time — answer within 60 s (Codex's default); longer work reports progress or uses the tasks extension.
- Annotations — set `title` and all four hints on every tool. They drive approval in VS Code, Codex, goose and the claude.ai directory; ChatGPT review rejects write tools missing them.

## The matrix

| Client | Transports | 2026-07-28 | Approval driven by | Limits worth knowing | Config |
| --- | --- | --- | --- | --- | --- |
| Claude Code | stdio, http, sse (deprecated), ws | yes for http; stdio opt-in | **tool name rules only** | output 25k tokens; descriptions and `instructions` cut at 2KB; property names 1–64 chars | `.mcp.json`, `~/.claude.json` |
| claude.ai connectors | remote | unstated | annotations: read-only runs, destructive always prompts | names ≤ 64; ~150k chars; 240 s | UI |
| ChatGPT | remote (`/mcp`), tunnel | unstated | manual confirmation on writes; all three hints required for review | `instructions` key facts in the first 512 chars | UI (developer mode) |
| Codex CLI | stdio, http | behind `mcp_2026_07_28` | `default_tools_approval_mode = "writes"` prompts non-read-only | callable names 128 chars; 60 s | `~/.codex/config.toml` `[mcp_servers.<name>]` |
| VS Code | stdio, http, sse; HTTP over `unix://` sockets | no (2025-11-25) | confirms every tool without `readOnlyHint` | 128 tools per request | `.vscode/mcp.json`, root key **`servers`** |
| Cursor | stdio, http, sse | unstated | approval by default; allowlist | — | `.cursor/mcp.json` `mcpServers` |
| Gemini CLI | stdio, http, sse | no evidence | `trust`, include/exclude lists | names > 63 truncated | `.gemini/settings.json` |
| Zed | stdio, http | no (2025-11-25) | `mcp:<server>:<tool>` permission keys | tools and prompts only | `settings.json` `context_servers` |
| goose | stdio, streamable_http | yes, conformance-verified | `readOnlyHint` feeds Smart Approve | — | `~/.config/goose/config.yaml` |

## Claude Code in detail

From `https://code.claude.com/docs/en/mcp` and `/permissions`.

- Scopes — `local` (default; `~/.claude.json`, this project only), `project` (`.mcp.json` at the repo root, shared), `user` (`~/.claude.json`, every project). Same name in several → local > project > user > plugin > connectors; the winning entry is used whole, never merged.
- `.mcp.json` — `{"mcpServers": {"<name>": {"type": "stdio", "command", "args", "env"}}}` or `{"type": "http" | "sse" | "ws", "url", "headers", "headersHelper", "oauth": {…}}`, plus `timeout` and `alwaysLoad`. An entry with `url` and no `type` is rejected. Server keys: letters, digits, `-`, `_`.
- Expansion — `${VAR}` and `${VAR:-default}` in `command`, `args`, `env`, `url`, `headers`. A missing variable leaves the literal text and warns. `${CLAUDE_PROJECT_DIR}` in `command`/`args` needs a default (`${CLAUDE_PROJECT_DIR:-.}`).
- Approval — interactive sessions ask before using a project's `.mcp.json` servers; a cloned repo cannot approve its own servers before workspace trust. `-p`, the Agent SDK and cloud sessions load them without asking.
- Permission rules — `mcp__<server>` or `mcp__<server>__*` (every tool on the server), `mcp__<server>__<tool>`, and globs after a literal prefix — `mcp__github__get_*`. An allow glob with no literal `mcp__<server>__` prefix (`mcp__*`) is skipped with a warning; deny and ask accept it. Deny beats ask beats allow, across every scope. Rules with parentheses are skipped in settings; argument matching exists only as an exact-value `--disallowedTools` deny on the CLI.
- Annotations — `readOnlyHint` lets read-only tools run in parallel; the other hints are "Informational only". Nothing auto-approves from annotations — which is why the risk tier belongs in the tool's name.
- Server-side levers — `_meta["anthropic/requiresUserInteraction"]: true` (Claude Code 2.1.199 and later) shows the permission prompt on every call, even in `acceptEdits`, `auto` and `bypassPermissions`, with no "don't ask again", and allow rules do not skip it. Where no person can answer it refuses instead: `dontAsk` mode denies the call, and under an MCP `--permission-prompt-tool` an allow becomes a deny — so a tool carrying it never runs headless behind a prompt tool. It is the one lever that raises the gate; none lowers it. `_meta["anthropic/maxResultSizeChars"]` raises one tool's text threshold up to 500,000 characters. `_meta["anthropic/alwaysLoad"]: true` exempts a tool from deferral.
- Tool search — on by default: only tool names and server `instructions` load at session start. The `instructions` field says what tasks the server handles and when to search for it — it is how the tools get found.
- Output — warning at 10,000 tokens, cap 25,000 (`MAX_MCP_OUTPUT_TOKENS`); larger results are written to a file and Claude gets the path.
- Schemas — a root-level `anyOf`/`oneOf`/`allOf` is flattened into prose, so validate the combination server-side; a tool with an invalid schema is dropped individually.
- `list_changed` — refreshes tools, prompts and resources; under 2026-07-28 it arrives on a held-open `subscriptions/listen` stream.
- Plugins — bundle servers in the plugin's `.mcp.json` or `plugin.json`; their tools are named `mcp__plugin_<plugin>_<server>__<tool>`.

## Distribution

- Official registry (`registry.modelcontextprotocol.io`, preview, API `v0.1` frozen) — `server.json` (schema 2025-12-11) naming packages (`npm`, `pypi`, `nuget`, `cargo`, `oci`, `mcpb`) or remotes. Namespace proven by GitHub login (`io.github.<user>/*`), DNS TXT, or `/.well-known/mcp-registry-auth`. CLI `mcp-publisher init | login | publish`.
- `.mcpb` bundles — a zip of a local stdio server and `manifest.json`; Claude's secondary route after remote servers.
- MCP Apps (`io.modelcontextprotocol/ui`, final) — a tool's `_meta.ui.resourceUri` points at a `ui://` HTML resource the host renders in a sandbox. Progressive enhancement — the tool must still work as plain MCP.
- Server Cards (`.well-known` discovery) and a standard client `mcp.json` are proposals, not standards; every client keeps its own config shape.
