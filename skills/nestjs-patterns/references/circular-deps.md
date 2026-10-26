# Circular module dependencies

How a module cycle is cut rather than papered over. Read when a `forwardRef()` is about to be added, `import/no-cycle` fires, or boot fails with "Nest can't resolve dependencies" or "Cannot access 'X' before initialization".

`forwardRef()` leaves the edge, the cycle and the lint in place. A dependency genuinely both ways — a registry and its registrants, a module and the features it composes — keeps its `forwardRef()`; any other `forwardRef()` stays only once steps 1–3 were each tried and the PR names why each failed. Cut the edge, cheapest that fits:

1. **Delete a dead edge** — the module is imported, but no provider of the importer injects any of its exports. Done when the importer boots without it.
2. **Extract a leaf** — both sides share a cohesive provider set with no reverse dependency. Move it to a lower module both import. Done when neither original module imports the other.
3. **Invert through a port** — the consumer needs a method or two, or the provider cannot detach. Inject an interface, not the module: the consumer declares the port and a token beside it, since an interface is erased at runtime; a `@Global()` binding module beside the provider imports the provider's module, binds `{ provide: TOKEN, useClass: Adapter }`, exports the token, and is imported once at the root; the consumer takes `@Inject(TOKEN)` and imports neither. Done when the consumer's module no longer imports the provider's and the app boots.

Before deleting a "dead" edge, list the imported module's exports, confirm no provider of the importer injects one, then boot the app. A provider whose file sits in another directory makes a live edge look dead.

A module that re-exposes a provider moved to a leaf exports the leaf module (`exports: [TheLeafModule]`), never the bare provider, or `app.init()` crashes.

`import type` is erased and is not a cycle edge. A `require()` inside `@Inject(forwardRef(() => …))` hides the file edge from the lint while the DI edge remains — cut or invert it like any other.

Removing one cycle can surface a require-time TDZ ("Cannot access 'X' before initialization") elsewhere; that is another cycle, cut the same way.
