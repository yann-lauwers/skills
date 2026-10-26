# Debugging

A container that will not start or exits at once, a stack that has to be rebuilt, and what tearing it down deletes. Read when a service is red in `docker compose ps`, or before a rebuild or a `down`.

```bash
docker compose ps                        # which service is restarting or exited
docker compose logs --tail=50 app        # its last lines; -f to follow
docker compose exec app sh              # a shell in a running one
docker compose run --rm app sh          # a shell in one that will not stay up — a fresh container, no restart loop
docker compose exec db psql -U postgres
```

An exit code 137 is the kernel's OOM kill — raise `deploy.resources.limits.memory` or find the leak; 139 is a segfault, usually a native module built for the host's platform through a bind mount (`references/volumes.md`). A `restart: always` service that dies at once loops silently, so its logs are read with `--tail`, never `-f` alone.

A neighbour it cannot reach is `references/networking.md`.

## Rebuilding

```bash
docker compose build                   # rebuild what changed; then restart the stack
docker compose build --no-cache app    # discard every cached layer for one service
```

Starting the stack again is `references/compose-stack.md`'s foreground form.

`--no-cache` is the answer to a stale layer only after `references/dockerfile.md`'s layer order has been checked; a Dockerfile that copies `.` before installing rebuilds from scratch on every edit anyway.

## Tearing down

```bash
docker compose down        # containers and networks; volumes stay
docker compose down -v     # volumes too — the database is gone
docker system prune        # dangling images and stopped containers, every project on the machine
```

`down -v` is the only routine command here that destroys data; name what it will delete before running it on a stack someone else may be using.
