---
tool: hetzner
role: hosting
status: default
secret: >-   # fields api-token, private-key, public-key, ssh-keygen-passphrase
  nexus-hetzner
defaults:
  ssh_host: claude-code   # Host entry in ~/.ssh/config
  server: claude-code
  server_id: 172034167
---
# hetzner — user floor (hosting)

Read by the `hetzner` skill.
