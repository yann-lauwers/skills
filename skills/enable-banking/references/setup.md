# Setup — everything before the first call

## Two applications, sharing nothing

- Sandbox and Production are separate registrations, each with its own `application_id`; the setup runs twice and produces two key pairs, two ids, two secrets-store items.

| | Sandbox | Production |
| --- | --- | --- |
| Reaches | the ASPSPs' sandboxes; for Belgium only BBVA and Mock ASPSP | the real banks |
| Activation | automatic | the provider's review |
| Extra fields | — | description, GDPR email, privacy URL, terms URL |
| Payment initiation | granted automatically | not registered |

- A sandbox link can return the account's real transactions → a sandbox statement is real financial data: sessions and non-production statements are never committed.
- Restricted production is a state, not an environment: the application registers as Production, and step 4's whitelist restricts its reach.

## The steps

1. The user creates the account at `https://enablebanking.com` and opens the Control Panel.
2. The user generates the key pair — § The key. Done when `~/eb-<env>-private.key` and `~/eb-<env>-public.crt` exist.
3. The user registers the application: its name, GDPR email their own, the environment's redirect URL (the register block's `redirect_url.<env>`; production refuses `localhost`). Done when it has an `application_id`.
4. The user whitelists each account by IBAN (production only). An account left off authorises, redirects, then vanishes from the session's account list → read a missing account as a Control Panel omission before suspecting the bank.
5. The key reaches the secrets store — § Adding the key to the secrets store.
6. Write the register block: `applications.<env>.application_id` and `.secret` (step 5's title), then per account `accounts.<account>` — `aspsp.<env>` (§ Which bank to name), `country`, `psu_type`, `redirect_url.<env>`. Done when step 7 resolves the application from it.
7. Prove the credential with `GET /application` (`api.md` § The JWT), signed with the environment's injected key, `kid` its application id. Done when the application record prints.
8. Link an account per `authorisation.md`; the holder authorises on their phone. Done when the session exists and the deep pull ran.

- `psu_type` and country are per-request values on `POST /auth`, never registration fields.

## The key

- Take "Generate outside the browser and import public certificate"; the browser route drops the private key into Downloads in cleartext.

```sh
openssl genrsa -out ~/eb-production-private.key 4096
chmod 600 ~/eb-production-private.key
openssl req -new -x509 -days 365 -key ~/eb-production-private.key \
  -out ~/eb-production-public.crt -subj "/O=<application name>/CN=<application name>"
```

- `sandbox` in place of `production` for the second application; the form imports the `.crt`.
- OpenSSL 3.x writes PKCS#8 (`BEGIN PRIVATE KEY`), 1.x PKCS#1 (`BEGIN RSA PRIVATE KEY`); both sign.
- The certificate expires after 365 days with no warning → re-check it a year on.
- The provider never holds the private key → it reaches the secrets store before anything else, never a repo.

## Which bank to name

- `aspsp.name` is the provider's own string → take it from `GET /aspsps?country=BE`, never the marketing name.
- A retail brand resolves under its parent bank's name.

## Adding the key to the secrets store

- One item per application, `<entity>-enable-banking-production` and `<entity>-enable-banking-sandbox`, the key in the `password` field.
- Never write these items: hand the user the item spec the secrets store's skill describes — the whole private key file, header and footer included, pasted from the clipboard.
- Never `cat` the key; read back its length:

```sh
keyless run -s EB_KEY=<ENTITY>_ENABLE_BANKING_PRODUCTION -- python3 -c 'import os;print(len(os.environ["EB_KEY"]))'
```

- A 4096-bit key reads a few thousand characters.
- Then delete the local `.key`; the `.crt` stays.
