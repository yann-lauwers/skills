# The harness — runner, providers, coverage, commands

Everything a spec needs before its first assertion: which runner, the shared render helper that supplies production providers, the coverage thresholds worth enforcing, and the commands that run the suite. Read when setting a project up, or when a test fails on a missing provider.

## Runner

| Runner | When | Note |
| --- | --- | --- |
| **Vitest** | Vite, Remix, anything greenfield | Native ESM, Jest-compatible API, fastest of the three |
| **Jest** | a Next.js or CRA repo that already ships it | Do not migrate a working suite for its own sake |
| **Playwright Component Testing** | JSDOM lacks the feature the component needs | The boundary is in `references/playwright-boundary.md` |

One runner for component tests per repo. Vitest plus Playwright CT in the same tree is allowed only where the lane split is explicit — CT for the components that need a browser engine, Vitest for everything else — and written down.

## Providers

Wrap production providers once in `test-utils.tsx`, re-export Testing Library through it, and import every spec from there. A provider list repeated per spec drifts from the app the moment a provider is added.

```tsx
// test-utils.tsx
import { render, RenderOptions } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

export function renderWithProviders(
  ui: React.ReactElement,
  options?: RenderOptions,
) {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });

  return render(
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={lightTheme}>
        <MemoryRouter>{ui}</MemoryRouter>
      </ThemeProvider>
    </QueryClientProvider>,
    options,
  );
}

export * from "@testing-library/react";
```

`retry: false` on the query client. Retries turn a deliberate 500 into a multi-second wait and then a timeout, which reads as a flake rather than as the error path the test asserts.

## Coverage

| Layer | Target |
| --- | --- |
| Pure utilities | ≥90% |
| Custom hooks | ≥85% |
| Presentational components | ≥80% — behaviour, not lines |
| Container components | ≥70% — golden paths plus error states |
| Pages | smoke test here; the flow is covered by an E2E run |

```ts
// vitest.config.ts
test: {
  coverage: {
    provider: "v8",
    reporter: ["text", "html", "lcov"],
    thresholds: {
      lines: 80,
      functions: 80,
      branches: 70,
      statements: 80,
    },
  },
}
```

## Commands

```bash
vitest                            # watch
vitest run                        # one-shot
vitest run --coverage             # with coverage
vitest run path/to/file.test.tsx  # single file
CI=true vitest run --coverage     # CI mode
```

On a Jest repo the same four shapes are `jest --watch`, `jest`, `jest --coverage` and `jest path/to/file.test.tsx`.
