# Driving a new component from its tests

The order the first tests arrive in when the component or hook does not exist yet; the loop itself belongs to /tdd .

1. Name the component's prop type and signature — the contract the first test asserts against.
2. Write the first test for the simplest case.
3. Run every case, the first included, through /tdd 's loop.
