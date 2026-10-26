# Linking an account

```
  session                     the bank                   the holder's phone
   ├─ POST /auth ────────────────►│                              │
   │◄─ { "url": … } ──────────────┤                              │
   ├─ prints the url ─────────────┼─────────────────────────────►│  authorises (itsme / bank app)
   │◄─ redirect carrying ?code=… ────────────────────────────────┤  pastes it back
   ├─ POST /sessions { code } ───►│                              │
   │◄─ session_id + accounts[] ───┤                              │
```

- The redirect is fixed per environment, recorded per account under `redirect_url.<env>` in the register block; the holder hands back the whole URL it lands on, and nothing need listen there.
- The code is single-use and short-lived: a late paste exchanges for nothing → run the link again.

## Running it

- The exchange and the deep pull run in the same sitting (`api.md` § The two limits).
- A `valid_until` past the bank's `maximum_consent_validity` is refused, never clamped.

## An expired session

- Whether a renewal replaces the old session or leaves it behind is unexercised.
