# Sendable and the escape hatches

## Rules that decide most diagnostics

- A value crossing isolation must be `Sendable`, or be transferred with `sending` and not used again
  by the sender ("sending 'x' risks causing data races").
- Region-based isolation lets a freshly created non-Sendable value move once; using it after the move
  errors.
- A global-actor-isolated class (`@MainActor final class`) is `Sendable`. A non-isolated
  `@Observable` class is not, and sending one to an actor errors.
- `Task { }` takes its closure as `sending`; capturing a non-Sendable parameter errors ("passing
  closure as a 'sending' parameter risks causing data races").
- A `@frozen public struct` of Sendable members is implicitly Sendable; a non-frozen public struct in
  a library-evolution module is not.

## The escape hatches, each with its obligation

| Hatch | Legitimate when | Carried by |
| --- | --- | --- |
| `@unchecked Sendable` | the type guards all mutable state with its own lock, or is immutable in fact | a lock-typed field (`Mutex<State>`) naming the state it guards |
| `nonisolated(unsafe) var` | a global or static that is genuinely synchronised another way | the synchronising type in its declaration |
| `nonisolated(unsafe) let` | never for a Sendable type — the compiler says "'nonisolated(unsafe)' is unnecessary"; use a plain `let` | — |
| `@preconcurrency import` | a module not yet annotated | a tracker ticket naming the import |
| `weak let` (Swift 6.3, SE-0481) | a `Sendable` class holding a weak reference to a `Sendable` referent — no hatch needed; `weak var` in the same class errors ("is mutable"), a non-Sendable referent still errors | — |
| `~Sendable` (Swift 6.4, SE-0518) | a base class that is non-Sendable on purpose; a subclass may still add `@unchecked Sendable` | the commit message |

A `static var` holding an atomic or a lock that is never reassigned should be a `static let`; the
`let` needs no hatch at all. An unprotected `static var` is an error in Swift 6.

## Warnings that should be errors

Several hazards this skill names are warnings in Swift 6 mode — an imported C callback touching
main-actor state, an `NSEvent` monitor closure, `DispatchQueue.global()` calling `@MainActor` code
— so a clean build proves less than it looks. Swift 6.4 prints a diagnostic group on each warning
(`[#ActorIsolatedCall]`, `[#RegionIsolation::SendingRisksDataRace]`, `[#MutableGlobalVariable]`,
`[#NoUseUnstructuredThrowingTask]`), and a group escalates per module with `-Werror <group>`
(SE-0443), Xcode's `SWIFT_WARNINGS_AS_ERRORS_GROUPS`, or SwiftPM's `.treatWarning(_:as:)`
(SE-0480); per declaration, `@diagnose(<group>, as: error, reason:)` (SE-0522, compiles on 6.4).
Promote `ActorIsolatedCall` to an error in every package that hosts a C callback or a GCD queue.
Whether that escalation reaches the imported-C-callback warning specifically is unmeasured.

An unassigned throwing `Task { }` warns on 6.4 (SE-0520, `NoUseUnstructuredThrowingTask`): the
error it throws is lost. Store the task or `try await` its value.

## Locks at a macOS 14 floor

| Lock | Availability | Use |
| --- | --- | --- |
| `Mutex`, `Atomic` (Synchronization) | **macOS 15** | not available at 14 |
| `OSAllocatedUnfairLock` | macOS 13 | the default at 14: `withLock { }`, state inside the lock |
| `NSLock` | always | fine inside an `@unchecked Sendable` class, with the fields it guards named |
| an `actor` | always | when callers can `await`; never for state a synchronous C callback must reach |

## Diagnostic → first check → smallest fix

| Diagnostic | First check | Smallest safe fix |
| --- | --- | --- |
| "main actor-isolated … cannot be used from a nonisolated context" | is the caller UI-bound? | isolate the caller, or `await MainActor.run { }` where main ownership is right |
| "actor-isolated type does not conform to protocol" | must the requirement run on the actor? | `extension T: @MainActor P`; `nonisolated` only for truly nonisolated requirements |
| "sending '…' risks causing data races" | which boundary is crossed? | keep access inside one isolation, or send an immutable value |
| "… cannot satisfy conformance requirement for a 'Sendable' type parameter" | does the conformance carry actor isolation? | remove it from the conformance, or keep the metatype on one side |
| "'Thread.current' is unavailable from asynchronous contexts" | debugging by thread? | a synchronous helper, or `MainActor.assertIsolated()` |

Adapted from AvdLee's Swift Concurrency skill (diagnostics table), corrected on Swift 6.4.
