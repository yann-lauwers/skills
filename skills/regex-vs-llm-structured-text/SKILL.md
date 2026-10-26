---
name: regex-vs-llm-structured-text
description: >-
  Decides between regex and an LLM for parsing repeating-pattern text, and shapes the hybrid
  pipeline — regex first, a confidence score per record, an LLM only on the low-confidence tail. Use
  on "regex or LLM for this", "parse this with an LLM", "extraction pipeline", "parse these
  invoices", "extract the fields from these forms"; fires when a `re.compile` or `re.finditer` is
  written over a document of repeating records, or a model call is about to run once per parsed
  record. Not for the SDK call's own shape — /claude-api .
metadata:
  origin: ECC
  source: https://github.com/affaan-m/ECC/blob/main/skills/regex-vs-llm-structured-text/SKILL.md
---

# Regex vs LLM for Structured Text

Router over parsing text that repeats a pattern — quiz questions, form fields, invoice lines, sectioned documents. One premise every row rests on: where more than 90% of records follow one pattern, regex parses them all first, and a model is called only on the records a confidence scorer flags.

## Routing table

| Intent | Read |
| --- | --- |
| IF deciding whether this text is regex work, LLM work, or both | THEN `references/deciding.md` |
| IF writing the regex parser, the cleaner, or the confidence scorer | THEN `references/pipeline.md` |
| IF adding the model call on the flagged tail, or choosing which model runs it | THEN `references/llm-validator.md` |
| IF the request matches none of the above | THEN `references/deciding.md`, say which row was closest |

## Done when

The decision — regex, LLM, or hybrid — is written down with the pattern-consistency estimate behind it. Wherever regex runs: the regex success rate and model call count are logged per run. For a hybrid: a scorer gates every model call, no call runs when no record is flagged, and parsed records are never mutated in place.
