# The iPhone

- Sync runs one way, computer → phone, carrying the vocabulary and the modes; the phone keeps its own `modeKeys` and `favoriteModelIDs`, each synced mode's key appended.
- The phone app, `com.superduper.superwhisper-ios`, keeps the same `settings/` and `modes/` under `/Documents/superwhisper/`, reached on a paired iPhone, by cable or Wi-Fi sync, through `uvx --from pymobiledevice3 pymobiledevice3 apps pull|push --documents com.superduper.superwhisper-ios`; `push` takes the local file first, `pull` the phone path first.
- Provenance: 2026-10-12, cable, pull and push read back byte for byte on iOS app 2.24.
- Back up the phone's files before a push.
- A phone mode carries fewer fields than the Mac's → fill a phone mode's shape from the Mac mode, folding `promptExamples` into the prompt as the Mac sends them: `EXAMPLES OF CORRECT BEHAVIOR:`, then `User:` / `Assistant:` pairs.
- A mode on a local model or on system audio stays on the Mac.
- No remote restart reaches the phone → the user force-quits and reopens the app, changing no setting in between.
- Witnesses → the Vocabulary screen, and a phone recording's `meta.json`.
