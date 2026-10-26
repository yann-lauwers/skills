# Render performance

The three levers that move a React tree's render cost — memoisation where it pays, context shaped so a change reaches few consumers, and lists that stay cheap as they grow. Read when a surface re-renders more than it should. Whole-app and Next.js-level cost belongs to /react-performance instead.

## When `React.memo` actually helps

Wrap a component in `React.memo` only when all three hold: it re-renders frequently, its props are usually equal between renders, and its own render is measurably expensive. The equality check runs on every render, so props that differ most of the time make it pure overhead.

## Avoiding render cascades

- Push state down rather than up wherever the tree allows it.
- Split context — one per concern, so a `themeContext` change leaves auth consumers alone.
- Read external stores through `useSyncExternalStore`; concurrent rendering requires it.

```tsx
// Two contexts: one rarely changes, one frequently
const ThemeContext = createContext<Theme>("light");
const NotificationsContext = createContext<Notification[]>([]);

// A component that only consumes ThemeContext does NOT re-render when notifications change
```

## Lists

Key on a stable identity — a database id, never the array index or a value generated during render. Virtualise with `@tanstack/react-virtual` or `react-window` once visible rows pass ~50 with non-trivial content.
