# Skills

## The tree

- `SKILL.md` → what every use needs, then the routing table, both inside the first 5,000 tokens a compaction re-attaches (`wc -c` ÷ 3.6) · `cookbook/*.md` one file per procedure · `references/*.md` tables, traps, conventions · `scripts/*` a deterministic sequence, executed, never paraphrased.
- The routing table names every file, each one level deep from `SKILL.md`.
- A skill carries no tests: no `tests/` directory and no test files.
- Format — the shape of one artifact a skill or agent writes: a report, a ticket, a PR body; the only place its length and shape are decided, reply rules deferring to it; it states its reader, none stated → a person.
- A format lives with its writer: one agent writing it on every dispatch → that agent's body · one skill → its `references/<artifact>.md` · several writers → the skill owning the act, every other writer naming it.
- A script lives with the act it performs: one skill running it → that skill's `scripts/` · several skills → the skill owning the act, every other caller citing it per § Citing a sibling and running it by `~/.claude/skills/<owner>/scripts/<name>` · an engine outside the skills among its callers → that engine's directory · a command people or launchd type → on `PATH`; never a canon folder of shared scripts.

## The body

- A line that holds for the whole task → worded as standing — a norm, or an order naming the act it recurs on — never a one-time order.
- A procedure's numbered steps each run once, in order; a line every step obeys stands above them, never as one of them.

## The description

- The description keeps its own form — third person, opening on the act that fires it ("Files one new ticket…") — never § How we write's line forms.
- It is the only text matched against the session → every "when to use" goes in it, never in the body.
- Trigger → the act about to be taken, the domain word only as a marker beside it: "Use when adding or changing a migration", not "when working with databases".
- A request that never names the domain → name what the act touches: file types, filenames, symbols, commands, the phrases the user says; the act with no request → "Also fires on the ACT — …".
- A sibling shares its keywords → "not for … — /owner ;", naming the true owner after reading its description; never excluding what this skill's own trigger or body owns.
- An ACT item a sibling's routine command also matches — a shared recorder, a sibling's spine, a read-only status call → leave it out.
- Fires too often → narrow it before adding exclusions · fires rightly, runs badly → fix the body.
- Every clause is a trigger, a marker or a boundary; never workflow steps, a summary of the body, or a vague job.
- `when_to_use` → trigger phrases and example requests, appended to `description`; past 1,536 characters together the listing cuts the tail.
- A skill with `disable-model-invocation: true` gets no ACT clause; its description says who starts it.
- A slash-name stands with whitespace both sides, never touching punctuation: "— /name ;".

## One subject per skill

- A tool skill explains one tool — commands, config, failure modes — true whoever calls it · a flow skill runs a process, composing tools and flows.
- A flow skill names every tool it composes; a tool skill names none of its callers, nor a sibling tool skill.
- A tool skill carries no other tool's commands, flags or mechanics; a step another tool performs names that tool's role, and its skill owns the how.
- A description joining two subjects with "and" → two skills.
- Two triggers, one procedure → one home, the other skill running it.
- A sentence that stops holding once the sibling it describes is rewritten → the sibling's; cite it.

## A tool's skill and its config

- Every wired tool → a skill saying how to operate it, and a config: `~/.claude/skills/agents-config/integrations/<tool>.md` (floor) and `<repo>/docs/agents/integrations/<tool>.md` (project). The token lives in the secrets vault as item `<entity>-<tool>`.
- The config → role, `status`, secret item, the keys `roles.md` defines, and values that change with the account, entity, repo or environment · never a key no reader resolves.
- A project file → ignored before it is written, per `SKILL.md` § Config levels, probed from the base checkout where the path runs through a link (exit 128); written on the tool's first use in the repo, whether or not anything differs, with a per-repo plugin's `true` in the same act, per § Where a skill lives; its `defaults` name only the keys where the repo differs from the floor — for a key the floor derives, from what the derivation returns — or one its owner pins against a floor change under `## Pinned`, one bullet per key · `defaults: {}` where nothing differs.
- The config body → one line naming who reads it — the tool's skill and any consumer reaching it by role; a project file over a floor → `Read as the floor names.`, plus any reader only that repo has · then only what a key cannot carry about this account, entity, repo or environment that the tool's skill or a consumer reads · never a reason, a date or the evidence that settled a value.
- What one repo adds to a tool → its values and the body line above, in the project config, reached by role · any other directive in the repo's `AGENTS.md` · a flow only that repo runs in a project skill · never a `docs/agents/` file outside `integrations/` and the files /setup-matt-pocock-skills and /worktrunk write.
- A value the tool itself defines — its CLI's install path, an env var it exports, a fixed API base → the skill.
- The skill → the tool's traps and how we work with it · never an API reference the vendor documents, or a checklist repeating its steps' done states.
- The call kernel — one authenticated call → the skill, once, reading its credential from the variable a `Needs: <NAME>` line names, with the header, prefix and hosts it travels to; the command sends no credential when the variable is unset; the host's provider fills it from the config's `secret`, or from the resolved entity or location where the config declares `resolves:` · a tool with no kernel → its auth mechanism and header in the skill.
- The skill carries a `## Project config` section naming its config path and what it does with none.
- A config holding a command surface, an operations table or a list of traps → the tool has no skill yet: write one, however thin.
- A call or two, no procedure → a single-file skill · a rich recurring flow → a cookbook per intent · unsure → the lean shape, said aloud.
- Config keys, `status` meanings and merge rules → `~/.claude/skills/agents-config/SKILL.md`.
- A new `role` value → reuse an existing capability word; a new word is the user's to confirm.
- Never write to the secrets vault: hand the user the item spec the `role: secrets` skill describes, and continue once it exists.
- A new tool's nearest sibling → the wired tool of its shape — rich flow · thin · project-less personal — its skill and its config both.
- Name the role, never the tool; only a tool's own config and skill name its vendor or CLI, a repo's line naming the service that fills a role and a path example the user wrote aside. A skill never names the provider filling its `Needs:` variable; each host declares that once, in its own user instructions.
- A repo's tracked line sending a reader into its project tool configs — the integrations folder under its `docs/agents/` — by path, file name or section → the pointer gives way to the service filling the role, in a few words (`<role> → <service>.`), and the rest of the line stays; a value it needs is named by role and key, left to resolution; a line that was only the path goes.
- Place a fact by altitude: method, true whichever vendor fills the role → the `AGENTS.md` section or skill owning the act · a tool's own mechanics versus its account values → the lines above.
- Inside a repo with no project layer for a tool → write it in the turn that found the gap, per the lines above.
- Record a call shape only after running that exact text end to end, with a provenance line; a recorded call that fails is diagnosed before it is edited.
- Done when resolution finds the config by role and the call authenticates through the host's provider, both exercised.

## Where a skill lives

- Every own skill's home is `~/Code/skills/skills/<name>/`, installed from `yann-lauwers/skills`: with `-g` into `~/.claude/skills/<name>` → every session here · without it, in a repo → `<repo>/.claude/skills/<name>`, committed in Yann's own repos and in `.git/info/exclude` in team repos → that repo · a skill only one repo will ever run → written straight into `<repo>/.claude/skills/<name>/`, tracked or git-excluded, never in the library.
- A skill that is no tool's → one consuming repo → project level; a second → user level.
- A new user skill takes no name any `.claude/skills/` under `~/Code` holds; a new project skill takes none the user level holds. The listing shows only the current repo's project skills → check on disk; an existing collision goes to the user.
- A tool's or a stack's skill → user level when every repo uses it, per repo when only some do; it names no repo's paths, scripts or skills.
- Per repo → a service a repo's own stack or tracker uses, or a stack only some repos hold · everywhere → a tool of this machine or of every repo, or one a caller reaches where no config exists.
- Installed in a repo → `npx skills add yann-lauwers/skills -a claude-code -y -s <name>` in it, and that repo's row in `~/Code/skills/README.md` in the same change.
- `Unknown skill: <name>` for a per-repo skill, in a repo whose stack or tracker uses it → read `~/Code/skills/skills/<name>/SKILL.md` by path, write its project config per § A tool's skill and its config where none exists, and install it there; the skill loads in the next session.
- Done → a fresh session's `system/init` event (`claude -p hi --output-format stream-json --verbose`) lists the skill in each repo holding it and nowhere else.

## Who may invoke it

- `disable-model-invocation: true` only where invocation is the user's call: an interview only the user answers · an estate sweep whose cost the user chooses · an irreversible outward act · a pass seated on its own.
- Writing something is no reason on its own → bound the run by constraints it can be audited against.

## The listing budget

- `skillListingBudgetFraction` in `~/.claude/settings.json` caps the listing; past it, descriptions drop, least-invoked first.
- `skillOverrides` → `"name-only"` · `"user-invocable-only"` · `"off"`.

## Citing a sibling

- By name alone: `/<skill> `, the case named in plain words; never a file or a `§` inside another skill. The case it names → a row of that skill's routing table, added in the same edit where missing.
- Not a sibling, so not this rule: a script run by its path, per § The tree · a doc addressed by its path, where the lines below allow one.
- A deferral needs the target reachable and its description firing on the act → the act inside its subject: widen that description in the same edit · outside it: repoint.
- A user or git-excluded project skill keeps no fact `~/.agents/AGENTS.md` states, in any wording — except a skill whose subject is canon itself, which states in full the facts of its own subject; `AGENTS.md` names those by the trigger that loads it, plus at most one principle line every session needs.
- A tracked project skill names no user-level skill and states a user-level fact in its own words; a user skill may name a project one; a git-excluded project skill may name a user skill.
- A skill names no rule, no `AGENTS.md` section and no doc, stating in its own words a fact the lines above don't drop — except its tool's config path in a user or git-excluded skill, /voice for a skill drafting a message in Yann's voice (loaded before drafting, and says what it does when it is unavailable), and a skill whose subject is canon itself.

## Frontmatter

- `name:` → the skill's directory name; tools following the Agent Skills spec skip a skill without it.
- `paths:` beside `disable-model-invocation: true` is dead config → keep one.
