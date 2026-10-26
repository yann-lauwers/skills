# Repair

- The three drifts and their fixes are fixed · titles are judgment.

## Read the estate first

```sh
$C workspace-group list --json
$C workspace list --json
```

- Join the two on `member_workspace_refs`: per group, `anchor_workspace_ref` is the anchor · per workspace, `current_directory` says where it stands and `latest_submitted_at` whether an agent has ever run in it.
- A `custom_color` of `null` on a group or a member is no drift → report the colourless folder and leave it; `cookbook/seating.md` Step 1 owns that repair, made by the next seat into the folder.

## The three drifts

### A session runs in the folder's own header

The anchor's row has work in it → create an empty anchor beside it and move the header:

```sh
$C workspace create --name "<the effort's topmost unit>" --cwd <effort root> --group <group-ref> --focus false
$C workspace-group set-anchor --group <group-ref> --workspace <the new empty ref>
```

- The group keeps its own `name`, so the header's label does not change.
- The demoted workspace stays a member and its session keeps running.

### A seat sits outside the folder its work belongs to

Move it, and set its hue per `cookbook/seating.md` Step 1:

```sh
$C workspace-group add --group <group-ref> --workspace <ref>
$C workspace-action --action set-color --workspace <ref> --color '<the destination folder's hue>'
```

- Its hue matches the folder it leaves, or it carries none → set it to the destination folder's hue · any other hue → leave it and report it.
- The destination's hue is the folder's own `custom_color`, else the most common non-null `custom_color` among its members, both in the estate read above · neither → report it and stop after the first line.
- `$C workspace-group remove --workspace <ref>` takes one back out.

### An effort's folder is named for something other than its topmost unit

```sh
$C workspace-group rename <group-ref> --name "<the effort's topmost unit>"
$C workspace rename <ref> --title "<unit identifier> <short title>"
```

- A repository's own folder, the one named for its repo, is the other kind → leave it named for its repository; that name is how `seat.sh` finds it.

## Safety

- Repair never closes a seat holding work: promoting an anchor, adding, removing and renaming all leave every session running.
- A seat's state is ambiguous → read it before touching it: `$C read-screen --workspace <ref> --lines 40` answers without surfacing it.
