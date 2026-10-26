# Verifying the provider

Step 5 — proving that the provider's real serialized responses satisfy the same artifact the consumer generated from. Static types are the cheap half; this file is the other half.

## Map storage to the contract at the boundary

```typescript
import type { components } from "./generated/api";

type OrderSummary = components["schemas"]["OrderSummary"];

export function toOrderSummary(row: OrderRow): OrderSummary {
  return {
    // OrderRow.id must arrive from storage as string or bigint, never an
    // already-rounded JavaScript number.
    id: String(row.id),
    status: row.status,
    total: row.total,
    cancellationReason: row.cancellation_reason,
  };
}
```

Configure the database driver to return string or bigint **before** the value reaches this function — `String(row.id)` on an already-rounded number only stringifies the rounding, since precision lost upstream cannot be restored downstream.

## Types catch fields; runtime validation catches values

Static types catch most field and enum mistakes. Add runtime schema validation, or a framework-level contract test, at the **serialization** boundary — where database values, language coercion and conditional response paths can still drift past a green typecheck.

## Verify every materially different path

- production and sandbox/mock mode
- success, and each documented error
- empty collections
- nullable fields
- feature-flagged or versioned responses

Each of those is a distinct serialization path, and a path nobody serialized is a path nobody verified. The happy path passing says nothing about the branch that returns `cancellationReason`.
