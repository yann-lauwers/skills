# Resurrect a dead session

- Run the steps in order; nothing is written before Step 4 is done.
- The judgment calls are Step 3's reading of the tail and Step 5's choice of what earns a line in the handoff.
- Read the transcript with a script written at run time, its parsing adapted to what the file holds.

## Step 0 — Pick the session

- The picker shows each session the way `/resume` does — its title and last ask, never the bare id.

1. Omit the live session's own id — the `sessionId` in its transcript, or its session directory name.
2. Encode the cwd into its project directory name (`references/transcript-forensics.md § Resolving the project directory`), list `~/.claude/projects/<encoded>/*.jsonl` sorted by mtime, and take the ten most recent.
3. Script a pass over those ten and print one block per session:

   ```python
   # Per transcript, newest first, skipping the live session id:
   #  - the LAST `ai-title` line's aiTitle — the session's current name
   #  - mtime, and the count of user + assistant entries
   #  - `cwd` and `gitBranch` from any entry that carries them
   #  - PR numbers from `pr-link` lines, deduped
   #  - tracker keys grepped from message text, ranked by frequency
   #  - the last user prompt, trimmed to ~140 chars
   ```
4. Print the blocks to the user and `AskUserQuestion` which session to resurrect, labeling each option with its title plus how long ago it ended.
5. The wanted session ran in another repo or worktree → widen the scan to every directory under `~/.claude/projects/`.
6. Empty listing → say the project has no session history and stop.

**Done when:** the user has named exactly one session id, never a guessed one.

## Step 1 — Locate the artifacts

1. Find everything keyed to the id:
   ```bash
   ls -d ~/.claude/projects/*/<session-id>.jsonl ~/.claude/projects/*/<session-id> \
         ~/.claude/session-env/<session-id> ~/.claude/file-history/<session-id> 2>/dev/null
   ```
   then the task list's directory, found as `references/transcript-forensics.md § The five artifact locations` says.
2. No transcript → report the id as not found, naming the glob searched, and stop; never reconstruct an absent session.
3. Which of the five locations exist says how much of the session survived — `references/transcript-forensics.md § The five artifact locations` names what each holds.
4. Read `cwd` from any transcript entry that carries it and compare it with the current working directory; they differ → say so in the reply and in the handoff's opening paragraph.

**Done when:** the transcript path is confirmed and the target repo/worktree is known.

## Step 2 — Read the task list

- The task list is the ground truth for what was in flight.

1. Read every task file:
   ```bash
   for f in ~/.claude/tasks/<team>/*.json; do cat "$f"; echo; done
   ```
   Each carries `id`, `subject`, `description`, `activeForm`, `status`, `blocks`, `blockedBy`.
2. Note which entry is `in_progress` — the thread the handoff picks back up.
3. No task file → record the absence for Step 5.

**Done when:** every task file in the directory is captured verbatim — one for one — with the in-progress (or next pending) entry identified, or the absence recorded.

## Step 3 — Read the transcript tail

- Script the read rather than reading the transcript whole; its claims about the outside world still go through Step 4.

1. Script a pass over the `.jsonl`. Read `references/transcript-forensics.md` first — it carries the line types, the block shapes, and the traps that change what the pass finds:

   ```python
   # 1. Counter over `type` to see the shape of the session.
   # 2. Every `pr-link` entry, deduped by prNumber — the cheapest read on which
   #    PRs this session drove.
   # 3. The LAST ~150 entries: assistant text + tool_use, and user tool_result,
   #    each truncated to ~300-500 chars, so the final actions are visible.
   #    Flatten message.content blocks — an errored tool_result is the death
   #    marker for a crash, and it lives in a block, not in a top-level field.
   # 4. Grep message text for the signals Step 4 verifies: tracker keys
   #    (ranked by frequency), `worktrees/<name>` paths, PR URLs.
   ```
2. Classify how the session ended against `references/transcript-forensics.md § Death markers` — the signature sits in the last few entries.
3. Reconstruct three things in your own words: what was being built, what the immediately-next action was, and why it stopped where it did.
4. The tail is too shallow to answer those → widen the window and re-read.

**Done when:** the interrupted action is written down as one sentence, alongside what was being built and why it stopped.

## Step 4 — Re-verify every claim live

- Run each check whose signal Step 3 surfaced. Present-tense fact wins; the transcript's version is discarded, not annotated.

1. **Branch and push state** — whether the last local commit reached the remote, from the session's own repo path:
   ```bash
   git -C <repo> status --short
   git -C <repo> log --oneline -10
   git -C <repo> log origin/<branch> --oneline -3
   ```
2. **PR** — every PR number Step 3 surfaced, its checks and review threads:
   ```bash
   gh pr view <n> --json state,mergeable,mergeStateStatus,statusCheckRollup,headRefName,baseRefName
   gh api repos/<org>/<repo>/pulls/<n>/comments
   ```
3. **Ticket** — a tracker key appeared → invoke the tracker's own skill (`~/.claude/skills/agents-config/scripts/agents-config role tracker`) and read the issue's current status.
4. **Worktree** — the repo path sits under `worktrees/` → `~/.config/worktrunk/bin/wtk-step fence <tree>` exiting 0 confirms worktrunk owns it, `git wt -C <tree> dev status` gives each dev unit's state, and `git wt -C <tree> urls` gives a nexus tree's URLs. Carry the URLs into the handoff.
5. **Background commands** — every `run_in_background` command died with the session. Check `ps aux` for anything that looks like it should still be running (a PR watcher, a dev server, a test loop) and list each one in FIRST ACTIONS as needing re-arming.

**Done when:** every signal from Step 3 has a verified present-tense answer, and each contradiction of the transcript is resolved in favor of the live check.

## Step 5 — Write the handoff

1. Read `references/handoff-shape.md` — the whole document: its body, filename, sections and task-restore block.
2. Write the one file it names, shaped by it.

**Done when:** the file exists and every fact in it traces to Step 2, 3, or 4.

## Step 6 — Reply

1. Reply with the absolute path plus one copy-paste line for the fresh session:
   `Read <absolute-path> and continue from it.`
2. One extra line, only when something resisted live verification, naming what stayed uncertain.
3. Never paste the handoff body into the chat.

**Done when:** the reply carries the path, the copy-paste line, and nothing else of substance.
