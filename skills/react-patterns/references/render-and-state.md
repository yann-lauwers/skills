# Render, hooks, and where state lives

The three calls that decide a component tree's shape: what render is allowed to do, what a hook is allowed to do, and which scope owns a piece of state. Read before writing a component, and whenever a value is about to be stored in a second place.

`eslint-plugin-react-hooks`' recommended preset enforces the render and hook rules below mechanically — `set-state-in-effect`, `set-state-in-render`, `refs`, `purity`, `static-components`, `exhaustive-deps`; a repo whose ESLint config lacks it → say so once in the reply.

## Render is a pure function of props and state

Derive during render. Storing a derived value in `useState` and syncing it with `useEffect` adds a render cycle, can desync, and hides the data flow.

```tsx
// Good: derive during render
function Cart({ items }: { items: CartItem[] }) {
  const total = items.reduce((sum, i) => sum + i.price * i.qty, 0);
  return <span>{formatMoney(total)}</span>;
}

// Bad: derived state stored separately
function Cart({ items }: { items: CartItem[] }) {
  const [total, setTotal] = useState(0);
  useEffect(() => {
    setTotal(items.reduce((sum, i) => sum + i.price * i.qty, 0));
  }, [items]);
  return <span>{formatMoney(total)}</span>;
}
```

## Side effects outside render

Effects, mutations, network calls and subscriptions live in event handlers or `useEffect` — never in the render body.

## Composition over inheritance

React has no inheritance model for components. Compose with `children`, render props, or component props — the recipes are in `composition.md`.

## Hooks discipline

The hook contract, in full — the deps line is where this goes wrong most often:

- Top-level only, never conditional.
- **Exact deps.** List exactly what the effect body reads, nothing more and nothing less. Never
  drop a ref into the array to quiet the lint. Three identities are stable and are the only
  exemptions: `dispatch` from Redux, a `useRef` object, and a `setState` setter.
- Cleanup every subscription, interval, listener — the effect that starts one returns the
  function that tears it down.
- Functional updater (`setX(prev => prev + 1)`) when the new state depends on the old.
- Default position: do not memoize — add `useMemo` / `useCallback` only when a profiler or a dependency chain proves it matters.
- Extract a custom hook only when the same hook sequence appears in 2+ components.

### One value, two meanings

Tracking "did X happen / was this user-driven" in a `useRef` and reading it in callbacks to gate `setState` puts semantic state outside React's data flow — invisible to the reconciler, untestable via state assertions, a magnet for stale-closure bugs.

Refs hold DOM handles, stable instance values, and mutable values that DON'T drive rendering. When one value carries two meanings (`undefined` = both "untouched" and "explicitly empty"), encode the distinction IN state via a discriminated union and DERIVE the rendered value — don't imperatively reset it.

```tsx
// ❌ Imperative tracking via ref — semantic state outside data flow
const [value, setValue] = useState<string | undefined>(initial)
const userTouchedRef = useRef(initial !== undefined)
const handleChange = (v) => { userTouchedRef.current = true; setValue(v) }
const handleContextSwitch = () => {
  if (!userTouchedRef.current) setValue(newDefault)
}

// ✅ Discriminated state + derived value — distinction lives IN the data
type Selection = { kind: "auto" } | { kind: "explicit"; value: string | undefined }
const [selection, setSelection] = useState<Selection>(() =>
  initial !== undefined ? { kind: "explicit", value: initial } : { kind: "auto" }
)
const value = useMemo(
  () => selection.kind === "explicit" ? selection.value : derivedDefault,
  [selection, derivedDefault]
)
const handleChange = (v) => setSelection({ kind: "explicit", value: v })
// no handleContextSwitch — value re-derives when derivedDefault changes
```

### A custom hook, end to end

```tsx
function useDebounce<T>(value: T, delay = 300): T {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const id = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(id);
  }, [value, delay]);
  return debounced;
}

function SearchBox() {
  const [query, setQuery] = useState("");
  const debounced = useDebounce(query, 300);
  const { data } = useQuery({
    queryKey: ["search", debounced],
    queryFn: () => searchApi(debounced),
    enabled: debounced.length > 0,
  });
  return (
    <>
      <input value={query} onChange={(e) => setQuery(e.target.value)} />
      <Results items={data ?? []} />
    </>
  );
}
```

## State location decision tree

```
Used by one component?
  -> useState inside it

Used by parent + a few descendants?
  -> lift to nearest common ancestor

Used across distant branches AND low-frequency reads (theme, auth, locale)?
  -> React Context

High-frequency updates shared across the tree?
  -> external store (Zustand, Jotai, Redux Toolkit)

Derived from a server?
  -> server-state library (TanStack Query, SWR, RSC fetch)
```

Most pages need neither context nor a global store. Resist the abstraction until duplicated lifting becomes painful.

Filters, pagination and search terms are URL state: they go through the router, so a reload, a shared link and the back button keep them.
