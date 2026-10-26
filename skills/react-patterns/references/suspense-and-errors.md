# Suspense and error boundaries

Where a boundary goes, and the errors it does not catch. Read when a fallback renders at the wrong level, or when an error escapes a boundary that looks like it should have caught it.

```tsx
<ErrorBoundary fallback={<ErrorView />}>
  <Suspense fallback={<UserSkeleton />}>
    <UserDetail id={id} />
  </Suspense>
</ErrorBoundary>
```

- Place Suspense boundaries close to the data, not at the route root — content then reveals progressively.
- One error boundary per feature, `{feature}-boundary.tsx`; its reset path calls `queryClient.resetQueries` before retrying, so a retry refetches instead of re-rendering the failed cache.
- Error Boundary is still a class API; `react-error-boundary` wraps it hook-side; in Next.js the boundary is the one the installed version's docs give, since a generic boundary also catches `redirect()` and `notFound()`; where those docs live — /nextjs-patterns · docs give no component-level boundary → `react-error-boundary`, its fallback rethrowing the errors the docs say `redirect()` and `notFound()` throw.
- A boundary catches what its children throw during render, lifecycle and constructors — **not** inside event handlers, and not inside async code.
