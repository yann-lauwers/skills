# Changing a contract already in use

The ordered protocol for moving a live boundary, and what separates an additive change from a breaking one.

## Protocol

1. Propose the consumer need and the compatibility impact.
2. Change the canonical artifact.
3. Review the contract diff with the affected consumers and the provider.
4. Regenerate types, clients and fixtures.
5. Update provider and consumer implementations.
6. Run consumer and provider verification (`verifying-the-provider.md`).
7. Merge only once every affected side agrees on the new contract.

## Additive vs breaking

**Additive change** — verify that old consumers keep working against the new artifact. A field added as optional and defaulted is additive; the same field added as required is not.

**Breaking change** — use the repository's versioning or migration policy. Never silently repurpose an existing field: a rename or a narrowed type under the old name is a break wearing the old field's clothes, and every consumer's typecheck stays green while the values change underneath.

