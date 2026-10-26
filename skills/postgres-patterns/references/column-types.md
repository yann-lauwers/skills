# Column types

| Value | Type | Never |
| --- | --- | --- |
| Primary key | `bigint` (identity) | `int` — it runs out at 2.1 billion; random UUID v4 — inserts land at random leaf pages and fragment the B-tree |
| String | `text` | `varchar(255)` — the limit is arbitrary and enforces nothing the domain asked for |
| Timestamp | `timestamptz` | `timestamp` — it records wall-clock digits with no instant behind them; `timestamptz` stores the instant in UTC and renders it in the session's `TimeZone` |
| Money | `numeric(precision, 2)`, precision sized to the largest amount the column will ever hold | `float` / `double precision` — binary fractions cannot represent 0.10 |
| Flag | `boolean` | `varchar`, `int` |

- A deviation from the table → stated where the column is declared.
- Changing an existing column's type → /database-migrations .
