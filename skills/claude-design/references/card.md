# A card

- A card is a preview HTML file whose first line is `<!-- @dsCard group="…" -->`; the pane indexes by that marker, and a card without it is invisible there.
- The vendor names `group`; a repo's index writer reads `name`, `subtitle` and `viewport` off the same line → `references/manifest.md` says where each lands.
- The pane refuses remote hosts → a card loads its fonts and libraries from files pushed beside it.

## The bundle

- A card that composes published components draws from one file, `_ds_bundle.js`.
- The host compiles its own bundle from pushed component sources until a push carries one to that path; from then on it serves the copy a push last carried, and component pushes leave it as it was.
- A project pushing its own bundle builds and carries it itself, when and from which tree its own push cookbook says.
- A bundle older than the tree keeps an older tree's components drawing, or leaves a card present, indexed and blank → caught at `cookbook/push.md` step 6.
- A card naming a component the bundle lacks calls `createElement(undefined)`, throws, and leaves an empty box.
- A card drawn from the tokens alone, no bundle import, is immune to a stale bundle and proves nothing about it.
