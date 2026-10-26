# Troubleshoot a component on the page

A component the owner expects is missing from a published system, or shows there blank or broken. Ends when the reply names which preview drew what, and the cause of each one that did not.

- Run the file reads cheapest first; open the page only when they leave the cause unnamed.
- Find the system per `SKILL.md` § Project config.

## Step 1 — Read the hosted files

1. `Artifact` `list` the link with `scope: "files"`, and look for `project/components/<Name>/preview.html`.
2. `Artifact` `read` the preview and `project/components/bundle.js`'s first line.

| Reading | Cause | Fix |
| --- | --- | --- |
| no `preview.html` for the component | the export wrote none, or a publish removed it | export the tip again and publish, per `cookbook/push.md` |
| its first line is not the `@dsCard` marker | the preview was written without one | fix the exporter, then publish |
| the bundle's header lacks the component, or its namespace differs from the index's `namespace` | the bundle and the index come from different trees | publish the whole export of one tree |
| the preview links a path the files listing lacks | the export left a file out | fix the exporter, then publish |

Done when one row names the cause — or none does, and Step 2 runs.

## Step 2 — Open the page

1. Run `cookbook/push.md` step 6's act over the components the owner named.
2. Open the screenshot it saved for each one.

- The page is the only witness → a local render of the export draws against files the page may not serve, and never stands in for it.
- `ABSENT` → the Components view never mounted that preview: Step 1's first row · `BLANK` → the preview mounted and drew nothing: read its console errors in the act's `ERRORS` line, then its source.

Done when the reply names what drew, component by component, and the cause of each that did not.
