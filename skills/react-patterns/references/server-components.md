# Server and Client Components

Where the RSC boundary sits, what may cross it in each direction, and which framework concerns sit on top of it rather than inside it. Read before adding `"use client"`, before passing a prop across the boundary, and when an import fails at the seam.

```tsx
// Server Component - default, async, never ships JS for itself
export default async function ProductPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const product = await db.product.findUnique({ where: { id } });
  if (!product) notFound();
  return <ProductView product={product} />;
}

// Client Component - opt in with "use client"
"use client";
export function AddToCartButton({ productId }: { productId: string }) {
  const [isPending, startTransition] = useTransition();
  return (
    <button
      disabled={isPending}
      onClick={() => startTransition(() => addToCart(productId))}
    >
      {isPending ? "Adding..." : "Add to cart"}
    </button>
  );
}
```

## Boundaries

- `"use client"` sits at the leaves: push the boundary as deep as it goes; parents stay Server Components.
- Server → Client: pass serializable props, or `children`.
- Client → Server: invoke Server Actions via `<form action={...}>`, or imperatively from an event handler.
- A Client Component file never `import`s a Server Component — compose them through `children` instead.

## Routing sits on top

These patterns are router-agnostic: they hold under the Next.js App Router, React Router and TanStack Router alike. Router-specific surfaces — loaders, actions, nested layouts, Route Handlers, Middleware, Parallel Routes — are framework concerns layered over React core, and they follow that framework's own docs rather than anything here; Next.js → /nextjs-patterns .
