# Editing a mode prompt

- The slash-command sync owns a prompt from rule 24's line to its end, keyed on that rule's opening words (`SW_MODES` in `scripts/live_config.py`) → handwritten text goes above rule 24, and those opening words stay as they are.
- The whole prompt travels to the model on every dictation → write the addition as prompt content under a heading the prompt already has.
- Witness → after a restart and one dictation in that mode, the new text inside the `prompt` field of that recording's `meta.json`.
