# Wording

- A title is one action read at a glance; the notes carry what the action cannot start without.

## Language

- Every to-do → French, whatever language the request arrives in.
- The English technical vocabulary the user already speaks keeps its English root inside the French sentence; a French translation that would displace one of those words is the wrong word.
- A verb → French conjugation on the English root: `checker` · `updater` · `watcher`.
- A noun, a command, a product name → as it is: `hook` · `stop hook` · `PR` · `CI` · `skill` · `agent` · `task list` · `prompt` · `commit`.

## Title

- Infinitive verb first · 3–8 words · no trailing punctuation · one action.
- Proper nouns stay: person · brand · place · ticket · skill.
- Hedging, asides and thinking-out-loud go.
- Recurring verbs: `checker` · `voir` · `faire` · `appeler` · `commander` · `réserver` · `créer` · `installer` · `relancer` · `ajouter` · `updater`.

## Notes

- Notes hold the facts the action needs: URL · phone number · account number · address · measurements · candidate dates · the draft of a message to send · the options still open.
- A note restating its own title → delete it.

## Rewriting a capture

- The user's own words are the source → keep that vocabulary, cut the thinking-out-loud, and move each fact into the notes.
- A paragraph-long capture → a title plus notes, every fact in it surviving somewhere.

## Unclear to-dos

- A to-do that cannot be started as written → the `À clarifier` tag, plus a note naming the one question that unblocks it.

## Duplicates

- Two to-dos naming one outcome → merge into the one with the richer notes; delete the other once its facts have moved across.
- Two candidate approaches to one outcome → a single to-do, with both listed in the notes.

## The house wording, shown

- ❌ `Update test setup` — names an area, not an action · ✅ `Regrouper les tests dans des dossiers _test_`
- ❌ a five-line capture used as the title · ✅ title `Feedback groupé en fin de dispatch multi-agents`, the reasoning and the screenshot URL moved to the notes
- ❌ `Commander machine à laver`, notes `Il faut commander la machine à laver.` · ✅ same title, notes carrying the drum dimensions and the retailer link
- ❌ `Checker pour créer skill billit qui utilise l'interface (opensource ?) qui utilise l'interface ?` · ✅ title `Créer un skill Billit`, notes `À vérifier : Billit expose-t-il une API publique, ou faut-il piloter l'interface ?`, tag `À clarifier`
