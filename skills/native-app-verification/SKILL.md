---
name: native-app-verification
description: "Proves a native desktop app change on a launched build when there is no browser — the build contains the change, an isolated instance that cannot touch the owner's, evidence from the accessibility tree or pixels, OS permission grants. Use on 'the app isn't picking up the change', 'launch it isolated', 'screenshot the app', 'prove it in the running app', or xcodebuild, zig build, a .app bundle, TCC, a menu-bar app. Not for a web page — the browser skills; not for writing the Swift, Zig or Rust — the language skill."
metadata:
  sources: >-
    Mechanisms abstracted from a Ghostty-fork macOS app's build and test docs;
    Windows reference adapted from https://github.com/affaan-m/ECC/blob/main/skills/windows-desktop-e2e/SKILL.md
---

# Native App Verification

Gets evidence out of a native desktop app an agent cannot see: the build, the instance, the reader, the grant, the timing.

- A native change is proven on a launched instance or not at all → a green unit suite never stands in for a window, a menu bar or a permission prompt.

## Before acting

1. Read the repo's own canon first → its build and test docs name the real commands, paths and instance variables; this skill names the mechanisms they instantiate.
2. Match the work, a review included, against the routing table; read the matched reference, then act.
3. Invoke the language skill § The stack's language skill names.

## Routing table

| Intent | Read |
| --- | --- |
| IF building, or judging a change from a build — "rebuilt and nothing changed", two toolchains, a prebuilt framework, a hermetic build | THEN `references/build-graph.md` |
| IF launching an instance to test — isolation, a copy beside the owner's, killing one, one check per instance | THEN `references/isolation.md` |
| IF reading or driving the running app — control surface, accessibility tree, screenshots, an empty tree, a capture that proves nothing | THEN `references/observation.md` |
| IF the app is a Windows native app (WPF, WinForms, Win32, Qt) | THEN `references/observation-windows.md` |
| IF a permission, signing identity or entitlement is involved — grants lost after a rebuild, screen recording, accessibility, automation | THEN `references/grants-and-signing.md` |
| IF the criterion is a time — launch, window open, frame, keystroke latency | THEN `references/measuring.md` |
| IF the repo's canon keeps this agent from launching an instance | THEN `references/when-an-agent-may-not-launch.md` |
| IF the request matches none of the above | THEN route to the closest-matching row — `references/observation.md` where none is close — name it in the reply |

## The stack's language skill

- Decided by what the repo carries, never by the request's words → invoke by name; a name-only listing entry still resolves.

| The repo carries | Invoke |
| --- | --- |
| `build.zig` | the repo's own Zig skill, found in `.claude/skills/*/SKILL.md`; none → the standard library of the version `build.zig.zon` pins (`zig env` prints `lib_dir`), never a recalled one, and report the absence |
| `*.xcodeproj`, `Package.swift`, or Swift sources | /swift-patterns |
| a C header two languages share, or any exported symbol | /ffi-boundaries , when the change touches it |
| `Cargo.toml`, `src-tauri/`, `CMakeLists.txt`, or anything else | no user-level skill yet → the repo's own canon plus the vendor's own docs; report the absence as a finding |

## Non-negotiables

1. A build that may not contain the change is never judged — measured, driven or captured — before its freshness is proven, per `references/build-graph.md`.
2. Never drive an instance the owner is using → every test instance runs isolated and is killed by the pid it reported; on a machine a person is using it is never activated, while inside a virtual machine the repo's canon launches into it may take that machine's front.
3. A repo whose canon limits who launches an instance wins → only that party launches, per § When an agent may not launch.
4. A reading that cannot tell "absent" from "could not read" is not evidence → a one-element accessibility tree, a capture of a backgrounded window, a blank screenshot prove nothing until the reader is proven to see.
5. Evidence is re-runnable → the command, the instance's run directory and the capture path travel with every claim.
6. Never move, resize, hide, minimise or quit another app's window, nor uncover the instance by any route → a criterion that holds only while the instance is visible or focused runs in the virtual machine the repo's canon launches into, where one exists; with none, it is proved below the window, and its on-screen leg goes to the owner as unproved.

## When an agent may not launch

- A repo's canon keeps a dispatched agent — builder, prover, reviewer — from launching an instance → `references/when-an-agent-may-not-launch.md`.
