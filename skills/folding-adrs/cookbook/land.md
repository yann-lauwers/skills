# Land and brief sibling branches

1. Open the pull request ready for review. Its body names each ADR → its carrier, the step-5 collision list from `cookbook/scope.md`, the docs cut and why, the `.out-of-scope/` verdicts, and what kept an ADR number on purpose (ADR-tooling fixtures, recorded wire data). Done when it is open and assigned.
2. After the owner merges, brief every branch still open against `<base>` → `references/briefs.md` § Sibling branches, filled with the merge commit and this round's renames, read from the diff, never from memory. Done when every running branch's owner has it.
3. Name the ADRs still on `<base>` in the reply as the next round's seed; the owner asks for a ticket → file it. Done when the reply names them.
