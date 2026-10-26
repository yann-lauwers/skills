# Testing a NestJS module

How a provider, a controller and the request pipeline around it get tested. Read when writing a spec against a module, a guard, or a validation pipe.

```ts
describe('UsersController', () => {
  let app: INestApplication;

  beforeAll(async () => {
    const moduleRef = await Test.createTestingModule({
      imports: [UsersModule],
    }).compile();

    app = moduleRef.createNestApplication();
    await app.init();
  });
});
```

Providers are unit-tested in isolation with mocked dependencies. Guards, validation pipes and exception filters are proven at the request level — they do not run in a unit test of the service behind them. The test app is wired through the same registration `main.ts` calls — its filter-registration helper, its global pipe if one exists; a test app missing them proves a pipeline that never ships.

Every service spec covers the happy path, at least one error branch and at least one boundary case — the test names show which is which. Request-level specs assert the status code and the error body for invalid, unauthorized and forbidden requests, not only the success path.
