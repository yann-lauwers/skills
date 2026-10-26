---
name: docker-patterns
description: "Writes or fixes a Dockerfile or Compose service — adding a service to a stack, volumes and networks, multi-stage builds, dropping privileges, keeping a secret out of the image, a container that will not start or reach its neighbour. Use on 'write a Dockerfile', 'add this to docker compose', 'the container can't reach the database', 'the image is huge', or `Dockerfile`, `compose.yaml`, `depends_on`, `healthcheck`, a bind mount, `.dockerignore`, `docker build`."
metadata:
  origin: ECC
  source: https://github.com/affaan-m/ECC/blob/main/skills/docker-patterns/SKILL.md
  note: partial import — drops the source's "Hardened CLI Installer Harnesses" section, which is ECC's own plugin-installer test infrastructure
---

# Docker Patterns

Router over the Dockerfile and Compose shapes this estate builds against. Three premises hold across every reference and are stated once here: a container is disposable, so anything that must outlive it sits in a volume and the image pins its base tag rather than riding `:latest`; a service reaches a neighbour by its Compose service name, and `depends_on` alone waits for the neighbour to *start*, never for it to be *ready* — readiness is a `healthcheck` plus `condition: service_healthy`; and a stack that serves ports is a dev server, started in the foreground where the repo starts its dev servers — its worktrunk dev alias where it has one — never detached with `-d`.

## Routing table

| Intent | Read |
| --- | --- |
| IF adding a service to a stack, wiring `depends_on`, or splitting dev settings from prod | THEN `references/compose-stack.md` |
| IF writing a Dockerfile, cutting an image down, or deciding what the build context carries | THEN `references/dockerfile.md` |
| IF choosing between a named volume, a bind mount and an anonymous volume, or a bind mount clobbers container-built files | THEN `references/volumes.md` |
| IF one service cannot reach another, or a port is exposed wider than it should be | THEN `references/networking.md` |
| IF dropping privileges, locking the filesystem, or getting a secret into a container | THEN `references/security.md` |
| IF a container will not start, exits at once, or the stack has to be rebuilt or torn down | THEN `references/debugging.md` |
| IF the request matches none of the above | THEN `references/compose-stack.md`, say which row was closest |

## Done when

The file in hand builds, the production stage runs as a non-root user with its state in a named volume, every dependant whose upstream carries a healthcheck waits on `service_healthy`, and no secret sits in the image, the Compose file or a committed `.env`.
