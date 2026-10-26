---
name: react-testing
description: "Writes and fixes React component and hook tests with Testing Library, Vitest (or Jest) and MSW — what to assert, which query, how the network is mocked, where JSDOM stops and a real browser starts. Use on 'write a test for this component', 'test this hook', 'mock the API in the test', 'this test is flaky', 'why does act warn', 'no a11y violations'; before writing a `.test.tsx` spec or any test calling `renderHook`; on MSW handlers, `userEvent`, `waitFor`, `vitest-axe`. Not for the red-green-refactor loop — /tdd ."
metadata:
  origin: ECC
  source: https://github.com/affaan-m/ECC/blob/main/skills/react-testing/SKILL.md
---

# React Testing

What a React test asserts, and with which instrument. Behaviour through accessible queries, network mocked at the wire with MSW, hooks exercised through their public API, and a stated boundary past which JSDOM stops answering and a real browser starts. Every recipe lives in a reference; this file routes to one.

One principle sits under every row: test what the user sees and does, never how the component reaches it. A test that inspects state, counts renders, or asserts DOM shape passes while the product is broken and fails on a refactor that changed nothing — the inverse of what a suite is for.

The stack this covers is Vitest + Testing Library + MSW under JSDOM. Jest appears only where a Next.js repo already ships it; the API is compatible and the recipes transfer unchanged.

## Before acting

Match the request against the routing table, read the matched reference, then write the test. A spec written from this file alone carries none of the traps.

## Routing table

| Intent | Read |
| --- | --- |
| IF deciding what a test should assert, or judging one that asserts the wrong thing — anti-patterns, snapshots, accessibility violations | THEN `references/what-to-assert.md` |
| IF picking a query, driving an interaction, or waiting on something async | THEN `references/queries-and-interaction.md` |
| IF the component talks to an API and the test has to answer it | THEN `references/network-mocking.md` |
| IF wiring the runner — providers, a shared render helper, coverage thresholds, the commands to run | THEN `references/harness.md` |
| IF the subject is a custom hook rather than a rendered surface | THEN `references/hooks.md` |
| IF JSDOM cannot do it — layout, scroll, drag, clipboard, iframes, a real flow across pages | THEN `references/playwright-boundary.md` |
| IF the component does not exist yet and the tests come first | THEN `cookbook/new-component.md`, then /tdd |
| IF a whole worked spec would answer faster than a rule — form submit, error boundary, Suspense | THEN `references/examples.md` |
| IF the request matches none of the above | THEN `references/what-to-assert.md`, say which row was closest |

## Related

- Component and hook design under test: /react-patterns
- The red-green-refactor loop itself: /tdd
- Reviewing test quality in a diff: /code-review
