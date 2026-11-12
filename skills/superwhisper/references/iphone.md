# The iPhone

- Nothing syncs between the Mac and the phone → a file push is the only route, last proven by cable on 2026-10-12, iOS app 2.24.
- The phone app `com.superduper.superwhisper-ios` keeps `settings/settings.json` and `modes/<key>.json` under `/Documents/superwhisper/` → `uvx --from pymobiledevice3 pymobiledevice3 apps pull|push --documents com.superduper.superwhisper-ios`; `usbmux list` answers `[]` → ask the user to plug the phone in.
- Pull the phone's files to a backup first; the pushed `settings.json` keeps the phone's own `modeKeys` and `favoriteModelIDs`, a new mode's key appended.
- A phone mode holds fewer fields than a Mac mode → build it from a pulled phone mode, folding the Mac mode's `promptExamples` into `prompt` the way the Mac sends them: `EXAMPLES OF CORRECT BEHAVIOR:`, then `User:` / `Assistant:` pairs.
- The phone loads the push once the user force-quits and reopens the app; witness → a phone recording's `meta.json`, pulled back.
