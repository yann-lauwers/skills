# Compose stack

Adding a service to a local stack, making one wait for another, and keeping dev-only settings out of the production file. Read when editing `compose.yaml` or one of its overrides.

## The shape of a service that waits correctly

```yaml
services:
  app:
    build:
      context: .
      target: dev                     # the dev stage of the multi-stage Dockerfile
    ports:
      - "3000:3000"
    volumes:
      - .:/app                        # bind mount for hot reload
      - /app/node_modules             # anonymous volume — keeps the container's deps
    environment:
      - DATABASE_URL=postgres://postgres:postgres@db:5432/app_dev
      - NODE_ENV=development
    depends_on:
      db:
        condition: service_healthy    # waits for the healthcheck, not the process
    command: npm run dev

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: app_dev
    volumes:
      - pgdata:/var/lib/postgresql/data
      - ./scripts/init-db.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 3s
      retries: 5

volumes:
  pgdata:
```

`depends_on: [db]` with no condition starts `app` the moment the `db` process exists, and the first migration lands on a database still initialising. A service with no healthcheck of its own gets `condition: service_started`, which says only that the process is up.

Local email lands in `axllent/mailpit:v1.31` (SMTP on 1025, web UI on 8025) rather than a real provider.

## Dev and prod overrides

`docker-compose.override.yml` is loaded on every bare `docker compose up`, so dev-only settings — a yann:debugger port, `DEBUG=app:*` — go there and never reach a file named explicitly. Production is a second file named on the command line:

```yaml
# docker-compose.prod.yml
services:
  app:
    build:
      target: production
    restart: always
    deploy:
      resources:
        limits:
          cpus: "1.0"
          memory: 512M
```

```bash
docker compose up                                                        # dev, override auto-loaded
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d    # prod files, explicit
```

A stack that binds host ports is a dev server: it runs in the foreground, no `-d`, so the process that owns its ports is the one you can stop. Where the repo has a worktrunk dev alias, the stack is that alias's command.

Compose stands in for an orchestrator only locally: a production multi-container workload runs under Kubernetes, ECS or Swarm, where restart, placement and secrets are the platform's.
