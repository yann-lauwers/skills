# Volumes

Choosing how a path inside a container is backed. Read when adding a `volumes:` entry or when a bind mount has overwritten something the image built.

| Kind | Syntax | Backed by | Use for |
| --- | --- | --- | --- |
| named volume | `pgdata:/var/lib/postgresql/data` | Docker-managed, survives `down` | database data, anything that must outlive the container |
| bind mount | `./src:/app/src` | a host directory | source code in dev, for hot reload |
| anonymous volume | `/app/node_modules` | Docker-managed, per container | shielding a container-built path from a bind mount above it |

The trap is the third row. A bind mount of `.:/app` lays the host tree over the container's `/app`, host `node_modules` included — empty, or built for the wrong platform. An anonymous volume at `/app/node_modules` mounts after the bind and keeps the image's copy:

```yaml
services:
  app:
    volumes:
      - .:/app
      - /app/node_modules
      - /app/.next              # same shield for a build cache
```

Data written to a container path with no volume beneath it dies with the container. `docker compose down -v` removes named volumes too — it is the one form of `down` that deletes data.
