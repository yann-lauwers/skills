# Optimize a file

Cuts one canon file to the strict minimum it needs to work; "improve X everywhere" runs it file by file. Unsure → cut: a line cut too far comes back, a doubtful line kept never leaves.

## Steps

1. Read the file with line numbers, its `git log`, and its `wc -c`. Done when any line can be cited as file:line.
2. Mine its real runs in `~/.claude/projects/*/*.jsonl`, this session excluded: search for the file's own signature (its commands, tool names, path), pair each tool call with its result, and keep the user request that started each run. Done when every run's request, failures and retries are listed, or the absence of runs is stated.
3. Draft the file's objective in one sentence from those requests, else from its pointer and body; set its pointer (a skill's description, the line linking to the file) and its body against it, and name each divergence. Stop for the user's go on the objective; "improve X everywhere" → every file's objective in one stop. Done when the user has approved it.
4. Probe every claim about a live system or code, read-only first; probe each replacement line too, on scratch data removed afterwards. Done when every claim reads confirmed, false or untestable.
5. Draft outside the live file, holding it to single responsibility for the approved objective; every old line, the pointer included, takes one verdict: `kept` · `merged: <line>` · `moved: <owner>` (it serves another objective, per SKILL.md § Where a fact goes) · `no-op` · `duplicate: <other line>` · `false: <probe>` · `cache: <lookup>`. Done when no line lacks a verdict and every step-2 failure inside the objective has a line preventing it.
6. Write the kept lines per SKILL.md § How we write, collapsing each restatement into a leading word; a line already in form stays byte for byte; check the draft against § Traps.
7. The file serves a safe request → a fresh subagent runs it from the draft.
8. Show the new file whole beside the verdict table, then stop for the user's go; a change after approval is shown again.
9. Install per SKILL.md § Where canon lives, run § The claim search on every dropped or moved name, and report before → after `wc -c`.

## Traps

- A gate's default branch, and a line saying when the rule changes nothing, are directives.
- A general premise moved into one case's step loses the other cases → keep it where every case reads it.
- A set a script or sibling emits — reasons, verdicts, exit codes → read the emitter, keep the set complete.
- A rendered or symlinked file → edit its source and re-render, never the copy.
