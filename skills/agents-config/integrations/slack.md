---
tool: slack
role: messaging
status: default
secret: >-
  nexus-slack-personal-token
defaults:
  bot_secret: >-
    nexus-slack-bot-token
  workspace: NexusGPT
  workspace_url: https://nexus-gpt.slack.com/
  team_id: T0694GBJYGG
  user_id: U09G0FDNUET
  bot_user_id: U0B44KJD8MA
  app_id: A0B3FK2S5BR
  self_dm: D09G0FDSDQX
  bot_dm: D0B4V9UJH6C
  channels:
    général: C06816WJE3Z
    aléatoire: C068J6E7N0L
    product: C09GNT5M2UE
    dev: C09SDGJG8BF
    newsletter: C09U6DVV7AR
---
# slack — user floor

- Read by the `slack` skill: its keys, and this body for what a key cannot carry.
- `#dev` — the team's dev broadcast channel.

## Roster

- Every teammate below writes in French, at `professional-friendly`.
- Nab — `U09G47W7FNE`, developer:
  - Address him as `captain`, in place of the greeting and of his name, in DMs and channels alike.
  - Never send him a nudge — no follow-up on an unanswered question, no reminder, no `up`, whatever interval has passed; a question goes to him once.
- Hassan — developer, user id unresolved.
- Shady, "the lead" — `U068FKM6TMH`, team lead.
- Assem Chammah, "the founder" — `U068RB2SDRS`, founder, DM `D09G0FE26UX` (the user token's).
- Dory, "the bot" — `bot_user_id`, handle `dory`; posts when the request or the calling skill names the bot, or for cross-team automation, never otherwise; its DM with Yann is `bot_dm`; takes its register from the calling context, never from the addressee.

## Channel posts

- Every channel in `channels` has this roster as its audience → a post there takes French, at `professional-friendly`.
- A channel post opens on `Hello tout le monde,`.
