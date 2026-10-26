---
name: nestjs-patterns
description: "Structures a NestJS backend past the basics — feature modules, validation pipe and DTOs, guards, interceptors, the exception filter that emits the error envelope (the repo's own validation library and envelope win), `ConfigModule` env validation, specs. Use on 'structure this module', 'validate this DTO', 'add a guard', 'validate env at boot', `forwardRef()`, or editing a `*.module.ts`, `*.controller.ts`, `*.service.ts`, `*.dto.ts`, `*.guard.ts`, `*.filter.ts` or `main.ts`. Not for Prisma — /prisma-patterns ; not for status codes — /api-design ."
metadata:
  origin: ECC
  source: https://github.com/affaan-m/ECC/blob/main/skills/nestjs-patterns/SKILL.md
---

# NestJS Patterns

Router over production NestJS patterns. A validation library or error envelope already in the repo wins over the defaults here — read it first. Covers where a file goes, what validates a request, who takes an access decision, what an error looks like on the wire, and what a service owes before it deploys. Each intent pulls one reference; this file answers nothing itself.

## Scope

Building or reviewing a Nest backend beyond the basics — a new feature module, a guard or interceptor, an exception filter, a config factory, a transactional write, or a spec against any of them.

## Routing table

| Intent | Read |
| --- | --- |
| IF placing a file, adding a feature module, or deciding what belongs in a controller versus a service | THEN `references/module-layout.md` |
| IF wiring the global pipe in `main.ts`, writing a request DTO, or shaping what leaves the API | THEN `references/validation.md` |
| IF adding a guard, a role check, an auth strategy, or typing the authenticated request | THEN `references/guards-auth.md` |
| IF the API returns inconsistent error bodies, an exception filter is being written, or a Server-Sent Events or streaming handler is added | THEN `references/error-envelope.md` |
| IF wiring `ConfigModule`, validating env at boot, or hardening a service for deploy | THEN `references/config-runtime.md` |
| IF adding repository code, a Prisma call, or a multi-step write that must be atomic in a service with no port layer | THEN `references/persistence.md`; behind a port, the repo's own architecture canon |
| IF writing a spec against a service, a module, a guard, or the validation pipeline | THEN `references/testing.md` |
| IF a `forwardRef()` is about to be added, `import/no-cycle` fires, or boot fails on an unresolved or uninitialized dependency | THEN `references/circular-deps.md` |
| IF the request matches none of the above | THEN `references/module-layout.md`, say which row was closest |
