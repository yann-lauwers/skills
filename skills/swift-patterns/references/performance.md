# Performance — instruments, and the costs already measured

Checked on Xcode 27.0 / macOS SDK 27.0 — the `OSSignposter`, `@inline(always)` and `@specialized`
compiled one per file (SKILL.md step 3); the Instruments facts come from the Xcode 27 release notes and
WWDC25 306. The costs below were measured on a SwiftUI and AppKit Mac app on macOS 27, a 120 Hz
display, `-O` builds. How to write views that re-run little: `swiftui-updates.md`.

## Signposts

`OSSignposter` is `Sendable`. `withIntervalSignpost("name") { … }` around
a synchronous region; `beginInterval` / `endInterval` with the returned state across an `await` or
a callback. Instruments 27 gives each signpost name its own track, so name intervals by the phase
they measure ("parse", "layout", "encode"), never by the function.

## Which instrument

| Question | Instrument |
| --- | --- |
| which executor ran what — cooperative pool, main actor, a custom executor | Swift Executors (Instruments 27) |
| where tasks and actors spend their time, per state | Swift Concurrency's task collection tracks and its per-state "Profile" call tree (27) |
| why a view body re-ran, and what it cost | the SwiftUI instrument (26): lanes for long view-body updates, long representable updates, layout-cache-miss reasons (27), and a cause-and-effect graph |
| what a log line coincided with | Time Profiler's os_log overlay (27) |
| a scripted, repeatable capture | `xctrace record --recording-options …` (27) |
| a main-thread block, and a frame delivered late | `--instrument Hangs --instrument Hitches` added to a Time Profiler recording |
| where the main thread spends a few seconds, with no trace | `sample <pid> <seconds>` |
| which `ForEach` in a lazy container takes the slow path | the launch argument `-LogForEachSlowPath YES` — /xcode-integration:swiftui-specialist , `references/foreach.md` § Diagnosing with `-LogForEachSlowPath` |

## Costs in Foundation and the standard library

- ISO 8601 parsing → a `static let` `Date.ISO8601FormatStyle(includingFractionalSeconds: true)`
  and `try style.parse(text)`: `Sendable`, no ICU. 355 468 timestamps took 65.6 s through
  `ISO8601DateFormatter` (about 185 µs a call) and 0.50 s through the style, which also accepts a
  timestamp with no fractional part.
- A `String` that came from Objective-C or `JSONSerialization` is a lazily bridged `NSString`, and
  Character work on it walks UTF-16 at about 9 MB/s → `makeContiguousUTF8()` once before splitting
  or scanning: 4.6 MB of output split in 0.11 s against 0.51 s. Decoding into Swift types with
  `JSONDecoder` avoids the bridge: 0.48 s against 1.48 s for 123 MB.
- Lines in a byte buffer → `memchr` inside `withUnsafeBytes`.
- The first word of a long text → `split(maxSplits: 1, whereSeparator: \.isWhitespace)` or a prefix
  scan; a whole split kept for its first element took 27.8 ms on one 227 000-character string.
- An inflected `AttributedString(localized:)` costs about 159 µs a phrase (50 µs uninflected, 10 µs
  for `String(localized:)`) → resolved once per key, count and locale, cached, and the cache
  flushed when `Locale.current` changes. Resolving runs off the main actor:
  `LocalizedStringResource` and `AttributedString` are `Sendable`, and 16 threads resolved 192 000
  phrases with 0 mismatches.
- Markdown that streams in → `AttributedString(markdown:options:)` with
  `appliesSourcePositionAttributes`, keeping every top-level block but the last two and
  re-parsing from the second-to-last block's start line; a text holding `]:` parses whole, and the
  finished text parses whole once. Over 8 918 streaming steps: 0 mismatches against a full
  parse, 20 when keeping all but the last block; 3.9× less parsing in total. Source columns count
  UTF-8 bytes.
- Independent per-line decoding of a large file → `withTaskGroup` over
  `min(lines.count, activeProcessorCount)` chunks, reassembled by chunk index, with the
  order-dependent assembly kept serial: 123 MB in 0.72 s wall against 1.62 s serial.
- Text measured for layout → Core Text (`CTTypesetter`, `CTLine`) built off the main actor and
  handed over with `sending`; layout objects serve one thread at a time, fonts any. 8.8 k
  characters took 1.75 ms against 4.49 ms for TextKit 2's `ensureLayout(for: documentRange)`; 107 k
  characters 6.07 ms against 36.4 ms, at equal heights.
- A large read-only text → a TextKit 2 `NSTextView` with `isHorizontallyResizable` false and a
  frame width from the longest line, measured off the main actor. A horizontally resizable one
  lays out the whole document: a 1 MB file's first frame took 411–1 220 ms against 9–16 ms.

## Optimizer control (Swift 6.4)

`@inline(always)` (SE-0496) and `@specialized(where T == …)` (SE-0460) each apply to one function
the profile named, never speculatively.
