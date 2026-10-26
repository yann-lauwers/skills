# Link bank rows and orders

1. Pair them: `billit bank reconcile`.
2. Show the user every `unique` pair and every `ambiguous` row with its candidates; a matching amount alone can be a coincidence.
3. Assign what the user confirms: `billit bank assign <row> <order>`.
4. Rows with no order and orders with no row → list them for the user; never pair them by guess.

Report: the entity, the pairs assigned, then the rows and orders left for the user.
