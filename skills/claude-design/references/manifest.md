# The pane's card index — `_ds_manifest.json`

What the Design System pane reads to draw its cards; a key the pane adds later is learned by reading one back.

```
namespace        "DesignSystem_<first six of the project id>" — the global the bundle exports under
components[]     { name, sourcePath }            one per component .jsx
cards[]          { path, group, viewport, subtitle, name }
                 path is the preview HTML; group, name, subtitle and viewport ("WxH") are read
                 off its @dsCard line by the repo's index writer
templates[]      { name, description, folder, entryPath, thumbnail{path,kind} }
                 one per *.dc.html artboard template
startingPoints[] empty unless the project declares any
hasThumbnailHtml true when thumbnail.html sits at the root
globalCssPaths[] the token and base stylesheets, in load order
tokens[]         { name, value, kind, definedIn, scope? }  every custom property, per theme scope
themes[]         { selector, label }
fonts[]          { family, weight, style, cssPath, files[] }
brandFonts[]     { family, status, tokens[], path }
source           "spa"
```

- `source` reads `"spa"` whoever wrote the file → it is no evidence the app rewrote the index; who last wrote it → compare what it carries against what each writer's tree holds.
- The pane groups by `cards[].group` as a string → a numbered prefix ("1 · Foundations") orders the groups.
- `components[]` is what `window.<namespace>` exposes to a card → a component absent from it renders nothing, however correct its file.
