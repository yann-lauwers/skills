# Accessibility-first composition

What a component owes a keyboard and a screen reader, decided while it is being written rather than audited afterwards. Read when building an interactive element, a form field, a modal, or anything that changes what is on screen.

- Render semantic HTML — `<button>`, `<a>`, `<nav>`, `<main>` — before reaching for a `role` attribute.
- Every interactive element is reachable by keyboard.
- Every input carries a label: `<label htmlFor>`, or `aria-label` where an icon does the labelling.
- Manage focus on route changes and on modal open/close.
- Run `axe` in component tests — /react-testing carries the harness.

## A native element carries four things a `role` does not

`<button>` gives focusability, Enter and Space activation, the announced role, and the disabled semantics in one token. `role="button"` gives the announcement only, so every `div` control owes `tabIndex={0}` and an `onKeyDown` handling both Enter and Space — and the two keys behave differently on a real button, which is why hand-rolled controls activate on Enter and stay dead on Space. Reach for ARIA when no native element carries the interaction: a combobox, a tab set, a tree.

## Do not

- `onClick` on a `div` or `span` with no `role`, `tabIndex` and `onKeyDown`.
- `aria-hidden` on anything focusable — the control keeps its tab stop and announces nothing, so a keyboard user lands on silence.
- A positive `tabIndex` — it jumps that element ahead of every element in document order, and the order stops being readable from the markup.
- `placeholder` standing in for a label — it disappears on first keystroke and several screen readers skip it.
- "Image of" in `alt` — the role is already announced.

## Naming a control

An icon-only control names itself with `aria-label`. A region with visible heading text points at that text with `aria-labelledby` instead, so the name moves when the copy does. `aria-describedby` carries what is supplementary — a consequence, a format hint, an error — never the name.

Decorative graphics inside a labelled control take `aria-hidden="true"`, or the name is announced twice.

```tsx
<button aria-label="Delete invoice" aria-describedby="delete-warning">
  <TrashIcon aria-hidden="true" />
</button>
<p id="delete-warning">Deleting an invoice cannot be undone.</p>
```

## A field's error has to be reachable from the field

Error text rendered next to an input is invisible to a screen reader reading the input. Link it with `aria-describedby`, flip `aria-invalid` on the same render, and give the message `role="alert"` so it announces when it appears rather than when focus reaches it.

Requiredness is announced by `required`; the asterisk beside the label is decoration and takes `aria-hidden="true"`.

```tsx
<input
  id="email"
  type="email"
  required
  autoComplete="email"
  aria-invalid={!!error}
  aria-describedby={error ? "email-error" : undefined}
/>
{error && <span id="email-error" role="alert">{error}</span>}
```

`aria-describedby` pointing at an id that renders conditionally is a dangling reference on the clean render, which some screen readers report as a missing description. Set it to `undefined` rather than to the id, as above.

## Live regions announce a change, not a value

A region is announced when its content changes while it is already in the accessibility tree. A region mounted at the same moment its message arrives announces nothing — render the container empty and fill it, or the status is silent for exactly the case it exists for.

`aria-live="polite"` waits for the user to stop; `assertive` interrupts, and is for a failure the user cannot proceed past. `aria-atomic="true"` makes the whole region re-read rather than only the changed node.

## Focus is a piece of state the component owns

Opening an overlay: store `document.activeElement`, move focus into the overlay, contain Tab and Shift+Tab inside it, close on Escape, and return focus to the stored element. Restoring focus is the half that gets dropped, and the keyboard user resumes at the top of the document with the page silently changed under them.

Containment past the simple case — dynamic content, nested portals, a portal outside the React tree — goes to `focus-trap-react` rather than a hand-rolled key handler.

A client-side route change moves focus to the new view's heading or to a skip target; the browser does nothing on its own, so the next Tab continues from wherever the old page left off.

## Motion asks the OS first

Read `(prefers-reduced-motion: reduce)` through `matchMedia` and subscribe to its `change` event — a value read once at mount goes stale when the user flips the OS setting mid-session. Reduced motion means the transition is replaced by an instant state change, never that the state change is skipped.

## What a component owes before review

- Every `input`, `select` and `textarea` has a label connected by `htmlFor`/`id`.
- Every icon-only control has `aria-label`; every decorative graphic has `alt=""` or `aria-hidden`.
- Tab reaches every control, in the order they are read, and leaves again.
- The overlay traps focus, closes on Escape, and gives focus back.
- Status and error text lives in a region that was already mounted.
- Heading levels descend by one.
- Text hits 4.5:1 against its background, and a control's own boundary hits 3:1.
- The hit area is at least 24×24 CSS pixels, padding included.
