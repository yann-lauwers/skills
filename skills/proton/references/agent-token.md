# The agent token

- It expires, one year at most → the user runs `pass-cli agent renew <agent> --expiration <1h|1d|1w|1m|3m|6m|1y>`; `pass-cli agent list` names the agent.
- The new token → whatever logs in with it, as the host's instructions route it; never an item in the vault it unlocks.
