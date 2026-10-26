# The help surface

Sources — clig.dev: "Display help when passed `-h` or `--help` flags. This also applies to subcommands which might have their own help text"; "Users tend to use examples over other forms of documentation, so show them first"; "Display the most common flags and commands at the start of the help text." GNU: "All programs should support two standard options: `--version` and `--help`."

## What each page carries

| Page | Must carry |
| --- | --- |
| top level | one or two sentences on what the tool is for and what it never does; the command list, one line each, common ones first; two to four examples with a trailing comment each; a support or issues link; `--version` |
| a command | a paragraph on the page itself — what it reads, what it writes, what it prints; every flag with a help string and its default; exit codes, where any but 0 is possible; an example where the flags combine |
| a flag | what it changes, in the tool's own words, and the default in the string |

An example block earns its place by the combination a reader would not guess, not the bare command.

## What breaks it

- Only the parent's one-liner set → the command's own page says nothing: most frameworks keep a short help for the parent's list and a separate description for the page; the trap per framework is in `references/frameworks.md`.
- Prose names the effect, never the code it runs.
- A test walks the parser and asserts every command and flag carries a description and the README's command table names every command; a bash dispatcher's version is in `references/frameworks.md`.

## Done when

Every page reads as a complete answer to "what does this do and how do I call it" with no other
file open.
