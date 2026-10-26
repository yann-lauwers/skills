# The model half: validating the flagged tail

## The gate

- The pipeline takes the model client as an optional argument; no flagged records, or no client → return the regex output unchanged.
- The model sees only records the scorer flagged; it is never on the path of a record the scorer accepted.

```python
def process_document(content, *, llm_client=None, confidence_threshold=0.95):
    items = clean_records(parse_structured_text(content))
    flags = {f.item_id: f for f in identify_low_confidence(items, confidence_threshold)}
    if not flags or llm_client is None:
        return items
    return [validate_with_llm(i, flags[i.id], content, llm_client) if i.id in flags else i for i in items]
```

## The prompt

- Give the model the original text, the current extraction, and the scorer's reason tags; ask for corrected JSON, or the single token `CORRECT` when the extraction already holds — that branch keeps a right extraction from being rewritten into a different right one.

## Which model

- The cheapest tier on the vendor's models page: the validation is a short, bounded correction the scorer has already sorted.
- Pin the id from the model's own page at pinning time, never from this file: the tier holds, the id retires.
- A tail that is not latency-bound → the batch API fits it, at the pricing page's discount.
- Last read 2026-10-02, https://platform.claude.com/docs/en/models/overview: the cheapest tier was Claude Haiku 4.5.
