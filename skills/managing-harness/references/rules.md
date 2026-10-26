# Rules

- No rule file at user level: user-level facts live in `~/.agents/AGENTS.md`, which every assistant reads.
- No new rule file at project level; a fact headed for one → SKILL.md § Where a fact goes, rung 5.
- An existing project rule → stays until its repo's migration moves it into that repo's `AGENTS.md`; a new fact on its subject goes into it meanwhile, so the subject never splits.
- Path scope → a directory's own `AGENTS.md` with a `CLAUDE.md` beside it holding `@AGENTS.md` · a glob over source code → true in every repo: `~/.agents/AGENTS.md` § Code Style · true of one repo: that repo's or that directory's `AGENTS.md` · any other glob → the skill owning the act.
