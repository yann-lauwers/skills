# The README

README — the web documentation clig.dev § Documentation asks for: the page a person lands on, before anything is installed, to decide whether the tool is for them and to reach a first run.

- `--help` stays the reference that matches the installed version.
- Its sections run in the fixed order below.

Sources: the standard-readme spec (`github.com/RichardLitt/standard-readme`, `spec.md`) for the sections and their order, and clig.dev § Documentation for what the README owes beside `--help`.

## The order

| # | Section | Carries |
| --- | --- | --- |
| 1 | title | the name a person types — the package and the command |
| 2 | short description, no heading | what the tool does and for whom, under 120 characters |
| 3 | background, no heading or `## Why` | the problem in plain words, what the tool builds on, and what it adds to that |
| 4 | `## How it works` | only where the tool makes a decision a user has to trust: the rule in one sentence, a worked example with numbers labelled as an example, and a picture |
| 5 | table of contents | a link to every `##` heading, once the file runs past one screen of sections |
| 6 | `## Requirements` | OS, runtime and version, what must already be installed, and each optional tool with what it adds |
| 7 | `## Install` | a code block that installs from nothing, the one-time setup after it, and how to remove it |
| 8 | `## Usage` | two to four commands a newcomer types, each with a trailing comment, including the combination a reader would not guess |
| 9 | `## Commands` | the command table, which `references/help-surface.md` owns, along with the test that holds it |
| 10 | reference sections | configuration and environment, file locations, output formats, exit codes, versioning |
| 11 | `## Contributing` | where to ask, whether pull requests are accepted, how to run the tests |
| 12 | `## License` | last; an SPDX identifier, or a statement that none is declared |

## What breaks it

- Rationale and measurements come above install → move them into the reference sections, and keep every figure.
- The requirements appear only in install prose → give them their own heading.
- Install is described in prose → write a code block that runs as pasted.
- There is no usage block → write one: the command table shows no command in use.
- The picture is only a mermaid fence → pair it with a plain-text list.
- A constant is quoted in prose → name the symbol it comes from.

## Done when

A reader holding no context can say what the tool is for, whether it runs on their machine, how to install it and which command to run first, from the sections above `## Commands`.
