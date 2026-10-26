# Connection modes

What each way of reaching a browser drives. Read when the question is whose browser a command drives, or when extension mode comes up.

The mode decides whose browser is being driven, which is the whole safety question.

| Mode | How | What it drives | Reaches a signed-in session |
| --- | --- | --- | --- |
| Isolated | `pw <command>` (the CLI's `open` with `config/isolated.json`) | a headless Chromium whose profile lives in memory | no — every run starts signed out |
| CDP | `pw --live <command>` (the CLI's `attach --cdp`) | the everyday browser, launched with its debugging port | yes |
| Persistent profile | the CLI's `open --profile <dir>` | a browser launched against a profile on disk | yes, after signing in there once |
| Extension | the CLI's `attach --extension` | a tab handed over by the Playwright browser extension | not on this machine |

`pw` carries the first two. A persistent profile pointed at the everyday profile fails while that browser runs, since a Chromium refuses a profile another instance holds; that mode needs a dedicated profile, signed in once.

## Extension mode reaches no browser here

The extension looks for Chrome's profile directory, while the everyday browser is `profile_browser`. It fails with `Playwright Extension not found in "…/Google/Chrome"` and suggests setting `PLAYWRIGHT_MCP_EXECUTABLE_PATH` — a browser mismatch, not a missing install; the extension id `mmlmfjhmonkocbjadbfplnigmagldckm` is installed in every `profile_browser` profile.

Following that suggestion — pointing Playwright at the everyday browser's binary — does not fix it: Playwright launches that binary with its own user data directory, which macOS treats as a second instance of the app, and the person gets a modal saying only one instance can be open. A signed-in tab is reached over CDP instead — `references/cdp.md`.
