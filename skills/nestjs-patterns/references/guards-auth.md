# Guards, auth and request context

Where an access decision is taken, and how the authenticated request is typed. Read when adding a guard, a role check, a strategy, or reading `req.user`.

```ts
@UseGuards(JwtAuthGuard, RolesGuard)
@Roles('admin')
@Get('admin/report')
getAdminReport(@Req() req: AuthenticatedRequest) {
  return this.reportService.getForUser(req.user.id);
}
```

Guards carry the coarse rule — is this caller authenticated, does it hold the role. Resource-specific authorization — does this caller own *this* record — belongs in the service, where the record is loaded. Auth strategies and guards stay module-local until a second module genuinely consumes them.

An authenticated handler takes an explicit request type (`AuthenticatedRequest`), never a bare `Request` with `req.user` typed `any`.
