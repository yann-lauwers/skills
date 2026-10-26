# The API

- Reference `https://enablebanking.com/docs/api/reference/`; base `https://api.enablebanking.com`.
- `api.tilisy.com` is a deprecated alias → never write it.
- `GET /sessions/{id}` with a live id and `DELETE /sessions/{id}` are unexercised.

## The JWT

- No API token: each request carries a JWT signed with the application's RSA private key, as `Authorization: Bearer <jwt>`; mint one per run, never cache it.

```json
{ "typ": "JWT", "alg": "RS256", "kid": "<application_id>" }
{ "iss": "enablebanking.com", "aud": "api.enablebanking.com", "iat": <now>, "exp": <now+ttl> }
```

- `iss` and `aud` are those two literals for every customer; the application id goes in `kid` and nowhere else.
- TTL ≤ 86400 s.
- `iat` in the future fails like an expired token → a 401 on a fresh token is a clock check before a key check.
- Nothing checks the key against the id: a key from one environment's item signing for the other's id answers a bare 401 → the item and the application id always name the same environment.
- `GET /application` is the cheapest call proving key, `kid` and clock at once.

## Sessions and accounts

- A pending authorisation is not addressable: the `sessionid` in `POST /auth`'s URL answers 404 on `/sessions/{id}` and `/auth/{id}` until the code is exchanged; the redirect's `code` is the only way back.
- An account's IBAN sits under `account_id.iban`, never at the root.
- `uid` addresses every later call and belongs to the session — a new link issues a new one, so it is stored beside the session, never in the entity file.

## Paging a statement

- `GET /accounts/{uid}/transactions` pages at 100 rows; pass `continuation_key` back until it is absent — the only pagination signal.
- Ask for `transaction_status=BOOK`; a pending row's amount and date still move.

## The transaction shape

- `transaction_amount.amount` is a string, unsigned, trailing zeros trimmed (`15`, `0.1`) → compare numerically; the direction lives only in `credit_debit_indicator` (`CRDT` / `DBIT`).
- `bank_transaction_code` is flat — `{ "description": "PMNT", "code": "ICDT", "sub_code": "ESCT" }`: domain, family, sub-family; the nested names the reference implies return nothing.
- `remittance_information` is an array of free-text lines.
- `entry_reference` is optional under PSD2 — null at some banks, unstable at others. Present → it is the `seq`; null → a derived one is stable only against a re-fetch of the same rows → fetch windows are contiguous, never overlapping.

## The two limits

- History collapses about an hour after the link: many banks drop from a year or more to 90 days → pull the full history in the same run as the link; every later run is incremental.
- A session expires at the `valid_until` the link asked for, capped by the bank's `maximum_consent_validity` from `GET /aspsps`; renewal is a new authorisation on the person's phone, never automatable.
- Both produce a short answer, never an error → a short fetch is checked against them before anything else.

## Errors

| Status | Means | Do |
| --- | --- | --- |
| 401 | JWT rejected | the item/environment pairing first, then the clock, `kid`, the key |
| 403 | the session doesn't reach that account | the account isn't whitelisted in the Control Panel |
| 429 | the bank's AIS cap, per account and endpoint, often four a day | back off; never retry in a loop |
