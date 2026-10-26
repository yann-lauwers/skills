# Observing and steering a seat

- Reading a seat answers what is happening · surfacing it takes the user's screen → read by default; surface only on request, never as part of starting a seat.

## Read without surfacing

```sh
$C read-screen --workspace <ref> --lines <n>
```

- `--lines` implies `--scrollback`, so it reaches what has scrolled off.
- `workspace list --json` answers without reading a screen:
  - `current_directory` → the path the seat was created at; it does not follow a session that moves itself in later.
  - `latest_submitted_at` → when an agent last submitted in it; absent → no agent has ever run in it.
  - `latest_conversation_message` → the last message text.

### Whether a seat is working is read from change, never from what it says

- Hash the screen across several reads → identical bytes: the seat is not progressing · anything else: it is.
- Never key a working-or-parked check on a banner: a usage-limit banner stays in the status block while the session runs on.
- Never count the spinner states caught: a turn shorter than the poll interval is invisible to a spinner check and visible to a hash.
- The composer renders placeholder text (`Press up to edit queued messages`) that looks like a typed-but-unsent message.
- A sent message is echoed into the transcript on its own `❯` line → only the last `❯` is the composer.
- A stall established → read the banners for why it stalled.

## Surface only on request

```sh
$C workspace select <ref>          # one seat, where it stands
$C workspace-group focus <group>   # the effort — focuses its anchor
```

## Write into a running seat

```sh
$C send --workspace <ref> '<text>'
$C send-key --workspace <ref> Enter
```

- `send` does not submit → write `send` and its `send-key Enter` together, always; unsent input in a composer looks exactly like a seat still thinking.
- `--command` at creation carries its own Enter; it is the create-time form and does not reach a seat that already exists.

## Labelling

```sh
$C workspace rename <ref> --title "<ticket> <short title>"
$C workspace-action --action set-color --workspace <ref> --color '#RRGGBB'
$C workspace-group set-color <group-ref> --hex '#RRGGBB'
$C workspace-group set-icon <group-ref> --symbol <sf-symbol>
```

- Name `--workspace` on every `workspace-action` call: it defaults to `$CMUX_WORKSPACE_ID`, so a set-color without it recolours the caller's own seat and reports success for the one it aimed at.
- A seat whose work has changed is renamed to match → `cookbook/seating.md` § Step 2 says when that is owed.
- A title names the unit, never the tool running in it.
- Colour is the folder's: every seat in an effort wears its group's hex.
- Setting or changing a colour, recolouring as the whole task included → read `cookbook/seating.md` Step 1 first; it owns where the hex comes from, and `scripts/seat.sh` sets a seat's colour at create time.
