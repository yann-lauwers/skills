# What a React test asserts

The line between behaviour and implementation, the anti-patterns that cross it, where a snapshot is still legitimate, and how an accessibility violation is asserted. Read before writing the first `expect`, and when judging a suite that passes while the product is broken.

## The principle

Assert what the user sees and does:

- Render the component with the providers it has in production.
- Interact through accessible queries — role, label — and `userEvent`.
- Assert visible output and observable side effects: a callback fired, a request sent, text on screen.

Never assert component state, props handed to a child, which hooks ran, how many renders happened, or DOM structure past what a user perceives. Never mock React or a framework hook.

Both failure directions come from the same mistake. A test bound to internals passes while the button does nothing a user can reach, and fails on a refactor that changed no behaviour — so the suite reports the opposite of the truth twice over.

## Anti-patterns

| Written | Why it is wrong |
| --- | --- |
| `container.querySelector("…")` | bypasses accessible queries, so the test passes where a real user is blocked |
| asserting a render count | implementation detail; a memo change turns it red for nothing |
| `vi.mock("react", …)` | never mock React — refactor the component instead |
| mocking child components by default | tests isolation nobody ships; mock a child only where it carries a heavy side effect |
| ignoring `act()` warnings | each one is a real bug — a state update after unmount, or async work outside a wrapper |
| mutable state shared across tests | green until the test order changes |
| a test that still passes with its assertions removed | it asserts nothing it claims to |

## Snapshots

No snapshots of rendered component output. They break on every styling change, get rubber-stamped in review, and pin DOM structure rather than behaviour.

Snapshots stay legitimate for pure serialization — `formatInvoice(invoice)` to a stable string, a generated config file. Visual regression on a component is a real screenshot diff in Playwright, never a DOM string.

## Accessibility violations

```tsx
import { axe, toHaveNoViolations } from "vitest-axe";
expect.extend(toHaveNoViolations);

test("UserCard has no a11y violations", async () => {
  const { container } = render(<UserCard user={mockUser} />);
  expect(await axe(container)).toHaveNoViolations();
});
```

Run axe in the component test for every interactive component. It catches missing labels on form inputs, invalid ARIA, missing alt text, and heading-order violations.

Contrast is the one it half-catches: JSDOM has no CSS engine, so axe sees inline styles and nothing from a stylesheet. Real contrast is a browser assertion — `references/playwright-boundary.md`.
