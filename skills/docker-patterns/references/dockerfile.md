# Dockerfile

Writing a Dockerfile, shrinking the image, and bounding what the build sends to the daemon. Read when editing a `Dockerfile` or a `.dockerignore`.

## Multi-stage: one file, a dev target and a production target

```dockerfile
FROM node:22-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

FROM node:22-alpine AS dev                # hot reload, debug tools; Compose builds `target: dev`
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
EXPOSE 3000
CMD ["npm", "run", "dev"]

FROM node:22-alpine AS build
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build && npm prune --omit=dev

FROM node:22.12-alpine3.20 AS production
WORKDIR /app
RUN addgroup -g 1001 -S appgroup && adduser -S appuser -u 1001
USER appuser
COPY --from=build --chown=appuser:appgroup /app/dist ./dist
COPY --from=build --chown=appuser:appgroup /app/node_modules ./node_modules
COPY --from=build --chown=appuser:appgroup /app/package.json ./
ENV NODE_ENV=production
EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=3s CMD wget -qO- http://localhost:3000/health || exit 1
CMD ["node", "dist/server.js"]
```

The `deps` stage copies only the manifests before `npm ci`, so a source edit reuses the cached layer; copying `.` first invalidates the install on every change. The production stage copies from `build` and carries no compiler, no dev dependency and no source. `USER` comes before the `COPY --chown` lines so nothing lands root-owned.

The examples pin to a major (`node:22-alpine`); the production stage pins to an exact tag (`node:22.12-alpine3.20`), since a rebuild on another day is otherwise a different image. `:latest` is never a base.

## `.dockerignore`

The build context is sent whole to the daemon and `COPY . .` copies all of it, so the ignore file decides both build time and what a layer can leak:

```
node_modules
.git
.env
.env.*
dist
coverage
*.log
.next
.cache
docker-compose*.yml
Dockerfile*
```

`.env` is the line that matters: without it a `COPY . .` bakes every local secret into a layer that `docker history` reads back.

