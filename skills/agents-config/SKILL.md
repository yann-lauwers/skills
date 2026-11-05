---
name: agents-config
description: "Resolves a tool's config and which tool fills a role (tracker, vault, secrets…), and owns the shape every tool's config follows. Use before calling any wired tool, on 'which tracker', 'which vault', a `docs/agents/integrations/<tool>.md` read or written, or an `agents-config` call failing. Not for writing a tool's skill — /managing-harness ."
---

# Integration Config — Shape & Resolution

- Authoring a tool's config → `~/.claude/skills/managing-harness/references/skills.md` § A tool's skill and its config; the config conforms to this skill.

## Two levels

- Floor — the user-level config, `~/.claude/skills/agents-config/integrations/<tool>.md`: a value for every key wanted everywhere, and a project-less tool's only config.
- Project — `<repo>/docs/agents/integrations/<tool>.md` at the git root, read over the floor key by key.
- Frontmatter is the merge surface; a consumer never reads a value out of body prose.

## Resolving a tool

1. By name → `~/.claude/skills/agents-config/scripts/agents-config get <tool> [<key>]`; `--role <X>` in place of the tool resolves the role first.
   - A script reads values through it, never merging the two files itself.
   - `agents-config resolve <tool>` → each level's path, for a reader that needs the files.
2. By role ("the tracker", "the secrets provider") → `agents-config role <X>`: project lines first, then every floor declaring the role; the project match is the answer, the floor lines the set it won against, never a second answer.
   - Resolve the role every time, never recall it: it resolves to a different tool per project.
3. An explicit target in the request ("in immo", "Caroline's account") → wins over every default.

- Every tool carrying a key → `agents-config list --key <dotted-key> [--json]`; a consumer enumerating tools by a key uses it, so a tool wired later appears with no consumer edit.
- Another repo → `--root ~/Code/<name>`.
- Exit 1 → the key or role is set at neither level: an empty answer, never an error.
- Exit 4 → the project config is tracked by git: report the refusal and stop, never falling back to `--floor-only`; Yann reviews the file and decides, and an agent never untracks, deletes or rewrites it to pass.
- A `project-required` tool with no project config and no explicit target → ask for each missing key by name.

## Read this first

| Acting on | Read |
| --- | --- |
| writing or reviewing a config file — its keys, `home`, `resolves`, how a project file merges | `references/config-shape.md` |
| the keys a role requires — `tracker`, `terminal`, `design` — or wiring a tool into one | `references/roles.md` |
