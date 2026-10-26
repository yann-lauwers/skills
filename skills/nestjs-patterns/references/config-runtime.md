# Config, environment and production defaults

How env reaches the app, and what a service running in production owes beyond compiling. Read when wiring `ConfigModule`, adding an env var, or hardening a service for deploy.

## Config and env validation

```ts
ConfigModule.forRoot({
  isGlobal: true,
  load: [configuration],
  validate: validateEnv,
});
```

Env is validated at boot, never lazily at the first request that happens to read it — an invalid config terminates the process instead of booting a half-working app. Config is namespaced by concern and read through typed helpers or a config service, never `process.env` scattered through feature code. Dev/staging/prod differences live in the config factory; branching on the environment inside a feature is the same fact written in N places.

## Production defaults

Structured logging with a request correlation id. Async provider initialization for DB and cache clients, each with an explicit health check. Background jobs and event consumers in their own modules — an HTTP controller is not a scheduler. Rate limiting, auth and audit logging declared explicitly on every public endpoint.
