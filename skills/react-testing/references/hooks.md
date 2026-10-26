# Testing a custom hook

Exercising a hook through `renderHook` — its public API, state changes under `act`, and a wrapper for the context it depends on. Read when the subject is a hook rather than a rendered surface.

Test through the hook's public return value only. Wrap every call that changes state in `act`. A hook that reads context takes a `wrapper` rather than a mocked context module.

```tsx
import { renderHook, act } from "@testing-library/react";

test("useCounter increments and decrements", () => {
  const { result } = renderHook(() => useCounter(0));

  expect(result.current.count).toBe(0);

  act(() => result.current.increment());
  expect(result.current.count).toBe(1);

  act(() => result.current.decrement());
  expect(result.current.count).toBe(0);
});

test("useCounter accepts initial value", () => {
  const { result } = renderHook(() => useCounter(10));
  expect(result.current.count).toBe(10);
});

test("useUser fetches user data", async () => {
  // Instantiate QueryClient ONCE per test, outside the wrapper, so it survives re-renders.
  // Created inside the wrapper closure it resets cache state on every render — flaky.
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  const wrapper = ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );

  const { result } = renderHook(() => useUser("1"), { wrapper });

  await waitFor(() => expect(result.current.isSuccess).toBe(true));
  expect(result.current.data).toEqual({ id: "1", name: "Alice" });
});
```

The third test is the one that goes wrong quietly. The wrapper is a component, so it re-renders — and a `QueryClient` constructed in its body is a new cache each time, which makes a fetch that resolved appear never to have resolved. Hoisting it above the wrapper is what makes the assertion stable.

Data fetched inside a hook is answered by MSW, not by a mocked client: `references/network-mocking.md`.
