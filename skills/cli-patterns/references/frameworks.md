# Framework traps

## argparse (Python)

- `add_parser(name, help=…)` shows in the parent's command list only. The command's own page
  shows `description=`; set both, or the page is a usage line and nothing else.
- `RawDescriptionHelpFormatter` keeps an example block's columns and stops wrapping the
  description too; wrap the prose by hand (`textwrap.fill(text, 78)`) and keep the examples raw.
- `%(default)s` in a help string prints the default; a default set and not shown is invisible.
- `add_subparsers(title="commands", metavar="<command>")` replaces the `{a,b,c}` brace list in
  the usage line with a name.
- A `--version` action on the root answers before the required subcommand check does, so `tool
  --version` works with no command.
- Usage errors exit 2 via `ArgumentParser.error`; a `SystemExit("message")` raised from a command
  exits 1 with the message on stderr — pick one per failure class and say it on the page.

## click / typer (Python)

- A command's docstring is its description and the first line its short help; a command with no
  docstring has a blank page. `show_default=True` per option or `context_settings` for all.
- Nested groups: `@group.command()` under `@click.group()` gives noun-verb for free; a flag that
  branches behaviour is the "verb wearing a flag" of `references/commands-and-flags.md`.

## commander (Node), cobra (Go), clap (Rust)

- commander: `.description()` on each subcommand and `.helpOption()` text; `.addHelpText('after',
  …)` carries examples; an option with no description prints bare.
- cobra: `Short` is the list line, `Long` the page; `Example` is a first-class field, and an empty
  one prints nothing. `SilenceUsage` keeps the usage dump off a runtime error.
- clap: `about` vs `long_about`, `#[arg(help, long_help, default_value_t)]`; `after_help` for
  examples. Derive-mode doc comments fill `about`/`long_about` from the first paragraph and the
  rest.

## bash — a `case` dispatcher

- One page per command: a `show_<cmd>_help` heredoc called from the handler's `-h|--help)` arm,
  and the top-level page a heredoc of its own rather than the handlers' one-liners stitched
  together. What a page carries is `references/help-surface.md`'s.
- `-h` is answered before any side effect, and a page prints on a machine missing every tool the command needs.
- Each handler runs its parse loop before its dependency check or any directory write; its arms only record values, resolving one — a tool call, a path check — after the loop.
- A parent handler dispatches its subcommand before touching anything; `main` runs no dependency check and writes nothing before it hands off.
- An unknown flag is refused with exit 2 and the usage-error message of `references/output-and-exit.md`.
- Every parser's `-*)` arm calls one helper with the words naming its command and the offending flag, so the refusal has one shape a test can match.
- No `*)` arm takes a dash-word as a positional.
- A handler wrapping another command stops parsing at `--` or after its fixed count of positionals, and every later word, `-h` included, is the wrapped command's.
- A bats test derives the surface. The script ends on `[[ "${BASH_SOURCE[0]}" == "$0" ]] && main
  "$@"`, so the test can source it without running it. Commands come from the dispatcher's word
  arms, subcommands from the word arms inside a handler, flags from each parser's dash arms,
  `shift 2` marking one that takes a value; the test then runs `-h`, `--help` and an unknown flag
  against every word found. Read the functions through `declare -f`, which puts every arm header
  on its own `tok1 | tok2)` line and every arm end on a lone `;;`.

Traps the test meets:

- macOS `/bin/bash` is 3.2: no associative arrays.
- The script's `set -euo pipefail` carries into whatever shell sources it, so an empty `grep`
  later in the discovery kills the test. Source it inside its own `bash -c` and dump `declare -f`
  from there, with `|| true` after the `source`, since the guarded `main` line ends on a false
  test when sourced.
- The probe word is an arm's first token, so arms are written canonical first (`create|c)`) and
  each refusal names that word.
- A help probe on the developer's own `PATH` passes a page that calls an optional tool; run it
  under a `PATH` holding only what printing needs, with an empty `HOME`.
- The dispatcher's own global flags sit outside every handler, and a per-command probe never
  reaches them — check them separately or say they are unchecked.

Worked example for the test, never for the dispatcher, whose `main` runs the dependency check and peeks ahead for `-h` to skip it: `tests/test_help_surface.bats` of the retired `wt`,
archived at github.com/yann-lauwers/tmux-worktree-manager, discovery in `tests/help_surface.bash` beside
it; each control plants one defect in a copied tree and asserts the check names it.

## Done when

The page shows a description, a default on every option that has one, and the examples keep their
columns — checked by running `--help`, never by reading the source. For a bash dispatcher, also:
`-h` exits 0 and writes nothing with the tool's dependencies off `PATH` and an empty `HOME`, an
unknown flag exits 2 with the helper's refusal, and a test deriving the surface refuses the next
command or flag that ships bare.
