---
name: analysing-recordings
description: Reads a recording through a subagent and brings back what it shows and says. Use when the user's message carries a recording (.mp4, .mov, .m4a) whose content the work needs.
---

A recording is read by a **reader subagent**, so its frames and transcript never enter this conversation. Only the **hand-back** does: a **listing** of the user's points, an index table followed by one block per point.

## Steps

1. Send one **reader subagent** per message, however many recordings the message carries. Give it:
   - the path of [READER.md](READER.md), to follow;
   - the absolute path of every recording;
   - the user's message, word for word, with any text they pasted alongside it.

2. Present the **listing** to the user whole: the index table first, then every block as the reader wrote it, each **unclear** point as a question. End the reply on asking whether the listing is right. The work the recording asks for starts once the user has **approved** the listing.

3. The user corrects a point → rewrite its row and block from their words. A correction that needs the recording looked at again, or a stretch they say was missed → a new **reader subagent** with that time window and their correction. Present the listing whole again. Done when the user has **approved** it.

4. Work from the approved blocks. A point handed to another agent goes as its row and block, whole, with the repo it lives in. Open a block's still only to judge the look yourself or to attach it somewhere.

A hand-back that reads **silent** carries no listing: tell the user in one line that the recording holds no voice, and ask for a new one.
