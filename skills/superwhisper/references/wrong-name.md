# A name comes out wrong

- Audio → recogniser, biased by the vocabulary → `rawResult` → replacements → cleanup model with the mode's prompt → `llmResult`; the vocabulary never reaches the prompt.
- Which stage broke it → that dictation's `recordings/<id>/meta.json`: the first of `rawResult` and `llmResult` where the name is already wrong.

| What the recording shows | Fix |
| --- | --- |
| `rawResult` holds an ordinary word that sounds like the name | add the name to `vocabulary` in `settings/settings.json` |
| The name is in `vocabulary` and `rawResult` still holds the ordinary phrase | name that phrase and the name it stands for beside rule 17 of the mode prompt, per `references/mode-prompt.md` |
| `rawResult` is right, `llmResult` is wrong | the mode prompt, per `references/mode-prompt.md` |

- A replacement rewrites its phrase in every mode, case-insensitively, before the model reads it → only for a phrase the recordings' `rawResult`s never show meant as speech; the user adds it in Settings → Vocabulary.
- Vocabulary witness → after a restart, `~/Library/Application Support/superwhisper/models/supervocab/ipa_cache.json` holds the keys `fr\u0001<word>` and `en\u0001<word>`; the cache keeps every word it ever saw, so it proves a first-time word only.
