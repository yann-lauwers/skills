---
name: claude-design
description: "Publishes a repo's design system to its Design System Artifact in Claude, synced from code, removes what the export no longer holds, and reads the published system back. Use on 'publish the design system', 'update the designs', 'put it in Claude Design', 'the component is blank on the page', 'which account owns the design system', or a Design System Artifact link. Also fires before an Artifact publish to a design system's link and before any `DesignSync` call. Not for what to draw — /impeccable ; not for the house identity — /house-style ; not for claude.ai sign-ins — /claude-login ."
allowed-tools: Read, Glob, Grep, Artifact, Bash(~/.claude/skills/agents-config/scripts/agents-config *), Bash(claude-login *), Bash(~/.local/bin/claude-login *), Bash(node ~/.local/share/claude-login/examples/*)
---

# Claude Design

- A hosted design system is an Artifact made from the Design System type, its content under `project/` and its page the type's own.
- Standalone Claude Design (claude.ai/design) closes on December 14, 2026, and `DesignSync` writes only there → never push through it.
- A system synced from code carries `"editing": "code"` in its index, `project/design-system.json`: its page is read-only, and each publish sends every file the repo's export wrote.
- An Artifact belongs to the account that published it · a publish names the system's link as `url` · one without it makes a second system.
- Another account publishes only once the owner shares the Artifact with it for editing, from the page's Share menu.

## Project config

- Config — `~/.claude/skills/agents-config/integrations/claude-design.md`, the floor, and `<repo>/docs/agents/integrations/claude-design.md` over it.
- `~/.claude/skills/agents-config/scripts/agents-config get claude-design --root <repo>` → `artifact` (the system's link, null until a first publish creates it), `mirror`, the repo's `design_owner`, and under `accounts` that owner's address.
- `medium` resolves to `artifact` → this skill runs · anything else, and no calling skill names a target → the repo publishes nowhere here.

## Routing

| IF | THEN |
| --- | --- |
| the work only draws, or reads a design system to build against it | nothing here |
| publishing a repo's export, or creating its first system | `cookbook/push.md` |
| a preview's contract — its marker, what the frame preloads, the bundle | `references/card.md` |
| a component missing, blank or broken on the page | `cookbook/troubleshoot.md` |

## Pushing

- Every publish runs `cookbook/push.md`, steps in order; a repo whose own design skill carries a push cookbook runs that one, built on these steps.
- Which commit, which exporter and when → the calling skill says.
