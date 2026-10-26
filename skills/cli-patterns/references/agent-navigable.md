# What an LLM reader needs on top

- Every command and every flag describes itself; completeness beats brevity.
- A dry run prints the act it would take.
- An error message names the fix.
- A read command changes no state — no seeded file, no probe starting the thing it measures; the page names every command that writes.

## Done when

An agent handed nothing but `tool --help` and the command pages can name every command, pick
the right flags for a task, predict each exit code, and know which commands write.
