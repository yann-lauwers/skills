# Composability

- Each fact has one home — the artifact whose subject it is; every other place names the role it plays.
- About to write a fact into a file opened for another reason → find its owner first; a consumer names the role.
- Writing a vendor's name into canon and copy-pasting a helper are the same failure; which files may name a vendor → `references/skills.md` § A tool's skill and its config.

This decides where a fact is written, not whether it is worth writing.

## One home

- Before writing a fact down, find the artifact that owns it. Owns it → write it there. Consumes it → name the role and let resolution reach it.

| Altitude                          | The unit   | The test                                                                                 |
| --------------------------------- | ---------- | ---------------------------------------------------------------------------------------- |
| Canon — `AGENTS.md`, skills, docs | a fact     | one artifact names it; every other names the role it plays                               |
| Config                            | a value    | the owning layer declares it; a layer that differs names only its difference             |
| Code                              | a behavior | extract at the second caller; declare a type at its origin so it flows to every use site |
| Domain                            | a concept  | one term, defined once — a synonym is a second definition                                |

- One home is where a fact lives, not how many places it is readable from. A reader who cannot reach the owner — a teammate with no `~/.claude`, a CI runner with no vault → the fact is delivered, generated from its one home. A copy nobody typed is not a second home; a copy somebody edits is.
- Delivering a fact to another repo → the first that fits: derive it from position · leave it per repo, where it only looks shared · a pointer, where the reader reaches the home at read time · the thing itself shared (one executable on `PATH`, one symlinked file) · injected into the reader's context on each run · a rendered copy, only where the reader cannot reach the home at read time and the fact must survive a clone.
- A rendered copy names no source, header or hash; its drift is computed by rendering in memory and comparing with disk; its first render reproduces the text the repo already had, byte for byte.
- Deduplicating answers how many homes, not which home — a command surface is skill material wherever it sits, and a config keeps only its values.
- A fact is individuated by who may change it — N owners who can each change their answer alone hold N facts with one answer today, not one fact with N addresses. Strip the proper nouns: what survives is method, with one home; then ask whether this owner could change its answer alone — yes → its own value, stated there in full.
- A surface carrying the basics while a doc carries the depth is composition; duplication is the same fact authored twice at the same altitude.
- Resolving a second home → the owner states the fact first, then each copy becomes the owner's name or goes.
- One slot — the first line of a reply, its closing line — is one fact: two files each claiming it both read as current and one never fires.
- Writing into a file whose purpose is to hold a project's facts (a `CLAUDE.md`, an index) → test each sentence: could it go stale without anything failing? Yes → the owning artifact keeps it.
- A section already in the file is no precedent: ask the fact's altitude before the file, and read a misplaced neighbour as a second breach, never as evidence.

## AGENTS.md may name a skill; a skill never names AGENTS.md

- `AGENTS.md` is always loaded and stays on this machine; a skill is a directory meant to be handed to someone with none of this setup. `AGENTS.md` names the skill to call when the case arrives; what a skill keeps of an `AGENTS.md` fact → `references/skills.md` § Citing a sibling.
- Dropping the path does not make it legal — "the worktrees section", a bare "§ Judgment Calls", a scope written as `AGENTS.md`'s complement each defer the same way and ship broken.
- Three shapes are not that arrow and stay: `AGENTS.md` as the skill's operand, where the skill's subject is canon itself; a canon file named in `allowed-tools:`; a pointer quoted inside an example as a past breach.

## Breaches

- The user flags a breach of this file → fix it at its source that turn; a tell no line here covers → add it to § One home as one line, in the same turn.
