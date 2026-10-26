# Observing the running app

- Three rungs, read top down → take the highest the app offers; a lower rung is a fallback, never a substitute for asking the app.

| Rung | What reads it | Proves | Fails as |
| --- | --- | --- | --- |
| 1. The app's own control surface | a socket, pipe, AppleScript/automation interface or debug verb set the app answers | state as the app holds it, and a capture of its own frame | a verb that does not exist yet |
| 2. The accessibility tree | AX on macOS, UI Automation on Windows, AT-SPI on Linux | what is on screen, by role and label | a blind reader that returns one element |
| 3. Pixels | a screenshot or recording | what was drawn | a stale frame from a window that did not redraw |

## Rung 1 — ask the app

- The app answers for itself → use the verbs the repo's docs name; queries return what the app holds, and a self-capture verb photographs its own frame with no Screen Recording grant.
- The app's own report and an outside reader disagree → the app's report holds, and the reader is blind.
- A self-capture needs a window that is ordered in and laid out; it may sit off every display.
- An ordered-out window never lays out → a fully headless render is not available from a normal app build.
- An app with no control surface, where verification recurs → raise the design gap in the reply (a debug-only surface answering state, drive and capture verbs); never build it inside an unrelated slice.

## Rung 2 — the accessibility tree

- The reading process needs the grant, not the app → on macOS the process running the checks, the terminal that launched it, must be an Accessibility client; `AXIsProcessTrusted()` from ApplicationServices answers it.
- Give controls stable identifiers (`accessibilityIdentifier` on Apple platforms, AutomationId on Windows) → a check addresses a control by id, never by label text or position.
- Custom-drawn surfaces — a GPU-rendered grid, a canvas — are invisible to the tree → read them through rung 1 or rung 3.

### A tree with one element is not a tree

- Before changing product code over an empty tree → separate the causes:

| Probe | Reading | Cause | Next |
| --- | --- | --- | --- |
| Is the reader trusted? | not trusted | the launching process lacks the Accessibility grant | the owner grants it; `grants-and-signing.md` |
| Read another app that has a window | one element for every app | the accessibility server is wedged | log out and back in; nothing in the repo cures it |
| Same, and ask the app itself (rung 1) | hundreds for the other app, one for ours, while ours reports a live window | the reader is intermittently blind to this process | re-read, judge from rung 1 meanwhile |
| Is the screen locked? | locked | a locked screen empties the tree while the app keeps drawing | unlock and re-run; a self-capture that renders the view itself stays valid locked; one that reads the window server's composited frame, an external capture, and a frame timing do not — the login window is frontmost |

- Print the reader's own diagnostic alongside any count, never the count alone.

## Rung 3 — pixels

- A capture taken while another app is frontmost → NOT JUDGED, never pass or fail; a backgrounded window does not redraw promptly, so it can show the same image either side of a real change.
- Surfaces that need the app frontmost → proved in the virtual machine the repo's canon launches into, where one exists; with none, listed as such; the rest of a check still reports.
- Pin the display scale for image comparison and record the scale beside each capture → template matching breaks across 100/125/150% scaling, themes and occlusion.
- A capture taken from outside the app needs the Screen Recording grant; a self-capture through rung 1 does not.
- A setting read once at launch — a theme applied to a separately configured surface → judge its pixels only on a run launched on that setting.

## Tools for the lower rungs

- Use what the machine has → `command -v` before relying on one.

| Platform | Tool | Covers |
| --- | --- | --- |
| macOS, any app | Peekaboo (`peekaboo`) | accessibility map with element ids, capture without taking focus, input to one window in the background, local OCR |
| iOS Simulator | XcodeBuildMCP / AXe | UI snapshot, tap and type by label, screenshots, video, LLDB |
| iOS, Android, macOS, Linux | Callstack `agent-device` | accessibility snapshots with refs, screenshots, logs, per-worktree device claims |
| Windows | pywinauto over UI Automation | `observation-windows.md` |

- A computer-use tool is a rung-2 or rung-3 reader with grants and a setup of its own → the app's control surface outranks it.
- One that activates the instance or moves the owner's pointer → never used on a test instance on a machine a person is using.
- One that refuses to start → a run defect of the reader: raise it once with its message, never retry it scenario by scenario.

## Evidence a reader can act on

- Every assertion says what it expected, what it saw, and carries the capture that was on screen when it failed.
- A check that could not judge → amber with its reason, never counted green.
