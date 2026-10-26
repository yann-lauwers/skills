# Tool design — what a model uses well

Sources: Anthropic's "Writing effective tools for agents" (`https://www.anthropic.com/engineering/writing-tools-for-agents`), the Claude tool-use docs (`https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools`), and the source of github-mcp-server, playwright, sentry-mcp and the reference servers, read 2026-09-22.

## Which tools to build

- "More tools don't always lead to better outcomes. A common error we've observed is tools that merely wrap existing software functionality or API endpoints." Build for workflows: `search_logs` over `read_logs`; `get_customer_context` over three lookups; `schedule_event` over list-then-create.
- Anthropic's API docs also say to fold `create_pr`/`review_pr`/`merge_pr` into one tool with an `action` parameter — only within one risk tier: clients permission by name, and Claude Code cannot match arguments in settings, so a read and a delete behind one name get one rule. GitHub's `actions_run_trigger` puts a workflow rerun and a log deletion behind one name — the counter-example.
- A surface whose contract is completeness — every command an app has is drivable from outside — is the exception to "don't mirror the API": there one tool per command is the requirement, and a registry that generates them is what keeps the surface complete. Budget the count all the same.
- Ask whether MCP is the right primitive at all. Playwright's own README now points coding agents at its CLI plus skills, "because CLI invocations are more token-efficient". MCP earns its place where a client needs the schema, persistent state, or no shell.

## Names carry the risk tier

- Put the tier first — `read_…`, `write_…`, `remove_…` — one word per tier, never a family of verbs. One allow glob then approves every read — `mcp__srv__read_*` — and a deny or ask glob catches every removal, with no way to sweep a destructive tool in by accident.
- One order, enforced by a test. GitHub mixes `get_file_contents` with noun-first `issue_read`, so `mcp__github__get_*` misses `issue_read`.
- Snake case, inside the name budget in `references/clients.md` § What a server can rely on.
- Namespace by resource after the tier (`read_invoice_status`, `remove_invoice`) when the server is large; clients already namespace by server. Anthropic measured prefix-versus-suffix namespacing to have "non-trivial effects" that vary by model — pick one and evaluate it.
- A read tool that returns a credential, a secret or content carrying one is not a read (`references/security.md` § Every server).

## Descriptions

- "Provide extremely detailed descriptions. This is by far the most important factor in tool performance" — what it does, when to use it and when not, each parameter, and what it does not return. Three or four sentences at least.
- Budget: the description budget in `references/clients.md` § What a server can rely on; lead with the point.
- Say how to recover from the tool's limits: "Returns up to 25 results. When hasMore is true, use the query parameter to narrow down results." (sentry-mcp)
- Name related tools ("use `read_invoice_list` first to get an id").
- State a handle's lifetime in the tool that mints it.
- No system-prompt voice in descriptions or results — no `IMPORTANT`, `MUST`, `CRITICAL` aimed at the model (sentry-mcp's response contract bans it).

## Inputs

- Unambiguous names: `user_id`, not `user`.
- Enums over free strings; defaults that keep responses small.
- No root-level `anyOf`/`oneOf`/`allOf` — Claude Code flattens it and sentry-mcp bans unions outright. Two shapes is two tools, or one flat object with optional fields.
- `additionalProperties: false`; `{ "type": "object", "additionalProperties": false }` for no arguments.
- A human-readable twin beside a machine handle when the call will be shown for approval: Playwright pairs `target` (a ref) with `element` ("Submit button"), so the prompt shows words.
- Semantic, stable identifiers in, the same identifiers out; resolve short refs (`invoice:3`) client-side and send ids on the wire.

## Responses

- "Return only high signal information" — names over UUIDs, no `mime_type`/`256px_image_url` noise. Anthropic measured that replacing opaque ids with meaningful ones "significantly improves Claude's precision".
- `structuredContent` against an `outputSchema`, plus the same data as text. Never put unique data on only one side (sentry-mcp).
- Size: filter, paginate, truncate, with small defaults, inside the size budget in `references/clients.md` § What a server can rely on. Give a selector for heavy fields (GitHub's `fields` enum, Anthropic's `response_format: concise | detailed`); write large artefacts to a file and return the path (Playwright's snapshot files); keep the tail of logs, not the head (GitHub's ring buffer).
- A truncated result says it was truncated and how to get the rest.
- Suggested next calls, when they save a turn: sentry-mcp's `suggestedActions: [{ toolName, arguments, reason }]`, at most three, complete enough to call without re-parsing.
- Untrusted text relayed from elsewhere is marked as such and scrubbed of invisible and BiDi characters (GitHub's `sanitize` package).

## Errors

- Tool failures are `isError: true` results in words the model can act on: what went wrong, why, and the next call. "Invalid departure date: must be in the future. Current date is 08/08/2025."
- Say who can fix it (sentry-mcp): the model (bad input — retry with X), the person (re-authorize, grant access), or nobody right now (service down — other tools still work; an event id to report).
- A refusal because of state names the state and the tool that clears it (Playwright: a pending modal names the tool that handles it).

## The surface budget

- Tool count: stay well under 100 per server; Sentry keeps ~20 visible, never over 25, enforced by a test, and routes the long tail through `search_…` + `execute_…` meta-tools. A meta-tool is one name for many operations — mark it destructive, since name-based rules can no longer tell them apart, or split it by tier the way Atlassian does (`executeRead`, `executeWrite`, `executeDestructive`).
- A very large API: Cloudflare's server-side code mode — `search` and `execute` tools taking code that runs in a sandbox with no outbound network — beat one tool per endpoint by three orders of magnitude in tokens. Pays off past a few hundred operations; below that, workflow tools win.
- Money, deletion, anything irreversible: a person approves out of band. Stripe returns an approval URL and the agent retries with the token it yields; under 2026-07-28 that is URL-mode elicitation through an `InputRequiredResult`.
- Surface switches: GitHub's `--toolsets`, `--read-only` (which wins over any explicit tool request) and `--exclude-tools`; Playwright's `--caps`; Sentry's skills with writes off by default. A read-only switch that overrides everything is the pattern to copy.
