# Publish

- A site publish is allowed once a minute; a second inside 60 s answers `429`.
- A `200` on a write or a publish says the request landed, never what the site serves.

1. `publish_site` with `customDomains: []` and `publishToWebflowSubdomain: true`. Done: `staging_url` alone is published.
2. On `staging_url`, fetch each changed page in every locale and find the new value in the HTML; a read seconds after a publish can return the previous edge copy, so repeat. Done: every new value found · still absent after five minutes → report that the publish didn't carry it, never publish again.
3. `site_check`, `<origin>` the `staging_url`; no `site_check` → skip. Done: exit 0 · non-zero → report its failures, never step 4.
4. Once 60 s have passed, `publish_site` with `customDomains` set to `custom_domain_ids` and `publishToWebflowSubdomain: true`, then steps 2 and 3 against production. Done: both pass on the custom domains.
