# The regex half: parser, cleaner, scorer

Read when writing the deterministic stages. The pipeline is one direction, and the scorer is what makes the model call optional:

```
Source text
  → [Regex parser]      one immutable record per match
  → [Text cleaner]      strips markers, page numbers, artifacts — returns new records
  → [Confidence scorer] one score and its reasons per record
      ≥ threshold → output as parsed
      < threshold → the model validator (references/llm-validator.md)
```

## Records are immutable

Every stage returns new records — a frozen dataclass, or the language's equivalent. A validator that edits a record in place leaves the scorer's reasons pointing at text that no longer exists; a cleaner that does so leaves the parser's output and the cleaner's output as one object, so a test against the parser cannot tell which stage changed it.

## The scorer's contract

The score is a number in `[0, 1]` and a tuple of reason tags, never a bare number: the tags are what the validator prompt reads.

```python
@dataclass(frozen=True)
class ConfidenceFlag:
    item_id: str
    score: float
    reasons: tuple[str, ...]

def score_confidence(item: ParsedItem) -> ConfidenceFlag:
    reasons, score = [], 1.0
    if len(item.choices) < 3:  reasons.append("few_choices");   score -= 0.3
    if not item.answer:        reasons.append("missing_answer"); score -= 0.5
    if len(item.text) < 10:    reasons.append("short_text");     score -= 0.2
    return ConfidenceFlag(item.id, max(0.0, score), tuple(reasons))
```

Start at 1.0 and subtract a fixed penalty per defect the regex can see — a field missing, a list too short, a text too short for the record it claims to be. The defects and their weights are the corpus's own: the ones above fit a multiple-choice quiz and nothing else. The threshold is a parameter with one default, set where the pipeline is assembled (`references/llm-validator.md` § The gate), so a run can widen the tail without a code change. `identify_low_confidence(items, threshold)` runs `score_confidence` over every record and returns the flags below the threshold; that list is what the gate reads.

## Tests and logs

Write the tests before the regex: one per known pattern, then the malformed cases — a missing field, a record split across a page break, an encoding artifact. Log the regex success rate and the model call count per run; a move in either, with the parser, cleaner, scorer weights and threshold unchanged, means the corpus changed.
