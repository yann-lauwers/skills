# Services — Is It Running, At Which URL, Why Isn't It Answering

- A dev server answers at a stable portless name, `https://<id>.<app>.localhost`, `<id>` derived from the tree's directory name, its port negotiated at each start and never pinned by hand — except on the `ports` edge, at `http://localhost:<port>`.
- A repo runs a managed dev server only where its project entry declares a `dev` alias: a single-server repo through `wtk-web`, a repo with a project folder through its own command.

## Step 1: Status first

```bash
git wt -C <tree> dev status
```

- Status reads the units' records and probes nothing → a unit reading `up` whose URL fails still goes to Step 2.

**Done when:** each unit's state is in hand.

## Step 2: Read the URL and the log

- The URL is the `url:` line `dev up` printed; probe it as printed: `curl -sS -o /dev/null -w '%{http_code}\n' <url>`.
- Why a unit fails → `git wt -C <tree> dev logs [unit] [-f]`; `wtk-web`'s unit is `web`.

**Done when:** the URL answers, or its failure has a log line naming why.

## Step 3: Start what is missing

```bash
git wt -C <tree> dev up
```

- It blocks until every health probe answers — `wtk-web` up to 120 s, a project folder's per its `AGENTS.md` → run it in the background and wait on its notification.
- A killed caller leaves the units running; `git wt -C <tree> dev down` is the stop, and it signals only this tree's units.
- Never start the repo's own dev script beside it: that binds the repo's default port and skips the env the unit writes.

**Done when:** `dev up` exits 0 and the printed URLs answer.
