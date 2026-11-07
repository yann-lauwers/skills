# The run

- Nothing reaches the owner mid-run: a question, a grant or a decision lands in `run.md` as an ask, a skip or a blocker.
- The run edits no product code, test, config or doc; its drivers and captures live in its run directory.
- Blocked at any step → write the head of `run.md` with verdict `BLOCKED`, the blocker and who must act, and a table holding at least every owner criterion; then steps 8–9.

1. Create the run directory, `<n>` one past today's highest.
2. Read the task per `references/plan.md` § Context, and the newest `run.md` with a verdict line. Done when the slice's direction fits one sentence.
3. `git rev-parse HEAD` is the brief's commit, and `git diff --stat <base>..<commit>` carries the change the ticket describes; otherwise blocked, on the builder.
4. Plan into `run.md` per `references/plan.md` and `references/run-md.md`. Done when every criterion has a plan, and each `prove` one a vehicle and an expected observation.
5. Preflight per `references/evidence.md` § Preflight; any failure → blocked.
6. Prove each `prove` criterion per `references/evidence.md`, then the walk where a vehicle is `browser` or `app`.
7. Grade into `run.md` per `references/run-md.md` § Grading. Done when every `prove` criterion has a verdict and its evidence paths.
8. HEAD is still the brief's commit and `git status --porcelain` prints nothing; otherwise blocked, naming what moved.
9. Stop every process the run started, then end on the final reply: the verdict line, then each FAIL, defect, ask, skip, `review` criterion and blocker, and anything left outside the run directory.
