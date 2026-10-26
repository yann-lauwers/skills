# Network mocking with MSW

Answering the component's HTTP calls at the network layer instead of stubbing the fetch client. Read when a component, a hook or a page under test talks to an API.

MSW intercepts at the wire. The component, its hooks, its data layer and its fetch client all run exactly as they do in production — the only substituted thing is the response. Stubbing the client instead tests a seam nobody ships.

## Setup

```ts
// test/setup.ts
import { setupServer } from "msw/node";
import { http, HttpResponse } from "msw";

export const handlers = [
  http.get("/api/users/:id", ({ params }) =>
    HttpResponse.json({ id: params.id, name: "Alice" }),
  ),
  http.post("/api/users", async ({ request }) => {
    const body = await request.json();
    return HttpResponse.json({ id: "new-id", ...body }, { status: 201 });
  }),
];

export const server = setupServer(...handlers);

beforeAll(() => server.listen({ onUnhandledRequest: "error" }));
afterEach(() => server.resetHandlers());
afterAll(() => server.close());
```

Set `onUnhandledRequest: "error"`. An unmocked request then fails the test loudly; on the default it passes through and the spec goes green against whatever the environment happened to answer.

`server.resetHandlers()` in `afterEach` is what keeps a per-test override from leaking into the next test.

## Per-test override

```tsx
test("renders error on 500", async () => {
  server.use(
    http.get("/api/users/:id", () => new HttpResponse(null, { status: 500 })),
  );
  render(<UserPage id="1" />);
  expect(await screen.findByText(/something went wrong/i)).toBeInTheDocument();
});
```

The default handlers cover the golden path; `server.use(…)` inside one test covers that test's failure, empty or slow case. Error states are asserted this way rather than by mocking a rejected promise.
