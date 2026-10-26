# Testing

## Swift Testing first

- `import Testing`, `@Test("sentence")`, `#expect`, `#require`, parameterised `@Test(arguments:)`.
- Async code: `await` directly in the test; callback APIs with `confirmation { }`. Never a sleep as
  synchronisation.
- `.serialized` on a suite runs its test functions and sub-suites one at a time (not only its
  parameterised tests), per the swift-testing source.
- Expected errors: `#expect(throws: MyError.self) { try f() }`; an `Equatable` error value works too.
  Since 6.1 the call returns the thrown error, so its fields can be inspected.

## Since Swift 6.1

The surface above is Swift 6.0's. What arrived since (proposal status lines in
swiftlang/swift-evolution `proposals/testing`; each name compiled on Swift 6.4 and checked against
Apple's Testing documentation):

| Swift | What |
| --- | --- |
| 6.1 | `confirmation(expectedCount: 1...)` ranged counts (ST-0005); per-test setup and teardown through a `TestScoping` trait (ST-0007) |
| 6.2 / 6.3 | exit tests — `#expect(processExitsWith: .failure) { … }` is how a trap such as `preconditionIsolated` off main is tested, with value capture into the child (ST-0008, ST-0012); a captured local spells its type: `[code = code as Int32]` |
| 6.2 / 6.3 | attachments — `Attachment.record(…)`, images included, for a screenshot of a drawn view (ST-0009, ST-0014, ST-0017) |
| 6.3 | `Issue.record(_:severity: .warning)` (ST-0013); `try Test.cancel(_:)` (ST-0016) |
| 6.4 | XCTest ↔ Swift Testing interop: `#expect` inside an `XCTestCase` and `XCTAssert` inside a `@Test` both report issues (ST-0021). A package at tools-version 6.4 or later runs `complete` mode, where every issue keeps its own severity; below 6.4 it runs `limited`, where the other library's issues are warnings. `SWIFT_TESTING_XCTEST_INTEROP_MODE` overrides it |
| 6.4 | `Transferable` attachments through `try await Attachment(exporting: value, as:, named:)`, macOS 15.2 (ST-0023); `swift test --maximum-repetitions N --repeat-until pass|fail` repeats one test case (ST-0024) |

Xcode 27 adds a test-plan setting for how a crash of the target app is graded (off, warning,
failure, fatal); the VoiceOver-driving UI-test service is `accessibility.md` § Proving it.

## Isolation in tests

Test targets have their own `SWIFT_VERSION`, strict level and Approachable Concurrency setting —
read them (`toolchain-and-modes.md`); a test target in Swift 5 mode with Approachable Concurrency on
behaves differently from the app target it tests. Mark a test `@MainActor` when it touches main-actor
code rather than hopping inside it.

## Doubles

Mock only boundaries — file system, network, clock, a C library. A mock with mutable state touched
from more than one isolation domain is itself a race: guard it with a lock, or make it an actor. A
mock declared `@unchecked Sendable` over bare `var`s hides exactly the bug the test exists to catch.

## Race detection

Run the suite under Thread Sanitizer (`xcodebuild test -enableThreadSanitizer YES`) when a change
touches threads, callbacks or locks; Address Sanitizer (`-enableAddressSanitizer YES`) when it
touches `Unmanaged` or C buffers.

## Triage of a red run

Classify before fixing: a compile failure in the test target, an assertion failure, a crash (read the
trap — an isolation trap names the executor), a timeout, or flakiness — rerun with `swift test
--maximum-repetitions 20 --repeat-until fail` (Swift 6.4) or Xcode's Test Repetition Mode, which
now repeats individual Swift Testing cases; a single rerun proves nothing. Adapted from OpenAI's
build-macos-apps `test-triage`.
