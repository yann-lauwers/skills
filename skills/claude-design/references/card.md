# A preview

- A preview is `project/components/<Comp>/preview.html`, `<Comp>` an ASCII JS identifier; its first line is `<!-- @dsCard group="…" height=N -->`, and `page` on that line marks a showcase page rather than a bundle export.
- The frame preloads `project/tokens.css`, the fonts, `components/bundle.css`, the index's `libraries` and `components/bundle.js`, then sets `data-theme` to the first theme · a preview loads more only by a relative path (`../../<path>`), an upload's `/_blob/<id>`, the artifact script CDNs and Google Fonts.
- `tokens.css` is the page's own file unless its first line is `/* <title> — generated from tokens.json */`: a system synced from code writes it on every publish.
- Anything under `project/assets/` that is not text is an upload, recorded in the index's `assetGroups`, never a file.
- `components/Cover/preview.html` is the system's cover, kept bare: a `README.md` beside it makes it a component.

## The bundle

- `components/bundle.js` is one classic script assigning `window.<namespace>`, the index's `namespace`; its first line `/* @ds-bundle: {"format":4,"namespace":"…","components":[{"name":"…"}]} */` names the components in order.
- No literal `</script` or `<!--` in it: a page inlining it ends there.
- A preview naming a component the bundle lacks throws and leaves an empty box.
