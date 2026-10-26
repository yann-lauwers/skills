# Persistence and transactions

Where ORM code sits and who owns a multi-step write. Read when adding a repository, a Prisma call, or a workflow that writes more than one row.

ORM code sits behind providers that speak the domain's language — a service calls `usersRepo.create(dto)`, not a query builder. A transactional workflow is owned by the service that owns the unit of work; a controller coordinating multi-step writes has split one invariant across the HTTP layer.

```ts
@Injectable()
export class BillingService {
  constructor(private readonly prisma: PrismaService) {}

  async chargeAndRecord(input: ChargeInput) {
    return this.prisma.$transaction(async (tx) => {
      const invoice = await tx.invoice.create({ data: input.invoice });
      await tx.ledgerEntry.create({ data: { invoiceId: invoice.id, ...input.entry } });
      return invoice;
    });
  }
}
```

The interactive `$transaction` callback holds a connection for its whole body, so an HTTP call or a long computation inside it starves the pool. Do the slow work first, then open the transaction around the writes.
