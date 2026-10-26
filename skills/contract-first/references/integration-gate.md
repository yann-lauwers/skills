# The integration gate

Step 6 — what has to be proven before the two sides integrate, and the checklist that closes a contract-first pass.

## Evidence, not two green suites

Before merge:

- consumer types generate successfully
- consumer fixtures validate against the contract
- provider responses validate against the contract
- at least one end-to-end happy path runs
- no consumer reads an undocumented field

## Completion checklist

- [ ] Consumer and provider owners are known.
- [ ] One authoritative contract artifact is named.
- [ ] Required fields, nullability, enums and errors are explicit.
- [ ] Consumer types or fixtures come from the contract.
- [ ] Provider responses are verified against the contract.
- [ ] Sandbox, error and conditional paths are covered where applicable.
- [ ] Breaking changes carry a migration or versioning plan.
- [ ] Both sides pass against the same contract before integration.
