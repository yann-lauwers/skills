# Evidence from a run directory

- Input → a run directory laid out per /validating `references/evidence.md` § Scenarios; any producer writing that layout qualifies.
- Before → the scenario captured on the base branch · after → the same scenario captured on this branch; a change with no before state → after alone.
- One sheet per scenario and side: `scripts/evidence.py sheet <scenario-dir> --out <png>`; a `series` scenario's frames, or its video, tile in name order.
- `scripts/evidence.py publish <png>… --repo <checkout>` → pushes onto the merged git config's `evidence_branch` and prints one image line per file; `null` → the repo publishes nothing, and Evidence stays text.
- The printed lines go into /pr 's Evidence, on its **Before:** and **After:** lines, each beside the sentence saying what to look at.
- Publish only images the body embeds; the branch is append-only and every line links an immutable commit.
- `publish` refuses a checkout whose origin no GitHub repository answers for.
