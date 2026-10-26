# Permission grants and signing (macOS)

- macOS keys each privacy grant — Accessibility, Screen Recording, Automation (Apple Events), Files and Folders, Microphone, Camera — to the code identity it was granted to: the signing team and bundle identifier for signed code, the code hash for ad hoc code.

## Ad hoc builds re-ask every build

- An ad hoc signature changes with every build → the app asks again for every grant after each rebuild.
- Builds run repeatedly on one machine → sign with a personal identity from a local, git-ignored xcconfig the project reads (`CODE_SIGN_IDENTITY`, `DEVELOPMENT_TEAM`); a free Apple ID gives an `Apple Development` identity.
- Name the identity only in that file → a target that sets its own signing beats the file.
- The file lives in one checkout → a worktree without its own copy builds ad hoc.
- Installing an ad hoc build over an installed copy signed with a stable identity → drops every grant that copy held.
- Grants are keyed to the installed path too → renaming the bundle folder asks again.

## Who needs the grant

- The process doing the reading needs it: an accessibility-tree check → the grant on the process that launched it, the terminal, not the app under test · an external capture → Screen Recording on the capturing process · an app photographing its own frame → none.
- A grant is the owner's click in System Settings → stop and name the service and the binary path that needs it.
- `tccutil reset <service> [bundle-id]` removes grants and never adds one.

## Reading what a build carries

```sh
codesign -dv --verbose=4 <App.app>             # identity, team, hash, runtime flags
codesign -d --entitlements - <App.app>         # entitlements as signed
codesign --verify --deep --strict <App.app>    # signature integrity
spctl -a -vv <App.app>                         # Gatekeeper's verdict
```

- Hardened runtime is required for notarization; the sandbox and `com.apple.security.*` entitlements change what the app may touch.
- A behaviour difference between a local build and a distributed one → an entitlement or runtime-flag difference until `codesign -d` shows otherwise.

## Distribution

- Notarization applies to what leaves the machine: `xcrun notarytool submit … --wait`, then `xcrun stapler staple`.
- A local verification loop never needs it.
