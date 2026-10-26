# Queries, interaction, and async

Which query finds an element, how a real interaction is driven, and how a test waits on work that has not finished. The three together are most of what a component spec is made of.

## Query priority

Testing Library exposes three tiers. Work top-down and stop at the first that fits:

1. **Accessible to everyone** — `getByRole`, `getByLabelText`, `getByPlaceholderText`, `getByText`, `getByDisplayValue`.
2. **Semantic** — `getByAltText`, `getByTitle`.
3. **Test ids, the escape hatch** — `getByTestId`.

```tsx
screen.getByRole("button", { name: /save/i }); // best
screen.getByLabelText("Email");                // fine for inputs
screen.getByTestId("save-btn");                // last resort
```

Pick the variant by what the assertion means:

- `getBy*` — throws when nothing matches. The default.
- `queryBy*` — returns `null`. The only one that asserts absence.
- `findBy*` — async, returns a Promise. For anything that appears after async work.

## Interaction with `userEvent`

```tsx
import userEvent from "@testing-library/user-event";

test("submits the form", async () => {
  const user = userEvent.setup();
  const onSubmit = vi.fn();
  render(<UserForm onSubmit={onSubmit} />);

  await user.type(screen.getByLabelText("Email"), "user@example.com");
  await user.click(screen.getByRole("button", { name: /save/i }));

  expect(onSubmit).toHaveBeenCalledWith({ email: "user@example.com" });
});
```

`await` every `userEvent` call. Call `userEvent.setup()` once per test and reuse the returned `user`.

Prefer `userEvent` over `fireEvent`: `userEvent` replays the browser sequence a real interaction produces — pointer, focus, key events — while `fireEvent` dispatches one synthetic event and skips everything a handler upstream of it depends on.

## Async

```tsx
expect(await screen.findByText("Loaded")).toBeInTheDocument();     // appears
await waitFor(() => expect(saveSpy).toHaveBeenCalled());           // side effect
await waitForElementToBeRemoved(() => screen.queryByText("Loading")); // disappears
```

Never wait with `setTimeout` plus an assertion — it encodes a machine speed and flakes on a slower one. The three matchers above retry until the condition holds or the timeout expires.
