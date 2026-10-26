---
name: cli-patterns
description: "Shapes a command-line tool so a person or an LLM can navigate it from `--help` alone — command tree, flags, help pages, examples, machine output, exit codes, versioning, README — and audits one against the published guidelines. Use on 'add a command', 'add a `--json` flag', 'write the help text', 'make it LLM-friendly', 'audit the CLI', 'is this a breaking change'. Also fires on editing an `argparse`, `click`, `typer`, `commander`, `cobra` or `clap` parser. Not for a library's interface — /codebase-design ; not for an MCP tool's schema — /mcp-development ."
---

# CLI Patterns

- The bar — clig.dev's *Command Line Interface Guidelines*, GNU's `--help`/`--version` convention beneath it; this skill adds what an LLM reader needs on top.
- `--help` is the one surface every reader hits first: a page with no description describes nothing, whatever the README says.
- A verb wearing a flag is a subcommand that was not cut; the `, and exit` in its help string is the tell.

## Routing table

| Intent | Read |
| --- | --- |
| IF auditing a CLI that exists — "is it described correctly", "make it LLM-friendly" | THEN `cookbook/audit.md` |
| IF adding a command, cutting a flag into a subcommand, or naming either | THEN `references/commands-and-flags.md` |
| IF writing or reviewing a `--help` page, an example block, or the README's command table | THEN `references/help-surface.md` |
| IF writing, reviewing or restructuring the README as a whole — what it opens on, its sections, their order | THEN `references/readme.md` |
| IF deciding what a command prints, adding `--json` or `--plain`, or choosing an exit code | THEN `references/output-and-exit.md` |
| IF deciding which part of a release's version moves, or whether a change is breaking | THEN `references/versioning.md` |
| IF the reader is an agent — completeness, dry runs, reads that write nothing, error messages that name the fix | THEN `references/agent-navigable.md` |
| IF the parser is `argparse`, `click`/`typer`, `commander`, `cobra` or `clap` and a framework trap is in play, or the tool is a bash `case` dispatcher | THEN `references/frameworks.md` |
| IF the request matches none of the above | THEN `references/help-surface.md`, say which row was closest |

## Done when

Every command's own `--help` opens on a sentence saying what it does, every flag has a help string with its default, the top-level page carries two to four examples and a support link, each page states its exit codes, structured output has `--json`, and a test in the repo refuses the next command or flag that ships bare.
