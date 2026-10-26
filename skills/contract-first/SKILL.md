---
name: contract-first
description: "Keeps a provider and its consumers from drifting — which artifact is authoritative (OpenAPI, AsyncAPI, Protocol Buffers, JSON Schema, shared type), who generates types and mocks from it, how real responses are verified against it. Use on 'the API contract', 'openapi.yaml', 'generate the api types', 'the response shape changed', 'the mock doesn't match prod', or a field renamed, removed, retyped or made nullable in a shape more than one service reads. Not for URLs, status codes or pagination — /api-design ; not for the red-green cycle — /tdd ."
metadata:
  origin: ECC
  source: https://github.com/affaan-m/ECC/blob/main/skills/contract-first/SKILL.md
---

# Contract-First

The router for one boundary between a provider and its consumers: which artifact holds the shape, how consumers derive types from it, how the provider proves its real responses satisfy it, and what a change to it costs. It governs how a boundary CHANGES; what a good API looks like belongs to /api-design , and test-first implementation to /tdd .

Two sides build against one machine-checkable artifact and both verify against that same artifact before integration. The failure this prevents is not a compile error — it is two green test suites over incompatible shapes, which reads as finished until integration.

## Scope

Frontend and backend proceed in parallel; two or more services exchange payloads, events or commands; field names, nullability, enums or error shapes keep drifting; a provider change can break a consumer someone else maintains; mock and production responses no longer have the same shape.

A single-module boundary that changes in one atomic commit and has no independent consumer earns none of this — a shared type is enough. `references/boundary-artifact.md` carries that test.

## Routing table

| Intent | Read |
| --- | --- |
| IF deciding whether a boundary earns a contract, which artifact holds it, or what belongs in it | THEN `references/boundary-artifact.md` |
| IF naming owners, deriving the shape from what consumers actually render, or writing the first schema | THEN `references/consumer-first.md` |
| IF generating consumer types or building contract-valid mocks while the provider is unfinished | THEN `references/generating-types.md` |
| IF proving the provider's real serialized responses satisfy the artifact | THEN `references/verifying-the-provider.md` |
| IF changing a contract already in use — additive or breaking | THEN `references/change-protocol.md` |
| IF deciding whether the two sides may integrate, or clearing the pre-merge checklist | THEN `references/integration-gate.md` |
| IF a boundary already drifted, or a design is being reviewed for the shapes that cause drift | THEN `references/anti-patterns.md` |
| IF the request matches none of the above | THEN `references/boundary-artifact.md`, say which row was closest |
