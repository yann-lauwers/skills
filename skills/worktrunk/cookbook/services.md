# Services — Is It Running, At Which URL, Why Isn't It Answering

Establishes a tree's live dev-server state before acting on it. The steps run in order, each answer deciding whether the next runs; which unit is at fault is judgment.

- A dev server answers at a stable portless name, `https://<id>.<app>.localhost`, `<id>` derived from the tree's directory name, its port negotiated at each start and never read or pinned by hand — except a tree on the `ports` edge.
- The edge: `portless` (macOS default) · `ports` (Linux default) → a slot, served at `http://localhost:<port>`.
- A repo runs a managed dev server only where its project entry declares a `dev` alias (`~/.config/worktrunk/config.toml`): a single-server repo through `wtk-web`, a repo with a project folder through its own command.
- A repo with a project folder → its `AGENTS.md` names its URLs, units, start timeout and remote host; read it before Step 2.

## Step 1: Status first

```bash
~/.config/worktrunk/bin/wtk-step fence <tree>
git wt -C <tree> dev status
```

- One line per unit: `up` · `stopping` · `down (wanted up)` · `down`; `no units recorded` → nothing was ever started in this tree.
- Status reads the units' records and probes nothing → a unit reading `up` whose URL fails still goes to Step 2.
- `fence` exits non-zero on the main checkout → no managed dev server runs there.
- `fence` exits 1 → `cookbook/troubleshoot.md` § No ownership token, and no `dev` command here until it exits 0; no `~/.config/worktrunk/` on this host → no managed dev server runs: stop.

**Done when:** each unit's state is in hand.

## Step 2: Read the URL and the log

- The `url:` line `dev up` printed, `https://<id>.<app>.localhost` with `<app>` the second argument of `wtk-web` in its alias, or `http://localhost:<port>` on the `ports` edge.
- Probe the URL as printed: `curl -sS -o /dev/null -w '%{http_code}\n' <url>`; a Node client outside portless needs `NODE_USE_SYSTEM_CA=1`.
- Why a unit fails → `git wt -C <tree> dev logs [unit] [-f]`; `wtk-web`'s unit is `web`.

**Done when:** the URL answers, or its failure has a log line naming why.

## Step 3: Start what is missing

```bash
git wt -C <tree> dev up
```

- Starts each unit detached in its own process group and blocks until every health probe answers, then prints the URLs: `wtk-web` waits up to 120 s (`WT_DEV_TIMEOUT` overrides) → give the Bash call a timeout past that, or run it in the background and wait on its notification.
- A killed caller leaves the units running; `dev down` is the stop.
- Exit codes: `0` up · `1` failed, log path printed · `2` usage, or the portless proxy is down → `portless proxy start`, once per boot, or on the `ports` edge a port already held — the message names its holder · `5` a `dev down` arrived meanwhile and won · `75` another start or stop of this tree held its lock for 60 s; the message names the holder's pid.
- Never start the repo's own dev script beside it: that binds the repo's default port and skips the env the unit writes.

**Done when:** `dev up` exits 0 and the printed URLs answer.

## Stop

- `git wt -C <tree> dev down` records the want first, then signals only the process groups this tree's units spawned — never another tree's.

