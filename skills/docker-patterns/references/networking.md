# Networking

One service reaching another, and which ports leave the Docker network. Read when a connection string is being written, a service cannot reach its neighbour, or a `ports:` line is added.

Every service on the same Compose network resolves by service name: from `app`, the database is `db:5432` whatever port it maps to the host, and a `redis` service, where the stack has one, is `redis:6379`. `localhost` inside a container is that container alone.

## Segmenting with named networks

```yaml
services:
  frontend:
    networks: [frontend-net]
  api:
    networks: [frontend-net, backend-net]
  db:
    networks: [backend-net]         # reachable from api, never from frontend

networks:
  frontend-net:
  backend-net:
```

## Exposing only what the host needs

```yaml
services:
  db:
    ports:
      - "127.0.0.1:5432:5432"      # host only
```

A bare `"5432:5432"` binds `0.0.0.0`, and Docker's own iptables rules sit in front of a host firewall such as ufw, so the port is open to the network whatever the firewall says. In production the `ports:` block is omitted entirely and the service is reachable only from its network.

## When a service cannot reach its neighbour

```bash
docker compose exec app nslookup db                       # name resolves → same network
docker compose exec app wget -qO- http://api:3000/health  # port answers → app is listening on 0.0.0.0, not 127.0.0.1
docker network inspect <project>_default                   # who is attached
```

A name that does not resolve means the two services share no network. A name that resolves and a port that refuses means the target binds `127.0.0.1` inside its own container, or is not up yet — see `references/compose-stack.md` for readiness.
