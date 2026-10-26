# Transport — the token path and the Slack MCP

- The token path and the Claude-app Slack MCP reach the same workspace and are not interchangeable: the MCP acts as whoever authorised the Claude app, carries no roster, and posts without the register, language and gate resolution the cookbooks apply.
- The Slack MCP (`mcp__*_Slack__*`) serves remote Claude-app integrations only, where that app is the acting surface and no local token is in play; reaching for it anywhere else breaches `SKILL.md § Rules`.
- A missing token, item or config never promotes the MCP → report Slack unwired per `SKILL.md § Project config`.

## Inside the carve-out

- Three traps make the connector look absent or unauthorised while it is present.
- Tool prefix → `mcp__Slack__<tool>` in a scheduled routine · `mcp__claude_ai_Slack__<tool>` in an interactive session; the interactive form in a routine fails as an unknown tool.
- A keyword tool search for `slack` returns nothing while the tool is there → resolve it by its exact name; that silence is not absence.
- Parameters → `channel_id` and `message`; `channel` returns `no_text`, and `channel` plus `message` returns an Internal Server Error.

## Markup on each route

- `chat.postMessage` takes mrkdwn, where a single asterisk is bold → `references/drafting.md § Markup`.
- The connector takes standard markdown and converts it before Slack sees it: a single asterisk arrives as italic → bold takes double asterisks.
- The `<url|text>` link form survives both routes.
