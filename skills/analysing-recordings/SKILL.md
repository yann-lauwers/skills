---
name: analysing-recordings
description: Reads a recording through a subagent and brings back what it shows and says. Use when the user's message carries a recording (.mp4, .mov, .m4a) whose content the work needs.
---

A recording is read by a **reader subagent**, so its frames and transcript never enter this conversation. Only the **hand-back** does.

Send one **reader subagent** per message, however many recordings the message carries. Give it:

- the path of [READER.md](READER.md), to follow;
- the absolute path of every recording;
- the user's message, word for word, with any text they pasted alongside it.

The **hand-back** is a table: one row per point the user makes or the screen shows, as finally settled, with the still that proves it. Work from the rows. Open a row's still only to judge the look yourself or to attach it somewhere. A row marked **unclear** goes back to the user as a question.

When the user says a stretch was missed, send a new **reader subagent** with that time window.
