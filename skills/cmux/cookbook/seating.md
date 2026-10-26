# Seating

- The caller decides which units there are, what each is called and the order they seat in; this file places them.

## Step 1: Resolve the folder

- `scripts/seat.sh` derives the folder from the repo's `seat_folders` and creates the repository's folder when none exists → omit `--group` unless the effort has its own folder or the script reports an ambiguity.
- The repository's folder is found by its name → a folder renamed away from its repo's name is not found and a second is created beside it: rename it back, or pass `--group`.
- `per-repository`, one unit, or seats landing where a folder already covers them → nothing to decide; go to Step 2.
- `per-effort`, and an effort with no folder yet → read `$C workspace-group list --json` first (names are not unique), then create it and seat with `--group`:

```sh
$C workspace-group create --name "<the effort's topmost unit>" --cwd <effort root path>
$C workspace-group set-color <group-ref> --hex '<#RRGGBB>'
```

- Run both: `create` takes no colour flag · `set-color` works though `--help` omits it.
- Omit `--from`: the group is then created anchor-only and stays empty; `--from` promotes a workspace holding work to anchor, and its session then runs in the folder's header.
- `--cwd` is the effort's root, never the first unit's worktree.
- After any change to `seat.sh` → `bash scripts/seat-test.sh`; `SEAT=<copy>` runs it against a mutation.

Done when: the effort names one group ref with a non-null `custom_color` and a root `--cwd`, or its seats derive the repository's folder.

### The folder's hue

- `seat.sh` repairs a colourless folder and adopts the hue its members wear → never recolour by hand before seating.
- A hue picked → /house-style 's chart palette, one no neighbouring folder wears; the palette carries no meaning.
- `CREATED … (closest hue already worn: <hex>)` → judge that pair on the sidebar; recolour the new folder where the two read as one.
- A member wearing a different non-null hue → leave it and report it.
- Two folders sharing a hue → the one with more members wearing it keeps it; the other takes a new pick.

## Step 2: Title the seats

- One seat per unit, in the caller's order; the effort's root unit gets a member seat like any other, never the anchor.
- Title = the unit's identifier + a short label.
- What a seat holds changes → re-title it: `$C workspace rename <ref> --title "…"`, by whoever sits in it or reuses it.

Done when: every unit has a title and an absolute location, and no live seat's title names work that has left it.

## Step 3: Create each seat

```sh
${CLAUDE_SKILL_DIR}/scripts/seat.sh \
  --name "<unit identifier> <short title>" \
  --cwd <the unit's location> \
  --group <group-ref> \
  --command '<absolute path of a launcher script>'
```

- `seat.sh` is the only create: never `workspace create` then a colour call.
- One run per seat; never loop over packed pairs — zsh does not word-split an unquoted parameter.
- `--command` is parsed by the seat's shell → never put prompt text in it: write the prompt to a file, and pass a script whose last line runs `claude "$(cat <file>)"`; an apostrophe in an inline prompt leaves the seat at `dquote>` while `seat.sh` still reports `SEAT`.
- An empty seat for the user to type in → omit `--command`.
- Exit codes, each stopping the run:
  - 2 → bad argument, unknown group, or an unreadable or invalid `seat_folders`.
  - 3 → no hue to adopt, or every hue worn → pick per § The folder's hue, re-run with `--hex`.
  - 4 → the colour did not stick (repair the named ref, never create a second seat), or the create failed (no seat exists; re-run).
  - 5 → ambiguous folder: two groups stand in `--cwd`, two are named for the repo, or `--group` disagrees with the derived one → pass the right `--group`. Nothing is created.
  - 6 → `--cwd` in no git repository and no `--group` → create the effort's folder per Step 1, pass it.

Done when: every unit printed `SEAT <ref> <hex>` or is reported as staying behind.

## Step 4: Report

- Name the folder and, per seat, its unit, ref and location.
- Record each seat's UUID (the listing's `id`) beside whatever state the caller keeps.
