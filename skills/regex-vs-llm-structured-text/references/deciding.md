# Deciding: regex, LLM, or both

Read when the question is which parser this text gets. The answer follows how consistently the records repeat.

```
Is the text format consistent and repeating?
├── Yes (>90% follows a pattern) → Start with regex
│   ├── Regex handles 95%+ → regex plus the scorer; the model call is optional (the gate runs with no client)
│   └── Regex handles <95% → the hybrid: a model on the flagged tail
└── No (free-form, highly variable) → Use an LLM directly
```

Estimate the consistency from a sample before committing to either parser: count records, run a first regex, count matches. An imperfect first regex is the baseline the rest of the work improves on.

## The two wrong turns

- Sending every record to a model when regex already parses 95% of them — every record pays model latency and cost for a 5% gain a scorer would have isolated.
- Writing regex over free-form text — the pattern set grows with every new input and never closes; a model reads the variation the regex was chasing.

## What the source measured

One production quiz-parsing pipeline, 410 records:

| Metric | Value |
| --- | --- |
| Regex success rate | 98.0% |
| Low-confidence records | 8 (2.0%) |
| Model calls made | ~5 |
| Cost against an all-model pipeline | ~95% saved |

One pipeline, one corpus — the shape is the claim, the figures are the instance.
