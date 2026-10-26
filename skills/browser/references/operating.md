# Operating `pw`

Where the wrapper and its CLI live, how they are proven and upgraded. Read when `pw` misbehaves, or before bumping `@playwright/cli`.

## Where it lives

`~/.local/share/playwright-cli/` is a git repository holding every piece, pushed to `github.com/yann-lauwers/pw` (private); its `README.md` names each file. `bin/pw` is the wrapper, linked from `~/.local/bin/pw`; `package.json` pins `@playwright/cli`; `config/isolated.json` is the isolated browser's config; `tests/run.sh` proves it. Commit and push there after any change.

One Claude session owns one browser session named `iso-<session id prefix>` or `liv-<…>`; a `PW_SESSION` name becomes `iso-<8-char session id>-<name>`, so two Claude sessions picking the same name never share a browser. Each runs as one `cliDaemon.js` process plus its Chromium, and exits after ten idle minutes. `pw` reads `cdp_endpoint` from the config holding `role: browser` when it starts a browser; `PW_CONFIG`, `PW_CDP` and `PW_IDLE_MS` override the isolated config, the endpoint and the idle timeout for one call.

`pw` refuses what would reach past its own session or undo its browser: `close-all`, `kill-all`, `install`, a leading flag, and `open` flags that override the isolated config (`--headed`, `--browser`, `--profile`, `--persistent`, `--extension`, `--config`, `--endpoint`, `--cdp`). `state-load` without a `PW_SESSION`, and any `state-load` under `--live`, is refused too. Each refusal exits 2 and says why. `--device` and `--mobile` pass, so a recipe's device `--config` becomes `pw open --device="<name>" '<url>'`.

## Reading its state

- `pw list --all` — every open browser session on the machine, across workspaces.
- `pgrep -fl cliDaemon.js` — the daemons behind them.
- `~/Library/Caches/ms-playwright/daemon/<hash>/<session>.err` — a daemon's stderr.
- A command failing with `gave up waiting for …/pw-<session>.lock` → a `pw` process was SIGKILLed mid-start; the lock names its pid, and the next start steals it once that pid is dead.

## Proving and upgrading

`~/.local/share/playwright-cli/tests/run.sh` drives real browsers — isolation, races, idle, crash, refusals, file locations, and live mode against a stand-in browser on a port of its own. It never touches a Claude session's browser or the everyday browser. It prints one line per case and exits non-zero on any failure. Named cases run alone: `run.sh live idle`.

A bump: change the pin in `package.json`, run `npm install --no-audit --no-fund` there, then `run.sh`. Any failure → restore the old pin and reinstall. The wrapper matches two of the CLI's "not open" messages word for word, so a wording change in a new version shows up as the idle and crash cases failing.
