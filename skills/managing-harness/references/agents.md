# Agent files

- Create an agent file only for what no dispatch parameter reaches: an enforced tool restriction · a `skills:` preload · `memory:` · `omitClaudeMd: true`, where its body, preloaded skills and brief carry everything it acts on. Only pinning a model → no file; pass `model` on the call.
- `tools:` grants names, never path scopes; a scope that must hold is a hook.
- `name` is kebab-case, equal to the filename minus `.md`, unique in its directory; the directory holds agent files at its top level only, beside `bin/` and dot-files, since every `.md` under it parses as an agent.
- Its description says when to dispatch it, what it receives and what it never does, and singles it out among its siblings; detail goes to its prompt.
- An agent the main loop dispatches unasked → `Use proactively` in its description.
- Every agent description loaded together stays under the 15,000 tokens past which the harness warns at startup.
- The built-in Explore and Plan load no CLAUDE.md and no rule; every other subagent loads both unless its file sets `omitClaudeMd: true`.
- No output style and no auto memory reach a subagent; only a fork inherits them.
- What its load leaves out and it acts on → its body or a `skills:` preload; a built-in agent preloads no skill.
- A procedure every run needs → a skill preloaded with `skills:`; that skill never carries `disable-model-invocation: true`, so an agent-only skill takes `user-invocable: false`.
- Body: a one-sentence persona, then only the headings its identity needs; a sequence of steps → a skill's `cookbook/`.
- Every mode name and return-format heading a dispatcher parses stays verbatim.
- `hooks` → this agent's own run only; a guard on what the caller does with the result → settings · `effort` → only when this agent's tier consistently differs from the session's · `permissionMode` → rarely: a widened mode bypasses prompts the user would otherwise see · `color` → where a family of agents shares one.

## The agents layer

- An agent file lives at `~/Code/skills/plugins/agents/agents/<name>.md` and answers to `agents:<name>` → edit, add or delete it there, commit, push, then `claude plugin marketplace update yannlauwers && claude plugin update agents@yannlauwers` (background auto-update takes it otherwise).
- `description:` holds one plain line — never a folded `>` or a quoted string.
- A pack that ships its own agents → its own installer writes them into each project's `.claude/agents/` beside its skill; never copy them into `plugins/agents/agents/`.
- An edited agent → dispatch it from a fresh session; a running one sees the change only after a delay.
