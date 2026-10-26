---
name: webflow
description: "Operates a live Webflow site — CMS content, pages, design, assets, audits, traffic — through the Webflow MCP server. Use to edit a CMS item, a page's text, SEO settings or structured data; to audit links, accessibility or SEO; to check traffic; on \"webflow\", \"the CMS\", \"the Designer\", \"publish the site\"; and before any `mcp__webflow__*` call or site publish."
---

# Webflow

## Project config

- Config: the repo's `docs/agents/integrations/webflow.md` over the floor, read merged: `~/.claude/skills/agents-config/scripts/agents-config get webflow <key> --root "$CLAUDE_PROJECT_DIR"`.
- No `docs/agents/integrations/webflow.md` in the repo → ask the user; on their yes, write it per /managing-harness , `references/skills.md` § A tool's skill and its config, asking which Webflow site by name, never picking one; then continue.

| Key | What it answers |
| --- | --- |
| `site` | the site's name |
| `site_id` | the site's id |
| `staging_url` | the Webflow subdomain a publish lands on first |
| `custom_domain_ids` | the custom domains' ids, which a production publish names |
| `site_check` | the repo's own check of the served site, `<origin>` the origin it reads; absent → no such check |

## Routing

| Intent | Read |
| --- | --- |
| connect, authorize, or switch site | § Connecting |
| write CMS items, pages, static text or schema markup | § Traps |
| publish | `cookbook/publish.md` |

## Connecting

- The server is `https://mcp.webflow.com/mcp`, registered in the repo's `.mcp.json`; a repo without it → `claude mcp add --scope project --transport http webflow https://mcp.webflow.com/mcp`.
- Not authorized → `/mcp`, then OAuth in the browser by a site owner or admin of that site; nothing substitutes for that person.
- One OAuth grant covers one workspace: another Webflow site is another authorization, never a parameter.
- Visual snapshots, and reading or changing the Designer's selection, page, mode, branch, canvas or breakpoints, need the MCP Bridge App running from the Apps panel; CMS, pages, assets and audits never do.

## Traps

- CMS field slugs are exact: read the collection's fields before writing `fieldData`; a slug that matches no field is dropped with no error.
- A write is a draft; nothing auto-publishes.
- `publish_collection_items` takes item ids only and publishes the primary locale straight to the live domains with no staging read → never the publish route.
- In a secondary locale, each page setting — SEO title, description, schema markup — serves the primary's value until that setting is written in that locale; the API reports unwritten markup as `isInherited: true`, and writing a translated title leaves the markup inheriting.
- A CMS item holds its own copy of every field per locale: an edit in one locale leaves every other serving the old value until each is written by `cmsLocaleId`; locale ids come from `get_site`.
- `set_text` on a page element writes the primary locale and removes that node's secondary-locale overrides → rewrite each translation right after with `update_static_content` by `localeId`; the node id is the element id, and `text` is the whole tag.
- A link's `update_static_content` override stores the whole tag, `href` included, and the first write for a locale fixes that locale's target; a later write changes only the text → write the locale's own path in its first override, never the `#` a content read returns for a page link. Untranslated, an element's own `linkType: page` resolves per locale.
- A brand-new CMS item's secondary-locale versions need creating in the Designer first; an existing item's per-locale fields read and update through the API.
- The Pages API rejects schema markup that doesn't parse as JSON, and the Designer's stored binding fails it twice — the `\}` escape and an unquoted token where a number goes: `"numberOfBedrooms":{{wf {&quot;path&quot;:&quot;<field-slug>&quot;,&quot;type&quot;:&quot;Number&quot;\} }}`. The form that validates and renders keeps the `&quot;` entities, closes with a plain `}`, and sits inside a JSON string: `"numberOfBedrooms":"{{wf {&quot;path&quot;:&quot;<field-slug>&quot;,&quot;type&quot;:&quot;Number&quot;} }}"` — so a bound Number renders as a string (`"5"`).
- A `500` from `bulk_update_pages` can arrive after part of the batch was written → re-read each page's metadata, then write the remainder with `update_page_settings`, one page per action.
- A traffic call answering empty or refused may mean Webflow Analyze isn't on the site's plan, never a broken query.
