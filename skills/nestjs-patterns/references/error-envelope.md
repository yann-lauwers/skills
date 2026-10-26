# Exception filters and the error envelope

One error shape across the API, and where an unexpected failure is caught. Read when a route returns an inconsistent error body, or when adding a filter.

## The repo's envelope wins

Read it first: the shared response schema or types package (a `response.schema.ts`, an `ApiResponse` type), the `@Catch()` classes (`grep -rn "@Catch" src`), and `APP_FILTER` / `useGlobalFilters` registrations. Success and error bodies follow the shape found there; a new filter emits that shape, and the order registered filters run in is read from the repo, not assumed.

/api-design owns "one shape per API, held on every endpoint".

## Default for a repo with none

The envelope /api-design gives: `{ error: { code, message } }`.

```ts
@Catch()
export class HttpExceptionFilter implements ExceptionFilter {
  catch(exception: unknown, host: ArgumentsHost) {
    const response = host.switchToHttp().getResponse<Response>();

    if (exception instanceof HttpException) {
      return response.status(exception.getStatus()).json({
        error: { code: exception.name, message: exception.message },
      });
    }

    return response.status(500).json({
      error: { code: 'InternalServerError', message: 'Internal server error' },
    });
  }
}
```

## Whatever the envelope

Expected client errors are thrown as framework exceptions (`BadRequestException`, `NotFoundException`, …) or the repo's domain errors; unexpected failures are logged and wrapped centrally, so the internal message never crosses the boundary.

Server-sent event streams bypass exception filters: an SSE handler captures its own errors to the error tracker. A client disconnect surfaces as an `AbortError` — check `error.name` and drop it rather than reporting it.
