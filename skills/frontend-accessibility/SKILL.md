---
name: frontend-accessibility
description: "Builds the keyboard model of a hand-rolled composite widget — dropdown, combobox, menu, tab set — to the WAI-ARIA Authoring Practices pattern, and checks a surface against WCAG 2.2's Redundant Entry and Focus Appearance. Use on 'aria-activedescendant', 'roving tabindex', 'WCAG 2.2', 'redundant entry', 'focus appearance', or writing `role=\"combobox\"`, `\"listbox\"`, `\"menu\"` or `\"tablist\"`, or an arrow-key handler in a custom list. Not for labels, semantics or focus management on a React surface — /react-patterns ."
metadata:
  origin: nexus-generalized
  generalized-from: "ECC's frontend-a11y skill, checked against the WAI-ARIA Authoring Practices Guide and WCAG 2.2 — trimmed after a canon review found most of it already stated, at the same or greater specificity, in react-patterns/references/accessibility.md"
---

# Frontend Accessibility — the Composite-Widget Pattern and WCAG 2.2

- Forms, semantic HTML, ARIA naming, live regions, focus management, motion and target size → /react-patterns , `references/accessibility.md`, read first; this skill carries only what it leaves out.

## Composite-widget keyboard pattern

- A hand-rolled dropdown, combobox, menu or tab set follows the WAI-ARIA Authoring Practices Guide's pattern for its shape; an invented role and attribute combination gets the focus model wrong while looking right.
- One roving tab stop, never one per option: the container is the only element in the tab order, and arrow keys move a tracked active option inside it.
- `aria-activedescendant` on the container points at the active option's `id`; an active option tracked only in component state is invisible to a screen reader.
- `aria-expanded` on the trigger reflects open or closed; `aria-controls` on the trigger points at the popup's `id`.
- Escape closes, Enter and Space select, arrow keys move.

## WCAG 2.2 — Redundant Entry and Focus Appearance

- Redundant Entry, 3.3.7, Level A → information the user already entered or was given earlier in the same process is auto-populated or offered to select on a later step, never asked for again, unless re-entry is essential, the information secures the content, or the earlier value is no longer valid.
- Focus Appearance, 2.4.13, Level AAA → a visible focus indicator covers at least the area of a 2 CSS pixel perimeter of the unfocused component, and its pixels hit 3:1 between the focused and unfocused states.
