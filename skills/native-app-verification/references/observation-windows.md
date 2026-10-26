# Windows native apps — UI Automation through pywinauto

- Covers WPF, WinForms, UWP/WinUI 3, Win32/MFC and Qt.
- Electron, CEF and WebView2 surfaces are browser surfaces → their HTML layer needs browser automation.

## The stack

```
test (Python) → pywinauto (backend="uia") → Windows UI Automation → the framework's UIA provider → the .exe
```

- Install: `pip install pywinauto pytest pytest-timeout Pillow`.
- Inspect the element tree with Accessibility Insights for Windows before writing a locator.

| Framework | AutomationId quality | Note |
| --- | --- | --- |
| WPF, UWP / WinUI 3 | excellent | `x:Name` becomes the AutomationId |
| WinForms | good | set `AccessibleName` |
| Qt 6 | excellent | accessibility on by default; class names `Qt6*` |
| Qt 5.15+ | good | |
| Qt 5.7–5.14 | fair | needs `QT_ACCESSIBILITY=1` in the app's environment; set `objectName` by hand |
| Win32 / MFC | fair | control resource ids surface as AutomationId strings |

## Locators and waits

- Priority: AutomationId > name (visible text) > class + index > XPath.
- Give every interactive control a stable id before writing tests → for Qt, `setObjectName(id)` and `setAccessibleName(id)` together.
- Synchronise on conditions — `spec.wait("visible")`, `wait_not("visible")`, a polled condition with a deadline — never on `time.sleep`.
- A control that exists but never turns visible → usually a minimised or off-screen window: `restore()` it first; never `set_focus()` a test instance on a machine a person is using, which activates it.

## Framework quirks

- A Qt `QComboBox` dropdown, `QMessageBox` and `QDialog` are separate top-level windows → find them from `Desktop(backend="uia")`, not under the main window.
- `set_edit_text` raises on Qt 5 when the Value pattern is missing → fall back to click, `^a`, and `send_keys`.
- Self-drawn controls (`paintEvent`-only widgets, `QGraphicsView`, `QOpenGLWidget`, a game engine) are invisible to UIA → only the screenshot fallback reaches them.

## Isolation per test

- Fresh process per test (`scope="function"`), never a session-wide app.
- Launch through `subprocess.Popen` with per-user storage redirected into pytest's `tmp_path`, then connect by pid:

```python
env = os.environ.copy()
env["APPDATA"] = str(tmp_path / "AppData" / "Roaming")
env["LOCALAPPDATA"] = str(tmp_path / "AppData" / "Local")
env["TEMP"] = env["TMP"] = str(tmp_path / "Temp")
proc = subprocess.Popen([APP_PATH, *shlex.split(APP_ARGS)], env=env)
app = Application(backend="uia").connect(process=proc.pid, timeout=LAUNCH_TIMEOUT)
```

- Child processes that must not outlive the test → assign the process to a Job Object with `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE`; it contains the process tree, not files or network.
- A clean OS per run → run the whole suite inside Windows Sandbox (Pro/Enterprise), the build mapped read-only and the artefact folder mapped read-write.
- Cap each test with `pytest-timeout`; its `thread` method cannot kill a Qt subprocess → reap children at exit (`psutil.Process().children(recursive=True)`).

## Screenshot fallback

- Template matching (`cv2.matchTemplate`) is the last rung and breaks on display scaling:

1. Capture templates at the target machine's scale; never resize a template to rescue a mismatch.
2. Pin the CI display resolution and scaling so capture dimensions reproduce.
3. Write `GetDpiForWindow(hwnd) / 96` beside every artefact.

- Process-wide DPI awareness set in the fixture can fight Qt's own DPI handling → prefer same-scale templates and a pinned CI display.

## CI

- `runs-on: windows-latest` gives a real interactive session.
- Upload the artefact folder with `if: always()` → a red run keeps its captures.
