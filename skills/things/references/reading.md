# Reading

- Filter on a list, never on the application → `to dos of list "Today" whose name is "X"` resolves; `every to do whose name is "X"` raises `-1728`.
- Ask a whose-clause for a property, never for the objects → `id of every to do of list "Today" whose name is "X"` returns a list of ids.
- Mutating inside a loop over the objects invalidates the specifier mid-repeat → collect ids first, then act by id.
- `project of t` and `area of t` raise when the to-do belongs to neither → wrap each access in `try`.
- An absent `due date` reads back as `missing value` and raises nothing, so a `try` never fires → test `if due date of t is not missing value then …` before formatting.
- A listing shows a due date only where one exists and says nothing where none does.
- An item scheduled for today appears in both `Today` and `Anytime` → deduplicate by id when reading across lists.
