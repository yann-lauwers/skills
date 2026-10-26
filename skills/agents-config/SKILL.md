---
name: agents-config
description: "Resolves a tool's config and which tool fills a role (tracker, vault, secrets…) through `agents-config get|role|resolve|list`, and owns the config shape every tool's config follows. Use before calling any wired tool, on 'which tracker', 'which vault', a `docs/agents/integrations/<tool>.md` read or written, or an `agents-config` call failing. Not for writing a tool's skill — /managing-harness ."
---

# Integration Config — Shape & Resolution

- Owns which keys a tool's config may carry, what each answers, and how any assistant resolves one; every assistant reads it — `~/.agents/AGENTS.md` § Integrations carries only the reflexes.
- Authoring a tool's config → `~/.claude/skills/managing-harness/references/skills.md` § A tool's skill and its config; the config conforms to this file.

## The decoupling law

- A config declares what it is (its `role`) and what it needs (its own secret item), never who provides them; no tool config names another tool.
- A capability a tool needs → named by role, never by the tool filling it, its vault or its CLI.
- A tool's skill may use `keyless run` — the injector's command, the one tool every consumer reaches a value through, whose own config names the provider; a change of provider edits that config and no consumer.
- Rebinding a capability is a one-line change at the composition level; no tool file moves.

## Config file shape

One file per tool, at either level, same keys:

```yaml
---
tool: <name>
role: <capability>        # open set: tracker · secrets · messaging · vault · vcs · cache · db · errors · surveillance · accounting · …
status: default | project-required
secret: <entity>-<tool>   # item NAME in the secrets provider — never a vendor name
                          # <entity> = whoever owns the account: a project (`nexus-linear`),
                          # a business (`probeo-billit`), or a person
resolves: entity | location   # optional: which register a tool serving several subjects resolves its target against
defaults: { … } | {}      # tool params (team, channel, console, key-prefix): real values for every
                          # key that has a cross-project answer, whatever `status` says; {} only when
                          # no key has one — see `status` below
---
# body — per ~/.claude/skills/managing-harness/references/skills.md § A tool's skill and its config
```

- `role` — what this tool is; the set is open, grows as tools land, and `secrets` is one role among them, filled by whichever tool declares it.
- `secret` — the item name the secrets provider holds; only the secrets provider's own skill fetches the value.
- `secret` written through the harness → the name goes on the line below the key, indented: the credential write guard rewrites a one-line key and value to a `${SECRET}` reference before it reaches disk; `agents-config get` reads both forms alike.
- `status` — `default`: a usable default exists, proceed · `project-required`: no default target; outside a project it resolves from an explicit target, and any key neither level carries is asked for by name.
- `project-required` bounds the target, not every key: a floor may still carry a `defaults` key that has a cross-project answer.

## A key any tool may carry — `home`

- `home` — optional on every config, whatever its role, read only by a status surface — where a person or a status probe reaches the tool: `url` its page · `health` an address answering 200 while it serves, omitted where the page itself is the check · `label` its name on a status surface, omitted → the tool name.
- A tool nothing local can open — a hosted API, a CLI-only tool → declares no `home`, and a status surface enumerating `home` does not list it.

## Keys a role requires

- A role several tools can fill → its consumers read the keys below whichever tool fills it; every floor declaring the role carries each with its own answer.
- A tool wired into one of these roles → its floor gets them in the same change.

### `role: tracker`

| Key | What it answers |
| --- | --- |
| `settled_categories` | the tracker's own fixed categories a ticket ends in, as its API names them, compared case-insensitively; every frontier, blocker check and "what is left" count treats a ticket there as closed, and a state added later falls in its category the moment it exists · no session transitions such a ticket on its own initiative; a transition the user names is carried out |
| `settled_states` | states this repo settles outside those categories, by name — a Linear state, or a GitHub label a repo treats as final while the issue stays open |
| `automated_states` | states only an automation moves a ticket into; a session reports one and never sets it |
| `label_creation` | `ask` or `free` — whether a marker label a pass needs is created without asking |
| `maintainer` | `'@<handle>'`, the tracker handle of the person who confirms a split and owes a size question; null where the repo declares nobody, and the ticket's reporter owes it |
| `architecture_owner` | `'@<handle>'`, the tracker handle of the person who owes a design question — the choice between an architect's options; null where the repo declares nobody, and the ticket's reporter owes it |

### `role: terminal`

| Key | What it answers |
| --- | --- |
| `seat_folders` | `per-repository` or `per-effort` — which folder a repo's seats join; the seating flow owns the method |

### `role: design`

| Key | What it answers |
| --- | --- |
| `medium` | where a repo publishes its validated design system, or null; the repo's design skill owns the method |
| `project` | the hosted project the validated system is published to, by name |
| `mirror` | the directory, relative to the repo root, whose tree the hosted project mirrors — what a push exports from a commit, and what a card has to sit under to reach the pane; null where `medium` is null |
| `design_owner` | `professional` or `private` — which of the floor's `accounts` holds this repo's design projects; a side of the owner's life, never an entity or a secret item's prefix |
| `accounts` | floor only: the Claude account holding each owner kind's design projects |
| `renders` | the globs, relative to the repo root, of every file whose change moves a pixel the owner would see, or null; the build's pick check owns the method |

## Two levels — the floor holds the defaults, the project overrides keys

- User level — the floor: `~/.claude/skills/agents-config/integrations/<tool>.md`, a value for every key wanted everywhere; a project-less tool's only config.
- "Floor" names what a user-level config is in a merge — the value governing where nothing above it says otherwise — never a third level.
- Project level: `<repo>/docs/agents/integrations/<tool>.md`, at the git root of cwd; what it holds and when it is written → `~/.claude/skills/managing-harness/references/skills.md` § A tool's skill and its config.
- A project config git tracks, the file or a link on its path, or an untracked one whose bytes a reachable commit held at that path → `agents-config` refuses it with exit 4 on every verb; only an untracked one no commit held merges, and `--floor-only` reads the floor alone.
- Exit 4 is no missing config → report the refusal and stop, never falling back to `--floor-only`; Yann reviews the file and decides, and an agent never untracks, deletes or rewrites it to pass.

## Merging the two levels

- A tool's effective config → the floor merged with the project key by key, the project winning on any key it names.
- A project file is a diff against the floor, never a replacement: a key it omits keeps the floor's value.
- Frontmatter is the merge surface; a consumer never reads a value out of body prose.
- Every overridable value is a `defaults` key; the top-level `secret` and `status` merge by the same rule — a repo scripting an API outside its vendor CLI names its own `secret` over the floor's — the forge's API item is the `vcs` config's `secret`, never the tracker config's.
- `tool` and `role` identify the file and never merge: both levels carry the same pair, and a project file omitting `role` drops out of role resolution, which globs frontmatter for it.
- `status` omitted → the floor's is inherited; write it only to change it.
- Absent ≠ `null`: an omitted key inherits the floor; a key set to `null` says "this tool has none here" and overrides a floor value.
- A project's `role` narrows what that tool fills here, read and never enforced: a repo using the same tool for less names the narrower role in its own file.
- Resolution lists that project match first and still prints every floor config declaring the role; the project match is the answer — § Resolving a tool, rule 2 — and the floor lines are the set it won against, never a second answer.
- `role` is one value, never a list: resolution matches a single scalar line, so a list resolves to nothing.
- A derived default beats a guessed one: where the environment answers a key (`git`, the forge, the service's own API), the floor's value is the derivation.

## Resolving a tool

1. By name ("linear", "the cameras" → a known tool) → `~/.claude/skills/agents-config/scripts/agents-config get <tool> [<key>]` prints the merged value — one key raw, or the whole config as JSON; `--show-origin` names the level that supplied it, as `git config --get --show-origin` does; `--role <X>` in place of the tool resolves the role first.
   - A script reads values through it, never merging the two files itself.
   - `agents-config resolve <tool>` prints each level's path with a presence flag, for a reader that needs the files.
2. By role ("the tracker", "the secrets provider") → glob `<repo>/docs/agents/integrations/*.md` for `role: <X>`, then `~/.claude/skills/agents-config/integrations/*.md`; both print, project first, and the project wins.
   - Resolve the role every time, never recall it: it resolves to a different tool per project, and the binding lives in each config, never a central map.
3. An explicit target in the request ("in immo", "Caroline's account") → wins over every default.

- By capability, across every tool → `~/.claude/skills/agents-config/scripts/agents-config list --key <dotted-key> [--json]` prints one row per tool whose merged config carries that key — `tool`, `role` and the value, or objects carrying the level each value came from; a consumer enumerating tools by a key uses it, so a tool wired later appears with no consumer edit.
- A key nothing declares → an empty answer, never an error.
- A dependency resolves the same way: a tool needing the secrets provider globs for `role: secrets`.
- Cross-project → root the glob at another repo: `--root ~/Code/<name>`.

## Multi-entity — default is yours

- A tool declaring `resolves: entity` or `resolves: location` → takes its item from the resolved subject — the item its register file names, else `<entity>-<tool>` — never from a config level, whose `secret` stays null.
- The subject → the request's, else the register's own default.
- The secrets provider is the registry: enumerate its items to see every entity.

## No active project

- cwd under no git repo → skip the project glob; resolution is `explicit > user floor`.
- A `project-required` tool resolving to neither → its missing keys are asked for by name.
