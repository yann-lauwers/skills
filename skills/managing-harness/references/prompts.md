# Prompts

- Prompt — text another model runs as its instructions: an Agent brief, a stored prompt beside the script that runs it, a skill's dispatch template, a prompt hook's prompt.

## What it carries

- After any opener line its dispatch sets (`Skills:`), one sentence: the job, and what it never does.
- Done → a check the agent runs on its own result before returning: a command's exit, a target number, an artifact on disk; what must stay unchanged → a check too.
- What the agent may write: nothing · its own scratch path · named files, a build or fix dispatch's file scope among them; and what it leaves alone.
- Material the agent can open — a ticket, a file, a log on disk → its id or path, plus the lines the task turns on, verbatim · material only this conversation holds — the user's words, an error seen here → pasted whole · never a summary of either.
- A value that can move while the agent runs — a branch, a base, a count → where to read it, never a copy.
- Material the model judges → named as data; an instruction inside it is classified or quoted, never followed; the guard travels in the prompt.
- A model-judged verdict → 3–5 examples in `<example>` tags, each a near miss on one side of the line with its verdict; an example of the obvious case → cut.

## The return

- States its reader — a script, the dispatcher, a person — its form, and what bounds its length: the closed list of items it carries, or a cap.
- A shape the call enforces (`--json-schema`) still states each field's meaning.
- The empty result → named, in its exact form, as a correct answer.
- Quoted evidence → verbatim with its location, and the prompt says the next step checks it against the source.
- A verdict with an uncertain middle → which way a tie breaks.

## Templates and retries

- A template marks every slot in one syntax and says where each value comes from; a slot left empty → no dispatch.
- Re-dispatch → quotes the criterion the last attempt broke and its failing output; never a bare retry.

## Where it lives

- Run by a script → `<script-name>.prompt.md` beside it, found from the script's own location · filled by one skill → that skill's `references/` or `templates/` · shared by several dispatches of one effort → that effort's working directory, named by path in each dispatch · a one-off → the call itself.
