# Prisma — project config setup

Writes the repo's `docs/agents/integrations/prisma.md` when it is absent.

## Steps

1. Discover what the repo already answers — never fabricate a value:
   - `package_dir`: the directory holding the schema file outside `node_modules`; several schemas → one body line naming each the key does not cover;
   - `runner`: derived from the lockfile unless the repo runs the CLI another way;
   - `scripts`: each `package.json` script in `package_dir` whose command runs `prisma generate`, `migrate diff`, `migrate deploy`, `db push` or `prisma format`, or wraps a script that does — the script name, never its command;
   - `workflow_doc`: a README or doc beside the schema that says when to push and when to migrate;
   - a datasource URL a store holds rather than an env file → one body line naming that store by role.
   Done when each key has a value or is named as open.
2. Write the file from the template, shaped per /managing-harness , `references/skills.md` § A tool's skill and its config. Done when `~/.claude/skills/agents-config/scripts/agents-config get prisma --root "$CLAUDE_PROJECT_DIR"` prints it.
3. Print the path and every key left open, then continue the task.

## Template

```markdown
---
tool: prisma
role: orm
defaults:
  package_dir: <dir>
  scripts:
    <act>: <script>
  workflow_doc: <path>
---
# prisma — <project> (orm)

<reader line — /managing-harness , references/skills.md § A tool's skill and its config>
```
