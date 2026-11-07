# Agent files

- Create an agent file only for what no dispatch parameter reaches: an enforced tool restriction · a `skills:` preload · `memory:` · `omitClaudeMd: true`, where its body, preloaded skills and brief carry everything it acts on. Only pinning a model → no file; pass `model` on the call.
- `tools:` grants names, never path scopes; a scope that must hold is a hook.
- The agents directory holds agent files at its top level only, beside `bin/` and dot-files: every `.md` under it parses as an agent.
- Every agent description loaded together stays under the 15,000 tokens past which the harness warns at startup.
- The built-in Explore and Plan load no CLAUDE.md and no rule; every other subagent loads both unless its file sets `omitClaudeMd: true`.
- No output style and no auto memory reach a subagent; only a fork inherits them.
- What its load leaves out and it acts on → its body or a `skills:` preload; a built-in agent preloads no skill.
- A procedure every run needs → a skill preloaded with `skills:`; that skill never carries `disable-model-invocation: true`, so an agent-only skill takes `user-invocable: false`.
- Body: a one-sentence persona, then only the headings its identity needs; a sequence of steps → a skill's `cookbook/`.
- Every mode name and return-format heading a dispatcher parses stays verbatim.
- `hooks` → this agent's own run only; a guard on what the caller does with the result → settings.

## The agents layer

- An agent file lives at `~/Code/skills/plugins/agents/agents/<name>.md` and answers to `agents:<name>`; refresh it per `SKILL.md` § Where canon lives.
- `description:` holds one plain line — never a folded `>` or a quoted string.
- An edited agent → dispatch it from a fresh session; a running one sees the change only after a delay.
