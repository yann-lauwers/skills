# Consumer-first — owners, jobs, and the first schema

The first three steps of a contract-first pass: who owns and consumes the boundary, what each consumer actually has to render, and the smallest schema that answers it. Generating types from the result is `generating-types.md`.

## 1. Identify consumers and owners

Record four facts before designing anything: who consumes the boundary, who owns the provider, who may approve contract changes, and which artifact is authoritative.

One owner resolves ambiguity. Ownership does not mean the provider designs the contract alone — a shape designed without its consumers is the storage model with a new name.

## 2. Describe consumer jobs

Start from what each consumer must render or accomplish, then ask:

- Which fields are actually required?
- What do missing, empty and null each mean?
- Which identifiers must remain strings?
- Which enum values can the consumer handle?
- Can one task-oriented response replace several coupled calls?
- Which errors require different consumer behaviour?

Never expose a database row and call it a contract.

## 3. Define the smallest useful contract

```yaml
# openapi.yaml
openapi: 3.1.0
components:
  schemas:
    OrderSummary:
      type: object
      required: [id, status, total]
      properties:
        id:
          type: string
          description: Opaque identifier; never parse as a number.
        status:
          type: string
          enum: [pending, paid, cancelled]
        total:
          type: number
          format: double
          minimum: 0
        cancellationReason:
          type: [string, "null"]
```

Define semantic constraints, not only syntax. `cancellationReason` being nullable is syntax; that it is null for every status except `cancelled` is the constraint a consumer branches on, and it belongs in the description.

Prefer a small compatible addition over a speculative general schema.
