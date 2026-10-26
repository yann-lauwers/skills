# Isolation

Checked on Swift 6.4 (Xcode 27.0) at a macOS 14 target unless a row says otherwise.

## Where code runs

| Code | Runs on | Note |
| --- | --- | --- |
| `Task { }` started from `@MainActor` code | the main actor | inherits the caller's isolation |
| `Task.detached { }` | the global executor | sheds isolation and priority; main-actor calls inside need `await` |
| `Task { @concurrent in }` | the global executor | the explicit way to start off-main |
| `nonisolated func f() async` | **the global executor**, unless `NonisolatedNonsendingByDefault` (or Approachable Concurrency) is on — then the caller's actor | the single most-misquoted rule: "Swift 6.2 runs async on the caller" holds only with the feature |
| `@concurrent func f() async` | the global executor | allowed on a member of a `@MainActor` class, which it then stops touching; `@MainActor @concurrent` together is rejected |

A runtime run showed a `nonisolated async` method called from the main actor running off the main
thread without the feature and on it with the feature — the difference is behaviour, not only
diagnostics.

## Keeping the main actor free

- A target on the main actor draws; decoding, file I/O, waiting on a process, serving a socket and work whose cost grows with its input run off it — in a `@concurrent` function or on an actor of the side that works — and the main actor receives the result.
- A `.task` in a main-actor view runs on the main actor: a synchronous decode or parse inside it holds the frame.
- Text that streams in is parsed off the main actor, once per version — never in `body`, which re-runs on every partial and re-parses the whole text each time.
- A pure fold over a long list (a reopened history into rows) is a value type run off the main actor, and the main actor assigns its result in one write.
- Streamed updates are coalesced before they reach the main actor.
- Work that keeps state between updates — caches, a pending change — is an actor owning a value type
  that holds the logic: the value type is tested synchronously, and the actor serialises and holds
  the state (WWDC25 268).
- A producer faster than the main actor's apply hands over by pull: the worker merges each update
  into one pending change and yields a nudge into an `AsyncStream` made with
  `.bufferingNewest(1)`; the main-actor loop awaits the nudge and takes the merged change. With a
  40 ms apply against updates 5 ms apart, pull finished 42 ms after the producer; an unbounded
  stream of changes fell 6.8 s behind, and `.bufferingNewest(1)` over the changes themselves
  dropped rows and ended on a wrong screen.
- An event source with several subscribers hands each its own stream with its own bounded buffer,
  filtered to that subscriber's slice before the main actor; two loops over one stream split its
  elements between them, and every single-subscriber test passes. The source yields without
  awaiting a subscriber, and each event carries a sequence number: a subscriber that sees a gap —
  its oldest events dropped by `.bufferingNewest` — re-reads a snapshot from the source.
- A SwiftLint `custom_rules` entry scoped by `included:` to the main-actor targets, at `severity: error`, bans the blocking calls there; an exemption is a `// swiftlint:disable:next` naming its reason.

## Conformances

- `extension Model: @MainActor Exportable` compiles in plain Swift 6 — no feature flag. Using it from
  a nonisolated context errors: "main actor-isolated conformance … cannot be used in nonisolated
  context".
- Under default MainActor isolation a plain conformance is inferred isolated — except where the
  protocol inherits `SendableMetatype` (`CodingKey`, through `Sendable`), which infers a
  `nonisolated` conformance (SE-0466, amendment). SE-0478's file-scope `default nonisolated` is
  accepted and not implemented in 6.4: do not write it.
- A global-actor-isolated conformance cannot satisfy a `Sendable` type-parameter requirement
  (`SendableMetatype`): remove the isolation from the conformance, or stop passing the metatype
  across isolation.
- Conforming to a `@MainActor` protocol on the **primary declaration** makes the type main-actor;
  conforming in an extension isolates only that extension.

## Actor reentrancy

Every `await` inside an actor is a point where other callers run. Read-then-await-then-write loses
updates: two concurrent `deposit(100)` with a suspension between read and write logged
`[100, 200, 210, 220]`. Read state again after the `await`, or deduplicate in-flight work:

```swift
actor Cache {
    private var inFlight: [String: Task<Data, Error>] = [:]
    func value(for key: String) async throws -> Data {
        if let task = inFlight[key] { return try await task.value }
        let task = Task { try await download(key) }
        inFlight[key] = task
        defer { inFlight[key] = nil }
        return try await task.value
    }
}
```

A force-unwrap of actor state after an `await` is a latent crash for the same reason.

## Capturing the caller's isolation

A `Task` inside a function that takes `isolation: isolated (any Actor)? = #isolation` inherits it
only if the closure uses it — write `_ = isolation` inside; a capture list alone still errors.

## `deinit`

- A nonisolated `deinit` of a `@MainActor` class cannot touch non-Sendable state (an `NSEvent`
  monitor token is `Any?`, so it cannot be removed there).
- `isolated deinit` fixes that and compiles at a macOS 14 target for a `@MainActor` class — the
  compiler weak-links a back-deployment shim (`swift_task_deinitOnExecutorMainActorBackDeploy`).
  Running it on a real macOS 14 host is unverified here; test it there before relying on it.
- Cancelling a stored `Task` from a plain `deinit` is fine.
