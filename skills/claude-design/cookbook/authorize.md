# Authorize

- Steps run in order, none skipped · which seat is used and what it is called are free.
- `C` — the terminal CLI: the `tool` `~/.claude/skills/agents-config/scripts/agents-config get --role terminal` prints, run from PATH.
- `A` — the act, `~/.local/share/claude-login/examples/design-authorize.mjs`.
- A session cannot authorize itself: `$C send` into its own seat queues until the turn ends, and nothing is left to answer the paste prompt → type the command into a second seat.

## Step 0: Decide whether the account matters at all

- The work writes into a design-system project — pushing cards, creating a project, deleting files there → continue · it only draws or reads → no grant; this cookbook does not run.
- Decide this when the design work first appears, not when the first push is about to run.
- `echo $CLAUDE_CONFIG_DIR` prints a path in the calling session → it reads its own profile, which a grant on the shared login never reaches → stop and name that to the person.

Done when the run has stopped here, or named the account it is authorizing for.

## Step 1: Resolve the owner account

- Resolve `design_owner` and its `accounts` address per `SKILL.md` § Project config.
- `design_owner` resolves to nothing inside a repo → name the `accounts` entries, settle it with the user, and write the answer into the repo's project config in the same turn, per /managing-harness , `references/skills.md` § A tool's skill and its config.
- Read `list_projects` first: a grant already on the shared login belongs to whoever minted it · its owner differs → minting for this account replaces that grant for every session on the shared login → say so and let the user decide before Step 2.

Done when one email address is named, and any grant this run would replace has been named with it.

## Step 2: Seat the helper

One seat, which exists only to hold the paste prompt:

```sh
BROWSER=/usr/bin/true claude
```

- Seat it through /cmux , `cookbook/seating.md`, with that line as the launch command and `--cwd` the repo the push comes from; a repo's own design skill loads only for a session started there.
- `BROWSER` is set at launch or not at all → a seat already running without it is replaced, never fixed.
- A fresh seat asks whether the folder is trusted → `$C send-key --workspace <ref> Down`, then `Enter`, then `$C read-screen` confirms the prompt is gone before anything else is sent.

Done when a seat ref names a session at its prompt.

## Step 3: Check the account can be signed in, without signing it in

```sh
claude-login status <email>
```

- Never `claude-login ensure` here: Step 6 signs in and authorizes in one run.
- `(cooldown N min)` on the `status` line → Step 6 would refuse for N minutes → wait it out before Step 4.

Done when `status` shows no cooldown for the account.

## Step 4: Type the command into the helper seat

```sh
$C send --workspace <ref> '/design-login'
$C send-key --workspace <ref> Enter
$C read-screen --workspace <ref> --lines 40
```

- Poll `read-screen` until `Paste code here` shows; a send into a busy seat is queued (`ctrl+enter to send now`) until its turn ends → absence means not yet, never failure.
- `A design credential is already stored — completing this flow replaces it` → that config directory holds the grant Step 1 named, and finishing replaces it.

Done when the seat shows an authorize URL and the paste prompt.

## Step 5: Read the URL off the screen

```sh
URL=$($C read-screen --workspace <ref> --lines 60 | python3 -c "
import sys
buf=''; started=False
for l in sys.stdin.read().splitlines():
    s=l.strip()
    if s.startswith('https://claude.com/cai/oauth'): started=True; buf=s; continue
    if started:
        if s and ' ' not in s: buf+=s
        else: break
print(buf)
")
```

- A URL under about 300 characters lost a line to the stitch → check it before spending a sign-in on it.

Done when `$URL` carries one unbroken authorize URL.

## Step 6: Approve it, and hand the answer straight back

```sh
CODE=$(node "$A" <email> "$URL"); rc=$?
[ $rc -eq 0 ] && { $C send --workspace <ref> "$CODE"; $C send-key --workspace <ref> Enter; }
```

- `$CODE` goes from the capture into the send only; never echoed, written to a file or printed · `${#CODE}` where a check is wanted.
- An account in several organizations → the act takes its `org` from `~/.config/claude-login/accounts.json`, or a third argument, `node "$A" <email> "$URL" "<org>"`; neither given → it stops naming the choices; never guess.
- The grant is scoped to the organization picked, and `list_projects` shows only that org's projects → Step 7's read-back decides the org was right.
- A refused code → retry from Step 4, never Step 6.
- `rc` 1 or 2 → nothing was sent; the stderr message → /claude-login 's route for a run that stopped with a message.
- `rc` 3 → claude.ai put a picture check on the consent page, which a driven browser never passes, so no retry → ask the user to open `https://claude.ai/api/account` in their own browser and confirm its `email_address` is `<email>`, signing that account in where it is not; then `open "$URL"`, and ask them to pick `<org>` where the consent page asks which organization — the `org` the act would have used; none declared → settle it with the user and write it to the manifest first, never guess — authorize, and paste the code into the helper seat, named by its cmux title; once they say it is pasted, `$C read-screen --workspace <ref>` shows this step's Done line, and a refused code → retry from Step 4.

Done when the seat prints `Design-system access authorized.`

## Step 7: Read the grant back

- Call `DesignSync` `list_projects` from the calling session itself; that read proves the caller can push.
- The readings are `SKILL.md` § The project's three; only the owner's own projects finish this step.

Done when the projects and their owner have been read back, and the owner is the address Step 1 resolved.

## Step 8: Close the helper and report

- Close the helper through /cmux , `cookbook/closing.md`.
- Report the account and what the read-back returned.

Done when the reply names the account and the projects the read-back saw.
