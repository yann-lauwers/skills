# Skills

## The tree

- `SKILL.md` → what every use needs, then the routing table, both inside the first 5,000 tokens a compaction re-attaches (`wc -c` ÷ 3.6) · `cookbook/*.md` one file per procedure.
- The routing table names every file.
- A skill carries no tests: no `tests/` directory and no test files.
- Format — the shape of one artifact a skill or agent writes: a report, a ticket, a PR body; the only place its length and shape are decided, reply rules deferring to it; it states its reader, none stated → a person.
- A format lives with its writer: one agent writing it on every dispatch → that agent's body · one skill → its `references/<artifact>.md` · several writers → the skill owning the act, every other writer naming it.
- A script lives with the act it performs: one skill running it → that skill's `scripts/` · several skills → the skill owning the act, every other caller citing it per § Citing a sibling and running it by `~/.claude/skills/<owner>/scripts/<name>` · an engine outside the skills among its callers → that engine's directory · a command people or launchd type → on `PATH`; never a canon folder of shared scripts.

## The body

- A line that holds for the whole task → worded as standing — a norm, or an order naming the act it recurs on — never a one-time order.

## The description

- A request that never names the domain → name what the act touches: file types, filenames, symbols, commands, the phrases the user says; the act with no request → "Also fires on the ACT — …".
- A sibling shares its keywords → "not for … — /owner ;", naming the true owner after reading its description; never excluding what this skill's own trigger or body owns.
- An ACT item a sibling's routine command also matches — a shared recorder, a sibling's spine, a read-only status call → leave it out.
- `when_to_use` → trigger phrases and example requests, appended to `description`; past 1,536 characters together the listing cuts the tail.
- A skill with `disable-model-invocation: true` gets no ACT clause; its description says who starts it.
- A slash-name stands with whitespace both sides, never touching punctuation: "— /name ;".
- A description joining two subjects with "and" → two skills.

## A tool's skill and its config

- Every wired tool → a skill saying how to operate it. The token lives in the secrets vault as item `<entity>-<tool>`.
- The call kernel — one authenticated call → the skill, once, reading its credential from the variable a `Needs: <NAME>` line names, with the header, prefix and hosts it travels to; the command sends no credential, and exits naming the variable, when it is unset · a tool with no kernel → its auth mechanism and header in the skill.
- What one repo adds to a tool → a `## <Tool>` section in that repo's `AGENTS.md`: the provider command filling the `Needs:` variable, whose account it opens, and where that account's own choices are kept · a flow only that repo runs → a project skill · never a file under `docs/agents/` · a tool no repo uses → that section in the host's `~/.agents/AGENTS.md`.
- An account's own choices — its numbering, its terms, what it re-invoices → the record the repo already keeps for that account; the skill names each choice it reads and asks the user for one the repo states nowhere.
- Only the tool's own skill and the repo's section for it name its vendor or CLI; a skill never names the provider filling its `Needs:` variable.
- A value the tool itself defines — its CLI's install path, an env var it exports, a fixed API base → the skill.
- The skill → the tool's traps and how we work with it · never an API reference the vendor documents, or a checklist repeating its steps' done states.
- A call or two, no procedure → a single-file skill · a rich recurring flow → a cookbook per intent · unsure → the lean shape, said aloud.
- Never write to the secrets vault: hand the user the item spec /proton describes, and continue once it exists.
- A new tool's nearest sibling → `billit`: its skill, and the `## Billit` section of `~/Code/personal-ops/AGENTS.md`.
- Place a fact by altitude: method, true whichever vendor serves it → the `AGENTS.md` section or skill owning the act · a tool's own mechanics versus its account values → the lines above.
- Inside a repo with no section for a tool it uses → write it in the turn that found the gap.
- Record a call shape only after running that exact text end to end, with a one-line provenance: date, route, result; a recorded call that fails is diagnosed before it is edited.
- Done when the call authenticates through the command the repo's section names, exercised.

## Where a skill lives

- User level (`-g`) → every session here · project level → that repo · a skill only one repo will ever run → written straight into `<repo>/.claude/skills/<name>/`, tracked or git-excluded, never in `~/Code/skills`.
- A skill that is no tool's → one consuming repo → project level; a second → user level.
- A new user skill takes no name any `.claude/skills/` under `~/Code` holds; a new project skill takes none the user level holds. The listing shows only the current repo's project skills → check on disk; an existing collision goes to the user.
- A tool's or a stack's skill → user level when every repo uses it, per repo when only some do; it names no repo's paths, scripts or skills.
- Per repo → a service a repo's own stack or tracker uses, or a stack only some repos hold · everywhere → a tool of this machine or of every repo, or one a caller reaches outside the repos using it.
- Installed in a repo → that repo's row in `~/Code/skills/README.md` in the same change.
- `Unknown skill: <name>` for a per-repo skill, in a repo whose stack or tracker uses it → read `~/Code/skills/skills/<name>/SKILL.md` by path, write what the repo adds to it per § A tool's skill and its config where nothing is written yet, and install it there; the skill loads in the next session.
- Done → a fresh session's `system/init` event (`claude -p hi --output-format stream-json --verbose`) lists the skill in each repo holding it and nowhere else.

## Who may invoke it

- `disable-model-invocation: true` only where invocation is the user's call: an interview only the user answers · an estate sweep whose cost the user chooses · an irreversible outward act · a pass seated on its own.
- `paths:` beside `disable-model-invocation: true` is dead config → keep one.

## Citing a sibling

- By name alone: `/<skill> `, the case named in plain words; never a file or a `§` inside another skill. The case it names → a row of that skill's routing table, added in the same edit where missing.
- Not a sibling, so not this rule: a script run by its path, per § The tree · a doc addressed by its path, where the lines below allow one.
- A deferral needs the target reachable and its description firing on the act → the act inside its subject: widen that description in the same edit · outside it: repoint.
- `AGENTS.md` may name a skill; a skill never names `AGENTS.md`: a user or git-excluded project skill keeps no fact `~/.agents/AGENTS.md` states, in any wording — except a skill whose subject is canon itself, which states in full the facts of its own subject; `AGENTS.md` names those by the trigger that loads it, plus at most one principle line every session needs.
- Dropping the path does not make it legal: "the worktrees section", a bare "§ Judgment Calls", a scope written as `AGENTS.md`'s complement each defer the same way.
- A tracked project skill names no user-level skill and states a user-level fact in its own words; a user skill may name a project one; a git-excluded project skill may name a user skill.
- A skill names no rule, no `AGENTS.md` section and no doc, stating in its own words a fact the lines above don't drop — except a skill whose subject is canon itself.
