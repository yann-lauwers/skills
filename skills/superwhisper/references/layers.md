# The Two Layers

## The pipeline

- Audio → recogniser → raw transcript → literal replacements → cleanup model with the mode's prompt → final text.
- A name the model spells wrong → the vocabulary cannot touch it.
- A name the recogniser misheard reaches the model as the words it heard → the prompt maps it back only when it names that exact mishearing.

## Which stage owns the symptom

| Symptom | Stage | What fixes it |
| --- | --- | --- |
| A command name comes out as an ordinary French or English word that sounds like it | Recogniser | Add the name to the vocabulary |
| A command name is spelled as something that does not exist, but sounds right | Cleanup model | List the real names in the mode prompt |
| A recurring, specific mishearing of a fixed phrase | Recogniser | A literal replacement, scoped tightly enough to avoid ordinary speech |
| A name already in the live vocabulary keeps arriving as an ordinary phrase that sounds the same | Recogniser — its bias loses to the common phrase | Name that phrase beside the mode prompt's rule for decoding in the technical register, with the name it stands for; a replacement only where the count `cookbook/diagnose.md` takes at its layer check shows the phrase never meant as speech, since it rewrites the phrase in every mode before any model reads it |
| The final text ignores a prompt rule | Cleanup model | The mode prompt |
| Unclear which | — | Compare a recording's raw transcript against its final text: the stage that broke it is the one where the name is already wrong |

## Layer 1 — the recogniser

- The vocabulary is a set of recognition hints, never an output rewrite.
- It lives in the settings file, so it is global: an entry biases every mode, not the one it was added for.
- A name that is also an ordinary word pulls plain speech toward it; an oversized vocabulary degrades punctuation, language detection and formatting, and no numeric limit is published → add only names a symptom calls for.
- The app phonemises every entry in French and in English, code-switched readings for an English name inside a French sentence included.
- Literal replacements apply after the recogniser and before the model, case-insensitively, in every mode.
- A replacement keyed on a bare word rewrites every use of it before the model sees it → key each one on the fixed phrase.

## Layer 2 — the cleanup model

- The mode's prompt is the only injection point under control.
- Context toggles feed it the clipboard, the selection or the active window; the window scrape supplies the proper nouns it sees, driven by what is on screen, never by config.
- No variable interpolation · no static context file.
- A mode's script field runs AppleScript after the model, on the finished text through a macro → it cannot inject context.
- No pre-dictation hook exists anywhere in the app → context computed at dictation time has no substrate.
- The prompt holds one generated block among its handwritten rules: the roster of real command names, under rule 24 of section F.
- The generator rewrites everything from rule 24's line to the end of the prompt, keyed on that rule's opening words → handwritten text goes above rule 24; changing its opening words makes the generator refuse the write.
- The roster travels with the rule that governs a near miss: close to exactly one entry → write that entry · close to none or to two → keep what was heard.
- Add, keep or remove the roster and the near-miss rule together, never one without the other.
- `$G --measure` prints the share of written command names matching a real skill across the recordings corpus, and the near-miss rule's compliance.

## What the app offers for automation

- No CLI and no HTTP API; the API reference on the vendor's documentation site is an unmodified starter template, not this product.
- Deep links drive the UI — open settings, switch mode, start recording — and accept no configuration parameters.
- Two routes remain: the vocabulary CSV import in the interface, the manual path · writing the config files, loaded at the app's next launch, the automated path, under `cookbook/apply.md`.
