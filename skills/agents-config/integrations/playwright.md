---
tool: playwright
role: browser
status: default
secret: null
defaults:
  cdp_endpoint: http://127.0.0.1:9222
  profile_browser: Dia
  default_identity: personal
  identities:
    personal:     { profile: Default,   dispatch: allowed }
    nexusgpt:     { profile: Profile 3, dispatch: allowed, environments: [dev, staging, prod] }
    haras:        { profile: Profile 4, dispatch: interactive-only }
    la-pepite:    { profile: Profile 5, dispatch: interactive-only }
---
# playwright — user floor (browser)

Read by `pw`, `browser-login` and the `browser` skill.
