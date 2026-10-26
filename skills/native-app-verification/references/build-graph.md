# Build graph and freshness

- A native app is usually two builds → a core (Zig, Rust, C or C++) compiled into a library or framework, and an app shell that links the prebuilt artifact.
- The shell's build never recompiles the core → a core change can be committed and the app rebuilt green without the change in the binary that launches.

## Map it before judging anything

- Name, for every artifact the launched app contains, the command that produces it and the source roots it reads.

| Shape | The artifact the shell links or embeds | Built by |
| --- | --- | --- |
| Zig / C core + Xcode shell | `.xcframework` or static library | `zig build …` (a separate step from `xcodebuild`) |
| Rust core + Swift shell | static library + generated header (`cbindgen`, UniFFI) | `cargo build` |
| Tauri | the webview's built `dist/` embedded by the Rust shell | the frontend bundler, before `cargo`/`tauri build` |
| C++ core + any shell | library from CMake | `cmake --build` |

## Prove the launched build holds the change

1. Freshness → compare the newest source under the core's roots with the artifact's modification time; the repo's own check, where it has one, is the answer. Run it after every pull, branch switch and rebase.
2. Identity → strongest form: the core's own build stamps into the artifact a content hash of every file under the core's source roots that git tracks or would track (`git ls-files --cached --others --exclude-standard`); the check reads it back through the core's API from the running instance and compares it with the same hash taken now.
   - A hash of tracked files alone stops moving while an untracked new file is edited → never the identity.
   - A commit id with a dirty flag → proves nothing while edits are uncommitted: two uncommitted states share both.
   - A stamp from the shell's build → proves only the shell, never the core it links.
3. Rebuild in order → core first, then the shell; a build that fingerprints by mtime skips work when the artifact looks newer than its inputs.

- Restoring a planted defect or a file under test → plain `cp` or `touch`, never `cp -p`: a preserved old mtime makes the build skip the restored file, and every later run grades the planted artifact.

## Hermetic builds

- Run the app build under `env -i` with an explicit `PATH` and `HOME` where the repo does → a full shell environment leaks toolchain selectors, `SDKROOT`, `CC`, a package manager's hooks.
- Never fix a build by exporting a variable the repo's own command omits.
- A link failing on an unknown option (`-lSystem`) → compiler shadowing until proven otherwise: `command -v cc`, then pin `CC`, `CXX` and the linker the way the repo's gate does.
- Keep derived data and build products out of synced folders → iCloud extended attributes on files under `~/Documents` break code signing.
- One build directory per checkout → pass the same derived-data or build directory on every build and test run, the repo's declared path where it names one; never a fresh directory per run, and never a second directory a freshness check could read by mistake.
- Read the repo's toolchain pin (`build.zig.zon`'s `minimum_zig_version`, `rust-toolchain.toml`, a required Xcode) and the installed version before diagnosing any error that could be a version gap.

## Reading a build's result

- Redirect the whole group to a log, so `EXIT=` lands in it, and re-exit with the build's own code — a call whose last command is `echo` exits 0 whatever the build did, and a backgrounded call's notification reports exactly that.

```sh
( xcodebuild …; ec=$?; echo "EXIT=$ec"; exit $ec ) > /tmp/build.log 2>&1
```

- Run the build as its own call, then read the log's diagnostics in a second call → a `grep` in the same call sets its status:

```sh
grep -nE '(error|warning):' /tmp/build.log
```

- Never pipe a build into `tail` or `head` to read its status → the pipeline returns the last stage's exit code, and the cut drops the lines that matter.
- A build wrapped in a job queue or runner goes inside the group: `( <runner> -- xcodebuild …; ec=$?; echo "EXIT=$ec"; exit $ec ) > /tmp/build.log 2>&1`.
