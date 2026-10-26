# Client-side data fetching

Fetching, listeners and local storage on the client — where duplicate work is invisible until the network tab is open.

## SWR / TanStack Query for deduplication

Multiple components calling `useUser(id)` should share one network request and one cache entry; react-patterns' data-fetching reference names the tool.

## Deduplicate global event listeners

```tsx
// INCORRECT — every component adds its own
useEffect(() => {
  window.addEventListener("scroll", handler);
  return () => window.removeEventListener("scroll", handler);
}, []);

// CORRECT — single shared listener via a hook + global subject
const useScroll = createScrollHook(); // singleton subject under the hood
```

## Passive listeners for scroll

```ts
window.addEventListener("scroll", handler, { passive: true });
```

Improves scrolling smoothness; the listener cannot `preventDefault()`.

## localStorage: version + minimize

- Always store a `version` field; bump on schema change and migrate or discard old data
- Keep payloads small — `localStorage` is synchronous and blocks main thread
