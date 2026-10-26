# Troubleshoot a card in the pane

A card the owner expects is missing from the pane, or shows there blank or broken. Ends when the reply names which card drew what, and the cause of each one that did not.

- Run the file reads cheapest first; open the pane only when they leave the cause unnamed.
- Find the project and its owner per `SKILL.md` § Project config and § The project.

## Step 1 — Read the hosted files

1. `get_file _ds_manifest.json` into the scratchpad, and look for each card the owner named.
2. Cards import a component bundle → run `cookbook/push.md` step 6's bundle check.
3. `get_file` the card itself: its first line carries the `@dsCard` marker, and every script and stylesheet it loads is a file in the project.

| Reading | Cause | Fix |
| --- | --- | --- |
| the card is absent from the manifest | another writer's push replaced the index, or the push carried none | rebuild the index per `cookbook/push.md` step 2 and push it |
| the manifest names it, the marker is missing | the card was written without one | add the marker, then push the card and the index |
| a card is blank with components missing, or draws an older look | the bundle at that path is older than the tree | `cookbook/push.md` step 6 |
| a file the card loads is absent, or was written `text/plain` | `cookbook/push.md` step 4's mime rule was broken | write that file again under its own type |

Done when one row names the cause — or none does, and Step 2 runs.

## Step 2 — Open the pane as the owner

1. Run /claude-login 's pane check as the project's owner, over the cards the owner named plus one card that imports the bundle, against the index Step 1 saved.
2. Open one saved frame and look at it; each `CARD` line names its file.

- The pane is the only witness → a repo's pre-push render compiles the bundle locally, draws green against a blank hosted project, and never stands in for it.
- No route into the pane as the owner → say so; never substitute another check.
- `ABSENT` or a `dropped` path → the index row · `BLANK` with `missing=` names → the bundle row · `BLANK` with nothing missing → the card itself: open its saved frame and its source.

Done when the reply names what drew, card by card, and the cause of each that did not.
