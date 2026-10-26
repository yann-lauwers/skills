# Cleanup pass

`<scratch>` is this session's scratchpad; `<skill>` is `~/.claude/skills/disk-cleanup`.

1. Map the volume: `bash <skill>/scripts/scan.sh <scratch>` in the background, then read `<scratch>/tree.txt` whole.
   Done when `tree.txt` exists and its row 1 total, the `df` used figure and `unreadable.txt` are in hand.
2. Show the map: `tree.txt` verbatim in one code block, headed by free space, volume used, scanned total and what the gap holds.
   Done when the owner has every row number to point at.
3. Research: dispatch one Sonnet agent per area in `references/agent-briefs.md`, all in one message.
   Done when every agent has reported, and each candidate carries evidence that it is out of use.
4. Verify the cheap facts the agents left open — a PR state, a process, a session's idle time — before ranking.
   Done when no candidate rests on "likely".
5. Present one table per class, largest first, IDs the owner can quote:

   | ID | GB | What | Why |
   |---|---|---|---|
   | A1 | 29.0 | Scratchpad `/private/tmp/claude-501/…nex-6579/da09…` | Repo copies from a closing review; every PR merged, worktree gone, idle 18 h |
   | B1 | 10.1 | Claude desktop's Cowork VM | Used yesterday; rebuilt on next use |

   - A → nothing is lost: it rebuilds, it is temporary, it duplicates something kept, or its work already landed.
   - B → something is lost or its use is in question; the Why names what goes.
   - Kept for unsaved work — dirty files, commits on no remote, a live session — listed below the tables, each with what it holds.
   - Close with the A total, the B total and the free space after each.
   Done when every agent candidate sits in A, B or the kept list.
6. Ask the owner which IDs to clean, and wait.
   Done when the owner has named them.
7. Clean exactly the named IDs:
   - Worktrees → /worktrunk ; the owner's pick of an A or B row is the choice to lose what it holds.
   - Duplicate trees that must stay readable → `python3 -I <skill>/scripts/clone_dedupe.py <dirs…>`, then again with `--apply`; files become APFS clones sharing blocks, every path and byte kept.
   - Package caches → their own prune command, run from a repo that pins the tool's version.
   - Every path removal → one script at `<scratch>/free-disk-<n>.sh` that re-checks each path for a process inside at run time, skips it when busy, and prints the free space before and after; `rm -rf` outside the scratchpad is refused here, so the owner runs it as one `! bash <script>` line.
   - Time Machine local snapshots pin every deleted byte until thinned → after the deletes, the owner runs `! sudo tmutil thinlocalsnapshots / 999999999999 4` on its own line, where `sudo` can prompt.
   - A retention setting or backup exclusion the owner picks → /managing-harness .
   Done when `df` shows the freed space and each named ID is gone or reported with why it stayed.
8. Report the freed total against the table's estimate, and each source that refills on its own — a leak, a missing rotation, a cache with no cap — as the fix it needs at its source.
