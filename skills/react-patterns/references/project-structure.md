# Project structure

Where a file goes and which way imports point in a React app. Read when creating a file, a feature folder, a provider, an API client, an env read or a permission check. A repo's existing layout and naming win; this is the default where a repo or a feature has none.

## Layout

- Feature folders: `modules/{feature}/{components,hooks,api}/`, tests in `modules/{feature}/__tests__/`.
- Dependencies run shared → features → app; a feature never imports from another feature.
- Imports name the file, never a barrel — /react-performance , `references/bundle-size.md`.
- Absolute imports (`@/*`), never `../../../`; kebab-case file and folder names, component files included (`user-card.tsx`).

## Shared pieces

- One internal wrapper per third-party UI component; features import the wrapper, never the vendor.
- One `provider.tsx` composes every global provider.
- `lib/` holds configured instances — API client, auth, analytics — never raw re-exports.
- Env goes through a Zod-validated `config/env.ts`; nothing reads `process.env` directly.
- Permissions are centralized `canX` functions; no inline role strings.
