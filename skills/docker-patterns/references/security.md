# Security

Dropping what a container does not need, and getting a secret to it without writing the secret anywhere. Read when hardening a service or when a credential has to reach a container.

## Compose hardening

```yaml
services:
  app:
    security_opt:
      - no-new-privileges:true
    read_only: true
    tmpfs:
      - /tmp
      - /app/.cache
    cap_drop:
      - ALL
    cap_add:
      - NET_BIND_SERVICE          # only when binding a port below 1024
```

`read_only: true` makes every write fail, so each path the process writes at runtime gets a `tmpfs` entry or a volume. Pair it with a non-root `USER` in the Dockerfile (`references/dockerfile.md`); `cap_drop` does nothing for a process that is root on a writable filesystem.

## Secrets

A runtime credential reaches the container through the process environment at `up` time, and the Compose file names the variable with no value:

```yaml
services:
  app:
    environment:
      - API_KEY                  # taken from the environment `docker compose up` runs in
```

Where the repo wires an app-secrets injector, it wraps the compose command — ahead of `docker compose up`, in the dev alias or the command typed; the value is never typed into a file, a committed `.env`, or a shell history. A repo with no injector uses `env_file: .env` pointing at a gitignored file holding dev-only values.

A file-backed secret mounts at `/run/secrets/<name>` in plain Compose, no Swarm needed:

```yaml
secrets:
  db_password:
    file: ./secrets/db_password.txt   # gitignored
services:
  db:
    secrets: [db_password]
    environment:
      POSTGRES_PASSWORD_FILE: /run/secrets/db_password
```

An `ENV` instruction carrying a literal key, or an `ARG` used for one, lands the value in a layer that `docker history` prints; the same goes for a `COPY . .` over a tree whose `.dockerignore` misses `.env`.
