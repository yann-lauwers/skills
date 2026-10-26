# Validation — the global pipe and the DTOs under it

How request input is validated and what leaves the API. Read when wiring `main.ts`, writing a request DTO, or deciding what a response exposes.

## The repo's validation library wins

Read it first: `package.json` for `nestjs-zod`, `class-validator`, `zod` or `valibot`; `main.ts` and the root module for `useGlobalPipes`, `APP_PIPE` and `APP_INTERCEPTOR`; a neighbouring `*.dto.ts` for the DTO form. Follow what is there — schema-derived DTOs and the pipe that goes with them (`nestjs-zod`'s `createZodDto` + `ZodValidationPipe`) stay as they are; never add `class-validator` decorators beside them. A schema DTO validates only where a `ZodValidationPipe` runs on its route — globally, via `APP_PIPE`, or by `@UsePipes`; none on the route → add one, never rely on `createZodDto` alone.

A repo with one global pipe keeps it; per-route config beside it is a divergence to justify.

## Default for a repo with none

```ts
app.useGlobalPipes(
  new ValidationPipe({
    whitelist: true,
    forbidNonWhitelisted: true,
    transform: true,
    transformOptions: { enableImplicitConversion: true },
  }),
);
```

`whitelist` strips unknown properties and `forbidNonWhitelisted` rejects the request that carried them. Request DTOs carry `class-validator` decorators. A nested object or array of DTOs needs `@ValidateNested()` and `@Type(() => Child)` together — either alone validates nothing below the top level.

## Whatever the library

Every request body is validated by a pipe that runs on its route. Unknown properties are rejected on every public API — `forbidNonWhitelisted`, or `.strict()` on the zod schema.

## Responses

Responses go through dedicated response DTOs or serializers, whatever the validation library — an ORM entity returned directly leaks password hashes, tokens and audit columns the moment a column is added.
