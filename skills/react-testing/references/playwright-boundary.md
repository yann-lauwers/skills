# Where JSDOM stops and a browser starts

The stated boundary between a component test and a real-browser run: what JSDOM cannot do, and which vehicle each kind of subject takes. Read when a test fights the environment rather than the component.

## What JSDOM cannot do

Vitest and Jest run under JSDOM, which has no layout engine and no browser process. It cannot:

- compute real layout — flexbox, grid, viewport queries, element size
- run CSS transitions or native animation
- test scrolling, drag-and-drop, or clipboard paste
- handle iframes, popups, downloads, or cross-origin flows
- exercise real network with DevTools-grade control

The tell is a test that mocks `getBoundingClientRect`, `IntersectionObserver` or `scrollTo` to get to green. Each mock is an assertion about the browser written by the test author, so the test proves the mock rather than the component. That is the moment the subject belongs in a browser.

## The vehicle

| Subject | Vehicle |
| --- | --- |
| A hook, a presentational component, a form with logic | Testing Library under Vitest |
| A component whose layout matters, or that uses a browser API JSDOM lacks | Playwright Component Testing |
| A user flow across several pages | Playwright E2E |
| Visual regression on a component | a real screenshot diff, never a DOM snapshot |
