# Instance isolation

- A test instance shares the owner's per-user state until every root it touches has moved: its control socket, logs, preferences, caches, application support, config directories, session records, keychain items, and any sibling tool's home it reads.
- Launched plainly, a test build binds the running app's socket, writes into its log, and can act on the owner's real data.
- One path resolved to the real home instead of the run directory is enough to act on the owner's data → every root is proven moved, never assumed.

## Moving the roots

- GUI frameworks resolve user directories through OS APIs, and several ignore environment overrides.
- macOS: `HOME=` moves nothing those APIs resolve.
- macOS: `CFFIXED_USER_HOME=` moves `NSHomeDirectory()`, `homeDirectoryForCurrentUser` and the Application Support URL into the fake home.
- macOS: `UserDefaults` still writes to the real `~/Library/Preferences`, keyed by bundle or executable name → preferences need their own override: a suite name, or a separate bundle id for test builds.
- A socket, log or sibling tool's home the app places by its own logic → needs an override the app reads, or one variable relocating a run directory.
- Windows: `APPDATA`, `LOCALAPPDATA` and `TEMP` redirect most frameworks (`observation-windows.md`).

## Launching one

1. Use the repo's isolated launcher; it names every variable and kills what it last started. Read the launcher for the set, never a doc restating its count.
2. No launcher → list each root the app writes (grep the source for the home, support-directory and defaults APIs), give each a run-directory override, and prove it: after launch, list what the instance wrote and confirm nothing new landed under the owner's directories.
   - A static check that no source path resolves to the real home catches the class before any launch.
   - On a machine a person is using, prove it never activates as well: on macOS a bare executable started from a shell activates itself and takes key; the same bundle opened with `open -g` stays inactive.
3. Record the launched pid in the run directory. Kill by that pid, never by name pattern → a pattern kills the owner's copy too.

## Driving one

- Never activate the instance on a machine a person is using → an active app takes the owner's keyboard; inside a virtual machine the repo's canon launches into, activating takes only that machine's front.
- Never send a global chord — close-window, quit, hide — on a machine a person is using → it resolves in the focus context, which may be the owner's window.
- Inside a virtual machine → the instance and its reader run in the guest's GUI session, never in a plain ssh session.
- One instance per check, in series → a state one check leaves (a theme, a panel, a second window) is never read by the next as the product's; two instances at once compete for the front, and a backgrounded window does not redraw promptly.
- A setting read once at launch → launch, switch, and launch again before judging it.
- A seam that lands one walk in three → hunt it across several fresh instances, counted; one green pass never certifies a live defect.

## Worktrees

- Every worktree builds its own app; each driven run gets its own run directory, even within one worktree.
- A machine the repo opens at an instance's first launch and keeps for later ones → build in it through the repo's command; a build on this host is not the one launched there.
- A local signing file or local config the main checkout holds may be absent from a worktree → `grants-and-signing.md`.
