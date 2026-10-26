# Trigger design

- A trigger answers two questions: is this an act or a mention of the act, and what exactly is it acting on — answer both.

## The two-view rule

- Match the act on a stripped view; read the operands from the raw text.
- Stripped view — the command with quoted spans and heredoc bodies blanked, so text about a command stops looking like the command.
- Choose the view per rule, never per module.
- Deletion Test — before normalising input, ask what the normalisation destroys; a rule whose discriminator can live inside the blanked spans reads the raw text plus a positional anchor.
- A check whose advice restates verbatim what the user typed is reading the wrong view.

### There are three views, not two

- A check reads whichever combination leaves its own discriminator standing:

| View | Blanks | Right for |
|---|---|---|
| **heredoc-only** | here-document bodies | a rule whose operand is legitimately quoted — a URL, a path, a message |
| **quote-only** | quoted spans | a rule matching a bare verb that could be discussed inside a string |
| **both** | quoted spans and heredoc bodies | most act-detection |
| **raw** | nothing | operand extraction, after the act has been established |

- After any change to which view a check reads, re-assert its true positive, not only its new silence.

## Command position, not substring

- A tool name appearing in text is not a tool being run: match only where a shell begins reading a command.
- Write the shared primitive once and call it from every trigger:

```python
def command_positions(cmd):
    """Offsets where a shell would begin reading a COMMAND.

    Quoted spans are excluded, so a command name inside a string is never a command
    position. Wrapper words that TAKE a command (sudo, env VAR=x, xargs, nohup, time)
    are absorbed, so the position lands on the real verb.
    """
    if not cmd:
        return set()          # no command text, no command positions — NOT offset 0
    return {m.end() for m in _CMD_SEP_RE.finditer(strip_quoted_spans(cmd))}


def at_command_position(cmd, match):
    """True when `match` (a match on the RAW command) starts where a command starts."""
    return match is not None and match.start() in command_positions(cmd)
```

- Enumerate the positions explicitly; the minimum set: statement separators (`;` `&&` `||` `|` `&` newline), the start of the string, opening a subshell `(` or group `{`, and after every shell keyword that introduces a command — `do`, `then`, `else`, `elif`, `in`.
- A bare `VAR=value` assignment prefix is a command position; absorbing the word `env` does not cover it.
- Assert the idiomatic forms: `PORT=3000 npm run dev` · `( npm run dev )` · `{ npm run dev; }` · `for d in */; do npm run dev; done`.
- Third-Instance Rule — when the same defect class reaches its third instance, stop fixing instances: count how many places independently invented the same helper; more than one → name it once, prove it once, and make every trigger call it.

## Read the subcommand, not just the binary

- Read the subcommand or argument that selects the gated mode, not only the binary, and close the match so a suffixed script name stays out:

```
(npm|pnpm|yarn)\s+(run\s+)?(dev|start)(?![\w:.-])
vite\s+(?:dev|serve|preview)\b
```

- Prefer a signal that is always in the command text over one that can live in a config file.

## Read the right object

### An after-the-fact hook must read the OUTCOME, not the request

- A hook that fires after an action and mutates durable state gates on whether the action succeeded, never on the request text.
- Test the "did it fail?" helper against the literals the system actually emits — its failure envelope and its machine codes, `NOT_FOUND` with an underscore as well as the prose `not found`.

### A content guard must cover every channel the content travels on

- A content guard covers the request as well as the response: a credential typed into a command sits in the transcript as much as one printed by it.
- Cover request and response under one check id sharing one rate-limit key, never as two checks: a second id double-fires whenever a command echoes its own input.

### Validate a format rule against YOUR OWN instances

- Validate a detection rule for a format you own against your own live instances, never only against borrowed examples.
- A format rule missing a segmented variant → widen the character class, never shorten the length bound.

### Scope a classifier to what it can actually classify

- Gate a classifier on the scope its verdicts are specific to, never on the tool alone.
- A literal `<placeholder>` surviving into emitted text is a hard scope error; read every message the live proof emits for an unfilled placeholder.

### A verifier must grade the object that changed

- A verifier derives its target from the payload, never from a hard-coded root.

## The empty parse is "I don't know"

- A guard with three outcomes — allow, block, no opinion — defaults to no opinion on every path where parsing produced nothing.
- `allow` is strictly worse than silence: it suppresses the host's own permission prompt.
- Prove the in-scope side on a non-empty set, and drive the empty case explicitly in the live proof.
- "Fail closed" names a specific conservative behaviour, never "fall back to the previous version".
- A target that cannot be resolved — a variable, a substitution → narrow the fallback's scope to the statement the command appears in, never widen its breadth to every path in the whole command, which produces denies whose stated reason is false.

## Your tokeniser is not the interpreter's tokeniser

- A guard that splits a language it does not itself execute validates the split against the real interpreter's argument vector, never against a plausible one.
- Unsure how a shell splits a string → put a shim executable on `PATH` that records its own `argv` to a side file, and ask it.
- A redirection operator with no space before it is a word boundary to the shell but not to whitespace tokenisation: `/</dev/null`, `/>/dev/null`, `/>>/dev/null`, `~>/dev/null` and `~/>log` each carry a target.
- A digit before the operator belongs to the word — `rm -rf /1>f` keeps `/1` as the argument; assert those rows separately.
- Closing a recognition gap → fix the conservative fallback in the same change: a safety net built from the same tokeniser inherits the same blind spot.

### Grouping characters glue to the word they precede

- `(` and `{` are word boundaries to a shell and not to whitespace tokenisation; strip leading grouping characters where the command word is resolved, never in the branch that noticed.
- Assert the parenthesised form `(cmd)` separately from the braced `{ cmd; }`: the space after the brace lets the braced form pass and hides the bug.
- A boundary fixed on one side → assert the other: a pattern ending `(start|up)([[:space:]]|$)` misses `wt start;` and `wt start && …`.

## Allowlist the closed side

- The programs that can invoke a dangerous command are an unbounded set; the verbs that only read about it are a small closed set — exclude the readers, never allowlist the invokers: excluding the closed side fails toward blocking, allowlisting the unbounded side fails toward allowing.
- A catastrophic-tier guard fails only toward blocking.
- Match broadly, then exclude the readers: `man`, `which`, `grep`, `cat`, `type`, `info`.
- A reader verb inside a command substitution is not reading: `$(which mkfs.ext4) /dev/sdb` formats a disk.

## Multi-signal triggers need RELATED signals

- Scope a conjunction of signals to one statement; co-occurrence in a shell line is not relatedness.
- Anchor name-fragment patterns to whole tokens: `\bKEEP=`, never `\w*KEEP\w*=`.

## Overrides need MORE discipline than triggers

- An override token counts only at a command position, in the same statement as the act — never as a raw substring anywhere in the command.
- The same holds for an exemption; narrowing one spelling → sweep its siblings in the same pass: `-h` and `--help`, and a `--` that passes the runner's flags to the script.

## Tighten only as far as the evidence

- Harden a predicate against the junk observed, never against a wider space imagined while fixing it.
- Name the observation each clause answers; a clause traced to no observed junk is a guess, a false positive waiting for its input.
- A boundary that is ambiguous by shape → record it in the registry row as a known limit, never legislate it away with a threshold.

## Implement the property, not the example

- A carve-out implements the property that justifies it, never the spelling that prompted it.

## Cost is a correctness property

- Never write two adjacent quantifiers over overlapping character sets — `[\w./-]+` followed by a `.` in the class, `[a-z-]+` followed by `[^|]*`: on failure the engine restarts at every offset.
- Prefer a lookbehind that removes the restart loop over a length cap that only bounds the inner rescan.
- Prove any rewrite by differential equivalence, never by reading it: hundreds of thousands of randomised strings over the pattern's own alphabet, comparing `bool(match)` and `group(0)`.
- Never bound the input at the hook boundary as the fix: "skip the guard past N bytes" is a bypass — pad the command with a comment; fix the ambiguous sub-expression instead.
- A cap beside the sub-expression fix is an open question, never settled: defensible only on a check whose miss is harmless, never instead of the fix; a cap on a blocking guard is a bypass whatever sits behind it — adding one → record which side of that line the check is on.
- Static analysis generates candidates; only measurement decides — the harness rules are `robustness.md` § Cost.

## Comments are claims

- A comment listing what a trigger covers is a claim: derive the prose from the pattern, or assert each named item fires.

## The self-reference signal

- A guard firing while someone documents, tests or audits it is a mention-vs-act defect: report it as a first-class defect.
- Drive the self-reference case in the live proof: a runbook heredoc naming the trigger, a commit message quoting it, a grep for it.

## Checklist before shipping a trigger

- [ ] The act is matched on a stripped view; operands are read from raw text
- [ ] The match is anchored to a command position via the shared primitive
- [ ] The subcommand or argument that selects the gated mode is read, not just the binary
- [ ] An empty parse returns *no opinion*, and the live proof drove it
- [ ] Any allowlist sits on the small closed side
- [ ] Multi-signal conjunctions are scoped to one statement
- [ ] Overrides are anchored to a command position in the same statement
- [ ] The pattern has no two adjacent quantifiers over overlapping classes
- [ ] The live proof drove the look-alikes: mention in echo, in a commit message, in a grep, in a heredoc, in a heredoc whose opener carries a redirect, in an inline interpreter string, in a filename
- [ ] The sibling checks were swept for the same shape in this same pass
