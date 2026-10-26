---
name: managing-harness
description: "Writes, changes and removes this setup's canon — rules, skills, agent files, CLAUDE.md, AGENTS.md — picks the home and config level a fact takes. Use on 'new rule/skill/agent', 'edit CLAUDE.md', 'retire a skill', 'optimize this file', 'where does this fact belong', 'it ignored the rule'. Also fires on a correction about to be recorded so it holds next time, an Agent brief or stored prompt about to be written, a vendor's name about to enter canon, a fact about to go into a file opened for another reason, a tool, a new service or vault item wired or named, a one-home breach the user flags, and on any edit under ~/.agents/{skills,agents,docs,settings,bin}/, a repo's docs/agents/ or its .claude/settings*.json; also a pack authored elsewhere installed. Not for a hook — /hook-development ."
user-invocable: true
---

# Managing Harness

Every canon body — rule, skill, agent, format, command, prompt, `CLAUDE.md`/`AGENTS.md`, doc — follows § How we write; each kind adds its own conventions in the reference § Read this first names.

## How we write

- One directive per line, in the shortest form that keeps it:
  - an act → an order: `Follow hexagonal architecture.`
  - a standing property → a norm: `One concern per file.`
  - a trigger → `condition → action`: `Simple question → plain prose, 1–3 sentences.`
  - a term's definition → `term — what it is`: `Port — a Sendable protocol with one async requirement.`
- Drop what the file already implies — its own subject, the reader as actor ("you", "we", "a session", "Claude"), a lead-in: `Nutshell follows hexagonal architecture.` in Nutshell's own rule → `Follow hexagonal architecture.`; an actor who isn't the reader — the user, another agent — stays.
- A bare line is the default, held unless the case gives a reason to depart; `never`, `always`, `only`, `no` and `every` mark a line with no exception.
- A set of options takes one line: `nothing owed · their decision · something running`.
- Every word earns its place; a dash, `only` or `where` that narrows is meaning: dropping one widens the line, adding one narrows it.
- Only this setup's own conventions, setup and decisions; a line the model's default, Claude Code, the output style, another file that loads wherever this one loads, a check, a permission rule or a hook in `~/Code/skills/plugins/yann/hooks/REGISTRY.md` enforcing it already covers → cut; a skill whose subject is canon keeps the facts of its own subject, per `references/skills.md` § Citing a sibling.
- State the mechanism, never the incident: delete the domain noun and what survives is the line; nothing survives → drop it, and judge it afresh if it recurs.
- A directive a reader would otherwise judge by quality → names what checks it — the command, path, value or tool.
- No reasons: measurements, dates, "why" and stories stay out; a reason that sets the line's scope or stops a reader refusing a legitimate step stays as one clause.
- A recorded call keeps its one-line provenance: date, route, result.
- No examples, unless the example is the rule.
- Draw the boundary between an agent, a skill, an instruction file and a config where their concepts differ.
- A set that grows on its own → name where it lives, never its members.
- Markdown: an H1, a few `##` groups, bullets; a tag only where a reader parses it or it delimits a prompt template; emphasis — capitals, bold, a warning glyph — only on a line seen ignored, never on two in one file.
- Frontmatter → every key matches the supported-fields table in Claude Code's skills, sub-agents or commands reference, since a misspelt key is dropped without error and no validator catches it; a skill, agent or command touched → `claude plugin validate --strict` on its `skills/`, `agents/` or `commands/` directory exits 0 before it lands, which proves only that the YAML parses.
- Many acceptable answers → a direction · a wrong step breaks something — a migration, a guard, an irreversible act → numbered steps, each with its done state · otherwise → bullets.
- Restructuring or rewriting a file's lines wholesale → bring the whole file to this section in the same change, through `cookbook/optimize.md`; a fix, a repoint or an added line → those lines alone; every other edit → the lines it touches.

## Where a fact goes

- The first rung that can hold a fact is its home:
  1. Reading the code yields it — a layout, a dependency list, an architecture tour → the code; canon states none of it.
  2. A command can decide it — lint, format, types, imports → a check, run in CI and fed back at edit time by a hook; no CI at that level → the hook alone.
  3. A hard allow or deny of a tool, command or path, session-wide, whose refusal needs no way out → a permission rule.
  4. Must hold or happen on every matching event, whatever the model decides → a command hook · judgment at a fixed event → a prompt or agent hook, its firing guaranteed and its verdict not · needed only once a skill runs → that skill's `hooks:` frontmatter, armed until the session ends; each through /hook-development .
  5. Every turn needs it → `AGENTS.md`, split from `CLAUDE.md` per `references/instruction-files.md` · only work under one directory needs it → that directory's `AGENTS.md`, with a `CLAUDE.md` beside it holding `@AGENTS.md`; never a rule file — `references/rules.md`.
  6. One act needs it → the skill owning that act; what one repo adds to a tool's act → `references/skills.md` § A tool's skill and its config.
  7. Durable reference no single act owns, reached by a pointer → how a tool works → that tool's skill · how one codebase works, beyond what it adds to a tool → that repo's `docs/agents/`.
- Beside the ladder: a value → config · what no dispatch parameter reaches → an agent file, per `references/agents.md` · text every session needs → `AGENTS.md`, never a SessionStart hook printing it · text that changes per run → a SessionStart hook.
- Its owner already states it → nowhere; name the owner.
- Directive ignored → check in order, before adding a word: loaded — for a past session, its `~/.claude/state/read-log/<session>` `instructions:` lines and its transcript's `nested_memory` attachments; for the session in hand, the user's `/context` · contradicted by another loaded file or a Claude Code built-in · lost in a long file · owed every time → rung 4.

## Config levels

- Three levels load together: user (`~/.claude/`) — true in any codebase · project shared (`<repo>/`, committed) — true of one codebase for every session that loads it · project local (`<repo>/`, never committed) — true only for the user in that repo.
- Decide each fact's level as it is written, not once per file.
- A user-level fact naming a stack, framework, repo, ticket prefix, port, env var, integration or domain concept → project level · a language's idiom true in every codebase writing it → `AGENTS.md` § Code Style.
- A fact about the user rather than the codebase — their paths, ports, accounts, tools → local, whatever the repo does.
- A project fact a teammate, a cloud session or CI must load → shared; in a repo only the user can pull (private, the user its only collaborator) → shared too.
- A local copy sits at the shared one's path, excluded from git — except settings (`settings.local.json`), instructions (`CLAUDE.local.md`) and MCP servers (`claude mcp add --scope local`).
- Before writing into a repo's `.claude/` or `docs/agents/` → `git check-ignore -v <path>`: ignored → local; not ignored → shared on the next `git add`; exit 128 → neither, the path runs through a symlink or leaves the repo.
- Collisions: settings merge key by key, local over shared over user; instructions and rules concatenate and none overrides another — two levels conflicting → make them agree or delete one; a same-named agent or MCP server is replaced whole; a user skill beats a same-named project skill, which then never runs.

## Where canon lives

- `~/Code/skills` (`yann-lauwers/skills`) is the one home of every own skill, agent and hook; a host installs them from GitHub with the commands in its `README.md`, never by link.
- Change one → edit it in `~/Code/skills`, commit, push, then refresh: a skill → `npx skills update -g -y`, and `npx skills update -p -y` in each repo using it · an agent or hook → `claude plugin marketplace update yannlauwers`.
- An installed copy (`~/.claude/skills/<name>`, the plugin cache) is never edited: the next update overwrites it.
- `~/.agents/AGENTS.md`, `~/.claude/settings.json` and `~/.config/` are this host's own files, backed up by the T7 only; edit them in place.

## Read this first, then act

| Acting on | Read |
| --- | --- |
| a rule file, or a fact headed for one | `references/rules.md` |
| a skill, a tool's skill and its config, a skill switched on per repo | `references/skills.md` |
| an agent file | `references/agents.md` |
| a prompt another model runs — an Agent brief, a stored prompt, a dispatch template | `references/prompts.md` |
| a `CLAUDE.md`, an `AGENTS.md`, their `.local` twins | `references/instruction-files.md` |
| rewriting a whole existing file — "optimize this", "improve X everywhere" | `cookbook/optimize.md` |
| placing a fact, delivering it to another repo, a second home, a one-home breach the user flags | `references/composability.md` |
| a hook, its wiring, its registry row | /hook-development |
| installing or updating a pack authored elsewhere, or which packs an optimize sweep leaves alone | `references/vendored.md` |

- A new file of any kind → read the nearest sibling of its kind and shape first, and match its sections and depth; § How we write and the kind's reference win where the sibling departs from them.

## The claim search

- Finds every file still naming what a change removed, renamed or reworded, or already stating what it adds: grep each name, and each changed claim's distinctive words with their inflections and the synonyms the canon uses for them, over `~/.claude/{agents,hooks,agent-memory}`, every real directory under `~/.claude/skills` but `synced`, `~/.claude/settings.json`, `~/.claude/*.md`, `~/.claude/projects/*/memory`, `~/.agents/{skills,docs,AGENTS.md,bin}`, the scripts under `~/.local/bin` and `~/.local/share/*` (never their data or state files, a staged original or a sandbox copy), and each `~/Code` base checkout's `CLAUDE.md`, `AGENTS.md`, their `.local` twins, `.claude/` and `docs/agents/`.
- Never all of `~/.claude` or `~/.agents`: state, history and transcripts flood the search and are never edited.
- A worktree's copy → reported, never edited.

## Changing what's written

- A directive changed, reversed or removed → change it at its home; a reversed one's new line takes the old line's place.
- A file removed → delete it: its history stays in its repo's git; a file in no repo → copy it to `~/.agents/archive/` first.
- Then § The claim search on every name and claim the change touched, in the same change.
