# Robustness

- A hook sits on the critical path of every tool call: it never crashes, never hangs, never corrupts shared state and never grows without bound.

## Fail-open is an invariant, not an `except` clause

- A hook that raises lets the action through — exit 1 is non-blocking (`events-and-contracts.md` § Output) — so every guard keeps running on every payload shape.

### Coerce at the entry point

- `(x or {}).get(...)` guards `None` and nothing else; coerce every payload field once, at the entry point:

```python
def s(v, default=""):
    """A payload field that MUST be a string. Non-str → default, never a crash."""
    return v if isinstance(v, str) else default


def d(v):
    """A payload field that MUST be a mapping. Non-dict → {}."""
    return v if isinstance(v, dict) else {}


tool  = s(data.get("tool_name"))
ti    = d(data.get("tool_input"))
cmd   = s(ti.get("command"))
fpath = s(ti.get("file_path"))
cwd   = s(data.get("cwd")) or os.getcwd()
```

- Never wrap the entry point in a blanket `try/except: sys.exit(0)`: it turns a crash into a silent skip, while coercion keeps the guard running and is the only version a test can assert on — `deny` on `{"file_path": ["/etc/passwd"]}`.
- Validate shape at every depth read, never only at the top level.

### Fail-open at each risky site, annotated

- Wrap each risky site on its own and annotate it with why it fails open — the shape is `rollout.md` § Logging must never change the verdict.
- Decide each helper's safe direction and assert it; a helper meant to fail open never fails closed.

## Cost

- A hook that hangs is a hook that is not running, and it is invisible — no error, no output, indistinguishable from a slow tool.
- Pattern cost → `trigger-design.md` § Cost is a correctness property.
- Only a separate process bounds a long regex call — a signal handler waits until the C call returns — so a timing harness forks:

```python
def timed(pattern, flags, fn_name, subject, cap=90.0):
    r, w = os.pipe()
    if os.fork() == 0:
        os.close(r)
        try:
            rx = re.compile(pattern, flags)
            f = {"search": rx.search, "match": rx.match, "findall": rx.findall}[fn_name]
            t0 = time.perf_counter(); f(subject); dt = time.perf_counter() - t0
            os.write(w, ("%.6f" % dt).encode())
        except Exception as e:
            os.write(w, ("ERR:" + type(e).__name__).encode())
        finally:
            os.close(w); os._exit(0)
    # parent: select with a deadline, SIGKILL on timeout
```

- Exercise each pattern with the function production calls: anchored `match` and unanchored `search` differ by orders of magnitude.
- Assert the shape of the cost curve, never an absolute second count: time at 2N stays under ~3× time at N.
- Import anything not needed on the common path inside the function that needs it: import cost is paid on every invocation.
- Measure an A/B interleaved, alternating A and B, never A-then-B.
- A floor-cost figure is a claim about a moment: re-measure it before building on it, and distrust any sentence saying no code change removes it.

## Concurrency

- Every subagent inherits the parent's session id, so all session-scoped state is shared at fan-out concurrency — the normal condition of any session that dispatches workers.
- A hook fires on the tool call whether or not the shell executes the command.
- `agent_id` can be missing from a subagent-stop payload that carries `agent_type`; never key identity on `agent_id` alone.
- Treat every child's activity as parent state: a child's probe is a write to the parent's store.
- Validate the shape of an extracted identifier before persisting it: an obligation keyed on a value that never recurs can never be discharged; rejecting shell metacharacters is not validation.

### Atomic value write

```python
tmp = "%s.tmp.%d" % (path, os.getpid())      # pid so two writers cannot collide
with open(tmp, "w") as fh:
    json.dump(obj, fh)
os.replace(tmp, path)                        # atomic on POSIX: readers see old or new
```

### Bounded exclusive lock, degrading to unlocked

```python
deadline = time.time() + 2.0
while True:
    try:
        fcntl.flock(fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        break
    except BlockingIOError:
        if time.time() > deadline:
            break            # proceed UNLOCKED — the pre-lock behaviour: degraded, never stuck
        time.sleep(0.005)
    except Exception:
        break                # fail-open: an unlockable filesystem must not break the write
```

- Never take a blocking lock with no deadline; the deadline caps the pathological case below the hook timeout.

### The locking rules

1. Both sides participate: appenders take the lock even when each append is atomic, so a rewrite in progress excludes them.
2. Atomicity is not exclusion: route every read→modify→write through one locked primitive.
3. Lock a sidecar, never the file you replace: a lock on the old inode is released the instant the rename lands.
4. Enrol readers: a reader opening bare can observe a mid-rewrite file.

### One-shot flags

- Set a one-shot flag with `O_CREAT|O_EXCL` on a path.
1. "Cannot write" never reads as "already set": a store error returns the firing value. A tri-state only where every call site changes in one pass; a call site where repetition is expensive gets an explicit strict variant.
2. Key the flag to the lifecycle unit the rule is about, never to the ambient run: a rule about a repeating event carries that event's sequence number.
3. Consume the flag at the point of emission, never at the point of entry: a flag spent on a path that emits nothing turns "first run" into "never".
4. A blocking verdict consumes nobody's flag — § Ordering inside one engine.

## Ordering inside one engine

- One engine (`registry.md` § One engine, not many hooks) means one process, one exit and a shared pool of one-shot flags, so order decides what runs.
- Compute a blocking verdict above every check that mutates shared state: a deny that exits discards the advisories collected above it after their flags are spent, and the loss never reaches the decision log.
- Obeying a gate never costs anything: re-issuing after the remedy the block names produces the layer behaviour the first issue would have produced.
- Hoist a decision whose inputs are the payload and immutable state; a deny gate reading a feed the warn block writes keeps the feed writes above it, and only its decision moves.
- Assert the invariant directly: a call that is denied consumes no one-shot key.

## State a hook writes is a premise every later check inherits

- A durable write — a marker, a registry row, a context file — needs the evidence bar of a block, never of a log line: ask what is true on disk if it is wrong, and for how long.
- Several checks misbehaving together → look for one shared piece of state before rewriting any predicate.
- Verify the writer that should have fired, not only the one that did: a dead writer and a wrong writer leave the same wrong state.
- Removing a bad write → check what it is nested inside first.

## State growth

- Bound the read, never slurp and slice:

```python
def read_tail_lines(path, n, window=4 << 20):
    """The last n lines WITHOUT materialising the file.

    Byte-bounded, not merely seek-based: an endless character device reports size 0, so a
    size-guarded seek still reads forever. Reading at most `window` bytes makes the cost
    O(window) for every input, including ones that never end. Discard the first line of the
    window when the file exceeds it, because seeking lands mid-line. Fail-open → [].
    """
```

- `once()` mutates: short-circuit with a once-flag above a scan only when the condition it jumps over is monotone for the whole run.
- A condition a lifecycle event archives, renames, clears or rotates is not monotone → fix the scan with a streaming helper that breaks on first match, and leave the flag where it is.
- Re-measure a filed cost against production-scale input before acting on it.
- Watch inodes, not bytes: one inode per distinct one-shot key, forever, is the tail risk.
- Sanitise the state key, not just the values: an unvalidated session id is a path traversal.
- Prune in this order:
  1. Touch the run directory on each turn-end event, so mtime means last activity; done when every live run's mtime tracks its last turn.
  2. Trigger from an event that already runs, at most once a day, behind a durable flag — no cron, no new process.
  3. Delete only what is older than the window and has `mtime <= now` and is not the current run and resolves, symlinks refused, to a real path inside the root.
  4. Bound the work per pass.
  5. Record the sweep with its count.
  6. Wrap the whole sweep in one try/except: housekeeping never changes a verdict.
- Prune for disk, backup and exposure, never for speed.
- Reading state never creates it: classify a call by what it does when the target is absent, never by the verb in its name.
- A repair that changes how an artifact looks on disk → list the diagnostics keyed on the old look and update them in the same change.

## Load-testing a hook

- Load-test with real OS processes, never threads: `flock` is per open file description, so two threads sharing a file object never contend.

```python
ps = [subprocess.Popen([sys.executable, driver, "append"], env=ENV) for _ in range(4)]
ps.append(subprocess.Popen([sys.executable, driver, "rewrite"], env=ENV))
for p in ps:
    p.wait()
kept = sum(1 for ln in lines("D", "f") if ln.startswith("KEEP"))
print("KEEP rows surviving the race: %d of 1200" % kept)
```

- Report the surviving count from the run; 1200 of 1200 is the pass.

- Break the lock on purpose once and confirm the count drops: a load run that cannot drop proves nothing.
- Size the load until the race window is hit on every run; a break that shows only intermittently → enlarge the load before concluding the code is fine.
- Pair every behavioural race run with a structural read, run once and reported: list every feed writer by name, read each one's body, and confirm it takes the sidecar lock (`.lock`), never `_flock(path, …)`; a writer with no lock call is a finding.

- A simulator does the work it simulates — it writes the files.
- Parse every output protocol the code uses: turn-end events use a different decision shape than tool events.
- Loaded machine → report ratios against a same-run baseline, never absolutes.

## The hostile payloads

- Run every adapter against every malformed shape; any non-zero exit that is not a deliberate deny is a guard bypass.

```
very long input (200 KB)          tool_input is a LIST / STRING / null
input is ONLY a heredoc           command is a LIST / INT / DICT
deeply nested object (120 deep)   file_path is a LIST / INT
1000-deep nested JSON             tool_name is a LIST / null / INT
NUL bytes                         session_id is a LIST
ANSI escapes                      empty stdin
RTL + zero-width characters       {} at top level
lone surrogate                    [1,2,3] / "x" / 42 / null / true at top level
invalid UTF-8                     truncated JSON, duplicate keys
```

- Cross it with a corrupted state store (feed replaced by a directory, NUL bytes, invalid UTF-8, a huge file, a symlink loop, read-only) and a broken environment (`HOME` unset / read-only / empty, project dir missing, `PATH` unset, broken locale).
