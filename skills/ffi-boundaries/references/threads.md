# Threads across the boundary

A callback runs on whichever core thread did the work — an IO read loop, a renderer, a timer —
whatever the caller's language believes about its isolation.

## Rules for a callback body

- Never block: copy what is needed and return.
- Touch UI state only on the UI thread, reached by an async dispatch, never a synchronous one.
- A callback firing per read or per frame hops at a bounded rate — one main-thread hop per few
  milliseconds — carrying the latest state, never one hop per event.
- Call back into the library only where the contract allows re-entry.

## Swift

State reaches a Swift callback only through `userdata` and `Unmanaged` — a C function pointer
captures no context — and the body follows the rules above:

```swift
let cb: @convention(c) (UnsafeMutableRawPointer?, UnsafePointer<UInt8>?, Int) -> Void = { ud, ptr, len in
    guard let ud, let ptr else { return }
    let sink = Unmanaged<Sink>.fromOpaque(ud).takeUnretainedValue()
    let bytes = Array(UnsafeBufferPointer(start: ptr, count: len))   // copy: ptr dies on return
    DispatchQueue.main.async { sink.consume(bytes) }
}
```

- `Sink` here is a `@MainActor final class`.
- A clean build never proves the body safe; what the Swift compiler checks on this seam →
  /swift-patterns .
