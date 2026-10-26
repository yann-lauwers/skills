---
name: browser
description: "Drives a real browser from the shell through `pw` — a page the fetch tools return empty, a site the user is signed into, a screenshot of a real page. Use on 'browse to', 'click through', 'scrape behind the login', 'open it in a browser', or a WebFetch that came back as a script shell or login wall. Also fires before the first `pw` command of a session, before `browser-login`, and before `open -a` with `--remote-debugging-port`. Not for a public post on X — /x ; not for learning which request an action sends — the API-discovery pass; not for signing into claude.ai — the claude.ai sign-in skill."
user-invocable: false
---

# Browser

- `pw` — a wrapper over `@playwright/cli`.
- Isolated is the default; a signed-in tab is earned by the task naming one.

## Project config

`~/.claude/skills/agents-config/integrations/playwright.md`, read with `~/.claude/skills/agents-config/scripts/agents-config get playwright <key>` — `cdp_endpoint`, `profile_browser`, `default_identity`, `identities`. Absent → `~/.claude/skills/agents-config/scripts/agents-config role browser`; still nothing → say the browser tool is unwired.

- `identities.<name>.profile` — the `profile_browser` profile holding that identity's tabs.
- `dispatch: allowed` — a dispatched run may load its session file · `interactive-only` — reachable only through the live tab, with the user present.
- `environments` — the identity's service has several; a session file is per environment.

## Pick the mode, then check it answers

| The task | The mode |
| --- | --- |
| read a page a fetch returned empty · screenshot a local file or a build · click through a site open to anyone | `pw <command>` — headless, one per Claude session, signed out; a login loads under its own `PW_SESSION` |
| a page behind a login · anything the request scopes to an identity | `pw --live <command>` — attaches to the everyday browser over CDP, in a tab of its own |

- `command -v pw` finds nothing → say so; take the vendor's API, an embed or a feed instead.
- Live: `curl -s <cdp_endpoint>/json/version` answers no `Browser` field → `pw --live` exits 3; relaunching is `references/cdp.md`.
- A live route resolves an identity: the request's, else `default_identity`. Name it before acting and confirm the tab's account — `pw --live` cannot choose a profile; never carry two identities in one run.

## Using it

- `pw [--live] <command> [args] [flags]`; `pw --help` lists commands, `pw --help <command>` its flags. A recipe's `-s=<name>` becomes `PW_SESSION=<name>`.
- Quote every URL: zsh globs `?`.
- The first command opens the browser; parallel calls never start a second and act on one tab — run its commands in sequence.
- Snapshots and unnamed screenshots land in `./.playwright-cli/`; a `--filename` lands in the working directory.
- A subagent on its parent's browser never runs `pw close`; one browsing beside its parent or a sibling prefixes `PW_SESSION=<name>`. `pw close` ends this session's browser.

## Routing table

| Intent | Read |
| --- | --- |
| IF reaching a page the person is signed into — relaunching on the debugging port, reading without dumping tokens | THEN `references/cdp.md` |
| IF the question is which browser a mode drives, or extension mode came up | THEN `references/connection-modes.md` |
| IF a browser window appeared in front of the person, or the isolated config has to change | THEN `references/isolated.md` |
| IF the request names an identity, a run needs a login, or `browser-login` is about to mint | THEN `references/session-files.md` |
| IF `pw` itself misbehaves or is upgraded | THEN `references/operating.md` |
| IF a dispatched agent needs a scripted browser of its own | THEN the `yann:browser-pilot` agent |
| IF the request matches none of the above | THEN `references/connection-modes.md`, name the closest row |

## Acting inside a session the user is signed into

- A live route, or an isolated browser after `pw state-load`, carries real credentials: a click there can send, buy or delete with no on-screen signal.
- Navigate, snapshot, screenshot, console and network reads proceed unconfirmed.
- A write — submitting a form, sending, buying, paying, deleting, accepting terms → the user's confirmation first, naming the site and action; one confirmation covers the whole approved sequence.
- Work in a tab you created, return it to where it started when done, and say which tab was driven.
