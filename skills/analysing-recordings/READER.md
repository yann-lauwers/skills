You are reading a recording for an agent that will never see it. Your **hand-back** is all it gets, so whatever takes the recording to understand is settled here.

The user talks over the screen and points: "ici", "ça", "celui-là". The words say what they want; only the **still** at that moment says what they mean. The transcript is a machine's hearing of them: it drops words and misspells names.

## Steps

1. Run `scripts/breakdown.py <recording>` (beside this file) on each recording. Add `--terms` with the names and interface words in the user's message, and `--from` / `--to` when the message names a window. It prints the path of a `MANIFEST.md`.

2. Read each `MANIFEST.md` in full, then look at every sheet it lists, to follow what the screen does from start to end.

3. List the **points**: everything the user asks for, questions or decides, and, where nobody speaks, every state the screen passes through that bears on their message. A point the user later changes or cancels is replaced by where they ended.

4. Open the **still** of every point as an image, and its neighbours when it does not show what the words point at. Done when each point names what is on screen, read from a still you opened.

5. Where something moves between two stills (a drag, a drop, a menu opening), the stills on either side do not say what happened. Run the script again on that stretch with `--from` / `--to`: a short window gets stills a fraction of a second apart. Report what did happen, which is not always what the action was meant to do.

6. Send the **hand-back**.

## Hand-back

One table and nothing around it but the two lines below it.

| # | time | point | on screen | still |
| --- | --- | --- | --- | --- |

- **point**: the whole ask as the user finally left it, complete enough to act on without the recording: the rule, not the change from a moment earlier.
- **on screen**: what the still shows at that moment, in the names the interface itself uses. Say so when it contradicts the words.
- **still**: its absolute path.
- Several recordings → a **recording** column, and a point that spans two of them is one row naming both.
- A point you cannot pin down → the row reads **unclear:** what was said, what the stills around it show, and what would settle it. A guess is worse than this row.

Below the table: one line on what the recording could not show (a stretch with no still, speech too garbled to use), and one line giving each breakdown directory.
