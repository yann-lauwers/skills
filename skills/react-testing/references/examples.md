# Worked specs

Three complete tests, each covering a case the rules describe in the abstract: a form submitted against a mocked API, an error boundary catching a throw, and a Suspense boundary resolving. Read when a whole spec answers faster than a rule does.

## Form submission, MSW plus `userEvent`

```tsx
test("submits user form and shows success", async () => {
  server.use(
    http.post("/api/users", () =>
      HttpResponse.json({ id: "1", name: "Alice" }, { status: 201 }),
    ),
  );

  const user = userEvent.setup();
  renderWithProviders(<UserForm />);

  await user.type(screen.getByLabelText("Name"), "Alice");
  await user.type(screen.getByLabelText("Email"), "alice@example.com");
  await user.click(screen.getByRole("button", { name: /save/i }));

  expect(await screen.findByText(/saved successfully/i)).toBeInTheDocument();
});
```

Every element is reached by label or role, the request is answered at the wire, and the assertion is the text the user ends up looking at.

## Error boundary

```tsx
function Broken() {
  throw new Error("boom");
}

test("error boundary renders fallback", () => {
  // Suppress React's console.error noise for the expected throw, then restore so
  // the spy does not leak across tests and hide real errors elsewhere.
  const errorSpy = vi.spyOn(console, "error").mockImplementation(() => {});
  try {
    render(
      <ErrorBoundary fallback={<div>Something went wrong</div>}>
        <Broken />
      </ErrorBoundary>,
    );

    expect(screen.getByText("Something went wrong")).toBeInTheDocument();
  } finally {
    errorSpy.mockRestore();
  }
});
```

Restore the spy in `finally`. A spy left installed by a failing assertion silences React's errors for every test after it in the file.

## Suspense boundary

```tsx
test("shows loading then content", async () => {
  renderWithProviders(
    <Suspense fallback={<div>Loading...</div>}>
      <UserDetail id="1" />
    </Suspense>,
  );

  expect(screen.getByText("Loading...")).toBeInTheDocument();
  expect(await screen.findByText("Alice")).toBeInTheDocument();
});
```

The fallback is asserted synchronously and the content with `findBy*` — the two variants doing exactly what `references/queries-and-interaction.md` assigns them.
