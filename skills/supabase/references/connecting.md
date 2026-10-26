# Connecting to the database

## Three endpoints, one database

| Endpoint | Reaches it over | Use for |
| --- | --- | --- |
| Direct | IPv6 only, unless the paid dedicated-IPv4 add-on is enabled | A network with working IPv6 |
| Shared pooler, session mode, port 5432 | IPv4 and IPv6 | A persistent client on an IPv4-only network |
| Shared pooler, transaction mode, port 6543 | IPv4 and IPv6 | Serverless and edge functions |

- An IPv4-only network → the shared pooler, never the dedicated-IPv4 add-on.

## Reading the endpoint off the string

| | Host | Username |
| --- | --- | --- |
| Direct | `db.<project-ref>.supabase.co` | `postgres` |
| Pooler | `<region-shard>.pooler.supabase.com` | `postgres.<project-ref>` |

- The username is the reliable field: a dot and the project ref → a pooler string; plain `postgres` against a pooler host fails authentication.
- The region shard is `aws-N-<region>`; several resolve per region and only the project's own accepts its credentials → probe each with the project's password.

## No route to host

- `No route to host` is a network verdict → run both checks before touching the credential:

```
curl -6 -s -o /dev/null -w '%{http_code}\n' --max-time 8 https://ifconfig.co   # 000 = no IPv6 route
dig +short db.<project-ref>.supabase.co A                                       # empty = IPv6-only host
```

- No IPv6 route plus a host with no A record → the direct endpoint is unreachable from here: switch to the pooler, never reset the credential.

## Session or transaction mode

- A client whose row-level policies read a setting applied inside the transaction → session mode on 5432: transaction pooling drops that state and the policies filter everything out, which looks like a broken policy.
