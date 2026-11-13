You are reading a recording for an agent that will never see it. Your **hand-back** is all it gets, and it shows it to the user for approval before acting, so whatever takes the recording to understand is settled here.

The user talks over the screen and points: "ici", "ça", "celui-là". The words say what they want; only the **still** at that moment says what they mean. The transcript is a machine's hearing of them: it drops words and misspells names.

## Steps

1. Run `scripts/breakdown.py <recording>` (beside this file) on each recording. Add `--terms` with the names and interface words in the user's message, and `--from` / `--to` when the message names a window. It prints the path of a `MANIFEST.md`.

2. Read each `MANIFEST.md` in full. Its `speech:` line reads `none` while the user's message says they spoke, commented or explained → the hand-back is the **silent** line below, and the reading ends here.

3. Look at every sheet the manifest lists, to follow what the screen does from start to end.

4. List the **points**: everything the user asks for, questions or decides, in their order. A point the user later changes or cancels is replaced by where they ended. Each point comes from words in the transcript; a recording with no speech, sent by a message that asks what the screen shows, takes its points from the states the screen passes through that bear on that message.

5. Open the **still** of every point as an image, and its neighbours when it does not show what the words point at. A shape too small to judge in a still (a corner, a ring, an inset) → cut that region from the recording at its full size with `ffmpeg` and open the cut. Done when each point names what is on screen, read from a still you opened.

6. Where something moves between two stills (a drag, a drop, a menu opening, a hover), the stills on either side do not say what happened. Run the script again on that stretch with `--from` / `--to`: a short window gets stills a fraction of a second apart. Report what did happen, which is not always what the action was meant to do.

7. Send the **hand-back**.

## Hand-back

A **listing**: the index table, then one block per point, then the two closing lines.

| # | where | problem |
| --- | --- | --- |

- **where**: the path to the element in the names the interface itself uses, down to its state: page › region › element › state, such as `Conversations › Archived › a row's ⋮ button › row hovered`.
- **problem**: one line: what is wrong, then what it should be instead, as the user means it.
- Several recordings → a **recording** column, and a point that spans two of them is one row naming both.

Then, for each row, a block under `### <#> · <where>`:

- **said**: the sentences that carry the point, quoted from the transcript in the user's language, with their time span; a name the machine misheard is corrected.
- **happens**: how to reach the state, then what is drawn there and how it differs from the same element in the state the user compares it to, in the interface's names. Say so when it contradicts the words.
- **wants**: the behaviour the user asks for, as a rule that tells fixed from not fixed. They name only the defect → `not said`.
- **stills**: the absolute path of one still per state **happens** names, each with that state.

A block is a brief: the user approves it at a glance and an agent that has seen neither the recording nor this conversation fixes the point from it alone. **happens** and **wants** take three lines each at most; what the screen shows beyond the user's words goes in one closing line, **also seen**, as a question.

A point you cannot pin down keeps its row and block, its **problem** opening on **unclear:** and its **wants** saying what would settle it. A guess is worse than this block.

Below the blocks: one line on what the recording could not show (a stretch with no still, speech too garbled to use), and one line giving each breakdown directory.

The **silent** line, sent alone: `silent: <recording> carries no voice (<the manifest's speech line>), so none of the comments the message speaks of can be read.`
