# Keys a role requires

- A role several tools can fill → its consumers read the keys below whichever tool fills it; every floor declaring the role carries each with its own answer.
- A tool wired into one of these roles → its floor gets them in the same change.

## `role: tracker`

| Key | What it answers |
| --- | --- |
| `settled_categories` | the tracker's own fixed categories a ticket ends in, as its API names them, compared case-insensitively; every frontier, blocker check and "what is left" count treats a ticket there as closed, and a state added later falls in its category the moment it exists · no session transitions such a ticket on its own initiative; a transition the user names is carried out |
| `settled_states` | states this repo settles outside those categories, by name — a Linear state, or a GitHub label a repo treats as final while the issue stays open |
| `automated_states` | states only an automation moves a ticket into; a session reports one and never sets it |
| `label_creation` | `ask` or `free` — whether a marker label a pass needs is created without asking |
| `maintainer` | `'@<handle>'`, the tracker handle of the person who confirms a split and owes a size question; null where the repo declares nobody, and the ticket's reporter owes it |
| `architecture_owner` | `'@<handle>'`, the tracker handle of the person who owes a design question — the choice between an architect's options; null where the repo declares nobody, and the ticket's reporter owes it |

## `role: terminal`

| Key | What it answers |
| --- | --- |
| `seat_folders` | `per-repository` or `per-effort` — which folder a repo's seats join; the seating flow owns the method |

## `role: design`

| Key | What it answers |
| --- | --- |
| `medium` | where a repo publishes its validated design system, or null; the repo's design skill owns the method |
| `project` | the hosted project the validated system is published to, by name |
| `mirror` | the directory, relative to the repo root, whose tree the hosted project mirrors — what a push exports from a commit, and what a card has to sit under to reach the pane; null where `medium` is null |
| `design_owner` | `professional` or `private` — which of the floor's `accounts` holds this repo's design projects; a side of the owner's life, never an entity or a secret item's prefix |
| `accounts` | floor only: the Claude account holding each owner kind's design projects |
| `renders` | the globs, relative to the repo root, of every file whose change moves a pixel the owner would see, or null; the build's pick check owns the method |
