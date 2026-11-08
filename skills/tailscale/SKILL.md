---
name: tailscale
description: "Manages the tailnet through the Tailscale API. Started only by /tailscale ."
disable-model-invocation: true
---

# Tailscale

Needs: `TAILSCALE_API_KEY` — one tailnet's API access token; curl exits 2 naming it when it is unset.

## Calls

- Base `https://api.tailscale.com/api/v2`; the tailnet segment `-` is the token's own tailnet.
- Auth — Bearer `TAILSCALE_API_KEY`:

```sh
curl --variable %TAILSCALE_API_KEY \
  --expand-header 'Authorization: Bearer {{TAILSCALE_API_KEY}}' \
  https://api.tailscale.com/api/v2/tailnet/-/devices
```

Provenance: 2026-11-08, curl 8.7.1, `TAILSCALE_API_KEY` set from the `yann-tailscale` token — `200`, a device list; unset → `Variable 'TAILSCALE_API_KEY' import fail, not set`, exit 2.

## Traps

- An auth key is a secret: pipe it from the API straight to the joining node (`tailscale up --auth-key=file:<path>`).
- A server node just joined → `POST /device/<id>/key` with `{"keyExpiryDisabled":true}`, or its key expires.
