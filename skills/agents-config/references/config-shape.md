# Config file shape

- A config declares what it is (its `role`) and what it needs (its own secret item), never who provides them; no tool config names another tool.

One file per tool, at either level, same keys:

```yaml
---
tool: <name>
role: <capability>        # open set: tracker · secrets · messaging · vault · cache · db · errors · surveillance · accounting · …
status: default | project-required
secret: <entity>-<tool>   # item NAME in the secrets provider — never a vendor name
                          # <entity> = whoever owns the account: a project (`nexus-linear`),
                          # a business (`probeo-billit`), or a person
resolves: entity | location   # optional: which register a tool serving several subjects resolves its target against
defaults: { … } | {}      # tool params (team, channel, console, key-prefix): real values for every
                          # key that has a cross-project answer, whatever `status` says; {} only when
                          # no key has one
---
# body — per ~/.claude/skills/managing-harness/references/skills.md § A tool's skill and its config
```

## Keys

- `role` — one value, never a list: resolution matches a single scalar line, so a list resolves to nothing; `secrets` is one role among the rest, filled by whichever tool declares it.
- `secret` — the item name the secrets provider holds; only the secrets provider's own skill fetches the value.
- `secret` written through the harness → the name goes on the line below the key, indented: the credential write guard rewrites a one-line key and value to a `${SECRET}` reference before it reaches disk; `agents-config get` reads both forms alike.
- `status` — `default`: a usable default exists, proceed · `project-required`: no default target; outside a project it resolves from an explicit target.
- `project-required` bounds the target, not every key: a floor may still carry a `defaults` key that has a cross-project answer.
- A derived default beats a guessed one: where the environment answers a key (`git`, the forge, the service's own API), the floor's value is the derivation.

## `home` — any tool may carry it

- `home` — optional on every config, whatever its role, read only by a status surface — where a person or a status probe reaches the tool: `url` its page · `health` an address answering 200 while it serves, omitted where the page itself is the check · `label` its name on a status surface, omitted → the tool name.
- A tool nothing local can open — a hosted API, a CLI-only tool → declares no `home`, and a status surface enumerating `home` does not list it.

## `resolves` — several entities or locations

- A tool declaring `resolves: entity` or `resolves: location` → takes its item from the resolved subject — the item its register file names, else `<entity>-<tool>` — never from a config level, whose `secret` stays null.
- The subject → the request's, else the register's own default.
- The secrets provider is the registry: enumerate its items to see every entity.

## How a project file merges

- A project file is a diff against the floor, never a replacement: a key it omits keeps the floor's value, the project winning on any key it names.
- Every overridable value is a `defaults` key; the top-level `secret` and `status` merge by the same rule — a repo scripting an API outside its vendor CLI names its own `secret` over the floor's.
- `tool` and `role` identify the file and never merge: both levels carry the same pair, and a project file omitting `role` drops out of role resolution.
- `status` omitted → the floor's is inherited; write it only to change it.
- Absent ≠ `null`: an omitted key inherits the floor; a key set to `null` says "this tool has none here" and overrides a floor value.
- A project's `role` narrows what that tool fills here, read and never enforced: a repo using the same tool for less names the narrower role in its own file.
