---
name: cloudflare-ops
description: >-
  Resolves this machine's Cloudflare account, zone and a repo's tunnel or R2 bucket from its
  config. Use when the user says "expose a port", "public URL for localhost", "tunnel",
  "cloudflared", "R2 bucket", "upload to R2". Also fires on the ACT — before a `cloudflared
  tunnel` or `wrangler r2` command runs. Not for what a Cloudflare product does or how its
  CLI works — /cloudflare , /wrangler .
---

# Cloudflare ops

## Project config

- `~/.claude/skills/agents-config/scripts/agents-config get cloudflare <key> [--root "$CLAUDE_PROJECT_DIR"]`; the floor is `~/.claude/skills/agents-config/integrations/cloudflare.md`, the project file `<repo>/docs/agents/integrations/cloudflare.md`.
- A repo with none → ask the user; on their yes, write one per /managing-harness , `references/skills.md` § A tool's skill and its config.
- `scope` — the capabilities this repo may touch: `[tunnel]`, `[r2]` or `[tunnel, r2]`; one outside `scope` → say so and stop.
- `role` → `tunnel` where tunnels are in scope, else `object-storage`; a `[tunnel, r2]` repo's R2 half → by the tool name `cloudflare`.
- Floor keys: `zone` · `account_id`.
- Tunnel keys: `hostname` and `tunnel_name`, a literal or its derivation · `wrapper`, the entry point where one exists · `port_source` · `driver`.
- R2 keys: `bucket`; commands take that `bucket`, never one picked off `r2 bucket list`.
- A key absent → resolve it from `cloudflared tunnel list` and the repo's gitignored `.env`; one neither answers → name it as missing.

## Who uses what

- Tunnels → `cloudflared`, logged in by `cloudflared tunnel login` (`~/.cloudflared/cert.pem`); a repo naming a `wrapper` → that entry point.
- R2 → `npx wrangler@4`, logged in by `npx wrangler@4 login`.
- Both logins leave the config's `secret` null.
