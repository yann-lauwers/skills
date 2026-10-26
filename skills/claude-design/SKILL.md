---
name: claude-design
description: "Pushes cards into a Claude Design design-system project through the `DesignSync` tool, reads them back, and mints the design login so the push lands on the owner's account. Use on 'put it in Claude Design', 'push the cards', 'the card is blank in the pane', 'which account do the designs go on', 'it says not authorized', 'run the design login'. Also fires before a session's first `DesignSync` call and before pushing `_ds_manifest.json` or `_ds_bundle.js`. Not for what to draw — /impeccable ; not for the house identity — /house-style ; not for other claude.ai sign-ins — /claude-login ."
allowed-tools: Read, Glob, Grep, DesignSync, Bash(~/.claude/skills/agents-config/scripts/agents-config *), Bash(claude-login *), Bash(~/.local/bin/claude-login *), Bash(cswap list*), Bash(cmux *), Bash(node ~/.local/share/claude-login/examples/*), Bash(python3 -c *)
---

# Claude Design

- A design-system project at claude.ai/design shows each card in its Design System pane; a project and its id belong to one Claude account.
- `DesignSync` ships its own commands, `/design-sync` and `/design-login`, named in the tool's own description → judge a design command against that description, never by its absence from skill, command, archive or plugin directories.
- `/design-sync` syncs one component at a time, never a wholesale replace · a session that cannot type it → § Pushing drives the tool directly, to the same bound.
- Access is a design login: `/design-login` writes a grant into the credential item of the session's config directory — `~/.claude`, the shared login, for every session started with plain `claude` — approved as one Claude account, and `DesignSync` reads it whatever account spends the quota.
- Minting that grant is this machine's act, never a question for the user, except where claude.ai's picture check stops the act → `cookbook/authorize.md`.
- Every `cswap switch` rewrites the shared login's credential item and the grant goes with it · a grant lost mid-work → re-mint it, never push or draw anywhere else.

## Routing

| IF | THEN |
| --- | --- |
| the work only draws — an artboard, a mock, a screen on a canvas — or reads a design system to build against it | nothing here: no grant needed |
| a write needs a grant this session does not hold — `list_projects` answered not-authorized, or another owner's | `cookbook/authorize.md` |
| finding the project, writing, deleting or reading back cards | § Project config and § The project, then `cookbook/push.md` |
| a card's marker, its fonts, or the bundle it draws from | `references/card.md` |
| the pane's card index, `_ds_manifest.json` | `references/manifest.md` |
| a card missing, blank or broken in the pane | `cookbook/troubleshoot.md` |

## Project config

- Config — `~/.claude/skills/agents-config/integrations/claude-design.md`, the floor, and `<repo>/docs/agents/integrations/claude-design.md` over it.
- `~/.claude/skills/agents-config/scripts/agents-config get claude-design --root <repo>` → the `project`, its `mirror`, the repo's `design_owner`, and under `accounts` the Claude account holding that owner's projects.
- `medium` resolves to anything but `claude-design` and no calling skill names the project → the repo publishes nowhere here; nothing in this skill runs for it.

## The project

- A calling skill that names the project names its owner too.
- Find the project by name with `list_projects` immediately before each push; never keep its id.
- Not authorized → this config directory holds no design login → `cookbook/authorize.md` mints one as the owner's account, and the push then runs here.
- Other projects, not this one → the login is the owner's and the project is new → `create_project` with the name, then `get_project` confirms `PROJECT_TYPE_DESIGN_SYSTEM`.
- Empty, or another owner's projects → the login belongs to another account → stop and name the owner's account; never push under it.

## Pushing

- Every push runs `cookbook/push.md`, steps in order; a repo whose own design skill carries a push cookbook runs that one, built on these steps.
- Which commit, who and when → the caller says.
