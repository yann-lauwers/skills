# Generating consumer types and mocks

Step 4 — deriving the consumer's types from the artifact rather than hand-copying them, and building contract-valid mocks so the consumer ships while the provider is unfinished.

## Generate, do not transcribe

```bash
npm run generate:api-types
```

Back that script with the repository's existing **pinned** OpenAPI generator — the one already in the manifest, run through the project's own package manager, never an on-demand runner that resolves a same-named package from a registry.

Delete handwritten copies once the generated or derived version exists. Two definitions of one shape drift, and the handwritten one is the copy that stays green.

## Build the mock against the generated type

```typescript
import type { components } from "./generated/api";

type OrderSummary = components["schemas"]["OrderSummary"];

export const paidOrderMock = {
  id: "9007199254740993123",
  status: "paid",
  total: 49.9,
  cancellationReason: null,
} satisfies OrderSummary;
```

`satisfies` is what makes the mock contract-valid — it checks the literal against the generated type while keeping the literal's own narrow types. A cast (`as OrderSummary`) asserts instead of checking, and a mock that lies is worse than no mock.

The id is a string in the fixture for the same reason it is a string in the schema: an identifier past 2^53 loses precision the moment anything treats it as a number.

The consumer now builds against contract-valid mocks while the provider is still in progress — which is the parallelism the whole pass exists to buy.
