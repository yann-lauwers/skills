# Anti-patterns, and the practices that replace them

The five shapes that produce drift, each with what it looks like in code, plus the practice list a design review reads against.

## Provider-owned guesswork

```typescript
// Database shape leaks directly to consumers.
return database.query("select * from orders");
```

The storage model now controls the public interface — including accidental renames and every field the consumer never asked for. Derive the shape from consumer jobs instead (`consumer-first.md § 2`).

## Duplicate sources of truth

```text
wiki payload example
frontend interface
backend serializer
mock JSON
```

Each copy can change independently, so none is authoritative. One canonical artifact per boundary; everything else is generated or derived from it.

## Compile-time types as the only proof

```typescript
return databaseRow as unknown as OrderSummary;
```

A cast hides incompatible runtime data behind a green typecheck. Verify serialized responses, not local type declarations (`verifying-the-provider.md`).

## Private field changes

Renaming `userName` to `user_name` in one implementation, without changing and reviewing the contract, is a breaking change — and that implementation's tests stay green the whole way through.

## Contract after implementation

Generating the artifact once both sides have finished records what happened. It coordinates no parallel work and prevents no drift; the contract's whole value was spent before it existed.

## Practices

- Design from consumer jobs, then map provider internals at the boundary.
- Make identifiers, nullability, enums and errors explicit.
- Generate types and mocks wherever the ecosystem supports it.
- Test real serialized provider output, alternate paths included.
- Treat a contract diff as a cross-team change requiring affected-owner review.
