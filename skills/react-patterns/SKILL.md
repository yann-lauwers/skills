---
name: react-patterns
description: "Shapes a React 18/19 component tree — what render may compute, what an effect is for, where state lives, the server/client boundary, Suspense and error boundary placement, form submission, re-renders, keyboard reach. Use on 'where should this state live', 'why does this re-render', 'server or client component', 'this form needs an action', `useEffect`, `\"use client\"`, `useActionState`, TanStack Query; when writing a `.tsx` / `.jsx` component or hook. Not for a slow page — /react-performance ; not for tests — /react-testing ; not for a hand-rolled combobox — /frontend-accessibility ."
metadata:
  origin: ECC
  source: https://github.com/affaan-m/ECC/blob/main/skills/react-patterns/SKILL.md
---

# React Patterns

Router over the React 18/19 patterns that decide a component tree's shape — what render may do, where state sits, what crosses the server/client boundary, how a form submits, and why a subtree re-renders. Four premises hold across every reference and are stated once here: state is the single source of truth, so nothing forces a visual change imperatively through the DOM, a ref or a store; `useEffect` is for syncing with something outside React — a subscription, a timer, a network call — and never for deriving one piece of state from another; refs do not re-render, so a value the UI depends on is never a `useRef`; and state sits in one of three tiers — local (`useState`), server (a server-state library), global UI (a store) — with server data read from its library rather than copied into `useState`.

## Routing table

| Intent | Read |
| --- | --- |
| IF deciding what render may compute, what an effect is for, or which scope owns a piece of state | THEN `references/render-and-state.md` |
| IF adding `"use client"`, passing props across the RSC boundary, or wiring a Server Action | THEN `references/server-components.md` |
| IF placing a Suspense fallback, or an error escaped a boundary | THEN `references/suspense-and-errors.md` |
| IF choosing between RSC fetch, TanStack Query, SWR and a handler-level `fetch()` | THEN `references/data-fetching.md` |
| IF building a form, a controlled input, or optimistic UI | THEN `references/forms.md` |
| IF a component is growing boolean props or past 250 lines, a parent must parameterise what it renders, or a shared component is about to change for one consumer | THEN `references/composition.md` |
| IF a subtree re-renders too often, or a list is getting long | THEN `references/performance.md` |
| IF wiring keyboard access, labels, focus management, or semantics | THEN `references/accessibility.md` |
| IF creating a file or feature folder, a provider, an API client, an env read, or a permission check | THEN `references/project-structure.md` |
| IF the surface is slow at the app or Next.js level — waterfalls, bundle size, server cost | THEN /react-performance , which carries the Vercel ruleset |
| IF the work is a component or hook test | THEN /react-testing |
| IF the request matches none of the above | THEN `references/render-and-state.md`, say which row was closest |
