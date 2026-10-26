# Composition recipes

The four shapes a component uses to accept content from its caller, and which one fits. Read when a component is growing boolean props to control what it renders, or when a parent needs to pass parameters into the markup it hands down.

## Slot via `children`

```tsx
<Layout>
  <Header />
  <Main>{content}</Main>
</Layout>
```

## Named slots

```tsx
<Page header={<Nav />} sidebar={<Filters />}>
  <Results />
</Page>
```

## Compound components — shared state via Context

```tsx
<Tabs defaultValue="profile">
  <Tabs.List>
    <Tabs.Trigger value="profile">Profile</Tabs.Trigger>
    <Tabs.Trigger value="settings">Settings</Tabs.Trigger>
  </Tabs.List>
  <Tabs.Panel value="profile"><Profile /></Tabs.Panel>
  <Tabs.Panel value="settings"><Settings /></Tabs.Panel>
</Tabs>
```

## Render prop / function-as-child

Earns its place when the parent has to pass parameters into the rendered output.

```tsx
<DataLoader id={id}>
  {({ data, isLoading }) => isLoading ? <Spinner /> : <UserCard user={data} />}
</DataLoader>
```

A hook returning the same shape — `useData(id)` — is usually the cleaner form; reach for the render prop when the markup, not the data, is what varies.

## Component boundaries

- Components render only: logic in hooks, data in the API layer, no nested render functions.
- 250 lines is a soft cap; over 300 → split. Over 10 props → compose smaller components.
- Visual variation goes through variant props, never a consumer's `className` override.
- A shared component about to gain a prop, ref or hook for one consumer → surface the alternatives first: drop the need, solve it in the consumer, or extend the component.
- A wrapper around optional children renders only when there are children (`items.length > 0 && …`) — an empty wrapper still renders its padding and takes a gap slot in its parent's flex or grid layout.
