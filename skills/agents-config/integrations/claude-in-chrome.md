---
tool: claude-in-chrome
role: live-browser
status: default
secret: null
defaults:
  browser: Dia
---
# Claude in Chrome — user floor (live-browser)

Read by any consumer that needs the browser the person is signed into, through `~/.claude/skills/agents-config/scripts/agents-config get --role live-browser`.

- Off by default: the app's Connectors panel keeps it disabled, so a session starts without its `mcp__claude-in-chrome__*` tools.
- Needed and absent → enable it for this session with `mcp__ccd_connectors__set_session_connector_enabled`, or ask the person to switch it on in Connectors.
- The extension runs in Dia, not Google Chrome: Chrome's profile carries no extension.
