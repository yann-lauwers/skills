# Authentication and authorization

## Credentials on the wire

```
# Bearer token in Authorization header
GET /api/v1/users
Authorization: Bearer <token>

# API key (for server-to-server)
GET /api/v1/data
X-API-Key: <key>
```

## Where the checks sit

```typescript
// Resource-level: check ownership
app.get("/api/v1/orders/:id", async (req, res) => {
  const order = await Order.findById(req.params.id);
  if (!order) return res.status(404).json({ error: { code: "not_found" } });
  if (order.userId !== req.user.id) return res.status(403).json({ error: { code: "forbidden" } });
  return res.json({ data: order });
});

// Role-based: check permissions
app.delete("/api/v1/users/:id", requireRole("admin"), async (req, res) => {
  await User.delete(req.params.id);
  return res.status(204).send();
});
```

- Authentication and the role check → the middleware chain the handler itself runs, never a request-interception layer in front of the app; the ownership check → where the row is loaded, inside the handler or the service, on every read and every write.
- Every endpoint is authenticated, or explicitly marked public.
- Guessable identifier and sensitive existence → 404 for both the missing and the forbidden row, as RFC 9110 §15.5.4 allows.
