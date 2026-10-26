# Measuring launch, window and frame time

- A native performance criterion is a number taken the same way before and after the change; one run is an anecdote, never a reading.

## The method

1. Define the span → cold launch to first frame · a window opened from a resident app · a keystroke to its drawn result · a frame's work. Cold and warm are different spans with different budgets.
2. Repeat → report the median and the worst over a fixed count, twenty launches as a floor for launch spans; never a mean over a handful.
3. Record the machine beside each number → load, thermal state, other apps running, power source.
4. Keep the record → each reading names the build it was taken on (`build-graph.md`, step 2 of § Prove the launched build holds the change).
   - A dispatched agent writes no record: every reading goes in its return.
   - The session that lands the change files it where the repo records its numbers, or in its own reply where the repo records none.
   - A number never outlives the build that produced it.
5. Same method after → the second reading uses the identical command and count; a change that does not improve the reading past the spread between runs is reverted by the party that took the reading, never kept on theory.

## Instruments from the command line

```sh
xcrun xctrace record --template 'App Launch' --launch -- <App.app/Contents/MacOS/Exe>
xcrun xctrace record --template 'Time Profiler' --attach <pid> --time-limit 10s
xcrun xctrace list templates    # Animation Hitches, Leaks, CPU Profiler, …
```

- App-defined spans → `os_signpost` intervals, visible in the same trace.

## Counting work, not only time

- The app can report the work a frame did — rows redrawn, layout passes, bytes written → assert on that count beside the time.

## A slow surface with no known cause

- Baseline first, locate the cost — core, shell, or the OS between them — change one thing, and re-measure with the same method.
