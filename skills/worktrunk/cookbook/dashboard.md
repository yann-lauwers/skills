# Worktree Dashboard

Answers what worktrees exist and what state each is in — the default for a worktree overview.

## Step 1: Gather

- The repos → every `[projects."<host>/<owner>/<repo>"]` key in `~/.config/worktrunk/config.toml`, each resolved to its base checkout — the checkout under `~/Code` whose `git remote get-url origin` matches the key.

```bash
git -C <base-checkout> worktree list          # every tree, whoever made it
git wt -C <base-checkout> list --full         # per tree: changes, divergence, CI — over the network
git -C <base-checkout> worktree list --porcelain | sed -n 's/^worktree //p' | tail -n +2 |
  while read -r t; do [ -d "$t" ] || { echo "gone    $t"; continue; }
    git -C "$t" rev-parse --git-dir >/dev/null 2>&1 || { echo "broken  $t"; continue; }
    ~/.config/worktrunk/bin/wtk-step fence "$t" 2>/dev/null
    case $? in 0) echo "owned   $t" ;; 1) echo "foreign $t" ;; *) echo "unknown $t" ;; esac; done
```

- `git wt list` shows per tree its uncommitted changes and its divergence from the default branch and the remote; `_` or `⊂` in Status marks a branch already integrated into the default branch; `--full` adds CI status. A tree's PR state → `gh pr list --state all --head <branch>`.
- The Branch column truncates long names → read a branch or a path from `git wt -C <base-checkout> list --format json` (`items[].branch`, `items[].worktree.path`), never from the table.
- The fence loop prints one row per linked tree: `owned` (carries worktrunk's `wtk-owner` token) · `foreign` (no token) · `unknown` (`wtk-step` missing or failed) · `gone` (nothing at the recorded path) · `broken` (its `.git` link no longer resolves — its base checkout moved).
- No `~/.config/worktrunk/config.toml` on this host → list only the repo the request names, else the repo the session stands in, and skip the fence loop; Step 1 is done with the other two outputs for that repo.

**Done when:** all three outputs are in hand for every configured repo.

## Step 2: Present

Show the COMPLETE output of every command Step 1 gathered in the reply, every section — every repo and every tree: the terminal collapses tool results, so the reply is all the user sees.

**Done when:** no section has been dropped or abbreviated.

## Step 3: Act on the follow-up the listing earns

- A tree marked `_` or `⊂` → run `cookbook/delete.md`'s pre-flight on it, remove the ones that come back clean, and report what went; one holding uncommitted or unpushed work surfaces instead, per that cookbook.
- A `foreign` row → surface it, never remove it from here; who owns it → `cookbook/troubleshoot.md` § No ownership token.
- A `gone` row → `cookbook/troubleshoot.md` § A tree deleted by hand.
- A `broken` row → `cookbook/troubleshoot.md` § `fatal: not a git repository` inside a tree `git worktree list` still lists.
- An `unknown` row → re-run `~/.config/worktrunk/bin/wtk-step fence <tree>` without `2>/dev/null` and surface what it prints.
- A tree with no PR → surface it: in flight or forgotten is the user's to say.
- Nothing notable → present and stop; an empty listing is an answer.

**Done when:** every row that warrants a follow-up has one, and no follow-up was invented for a row that does not.
