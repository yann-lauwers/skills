# The isolated mode — what it launches

What `pw <command>` runs, and why its settings live in a config file. Read when a browser window appeared in front of the person, when the config has to change, or when the question is which binary the signed-out route uses.

`pw` opens the browser with `--config` pointing at its own `config/isolated.json`, and that file is the whole configuration:

```json
{ "browser": { "browserName": "chromium", "isolated": true,
               "launchOptions": { "headless": true } } }
```

It launches Playwright's bundled `~/Library/Caches/ms-playwright/chromium_headless_shell-<build>/…/chrome-headless-shell` and touches no installed browser.

**Without `browserName: chromium`, the CLI resolves the `chrome` channel and launches Google Chrome** — a window in front of the person on every page check. The CLI's `--browser` flag takes `chrome`, `firefox`, `webkit` and `msedge` but no plain `chromium`, so the setting lives in the file. The file names no version-numbered path, so a Playwright upgrade moves the build without touching it.

Nothing is left on disk between runs, and every browser starts signed out. A run that needs a login loads a minted session file — `references/session-files.md`.
