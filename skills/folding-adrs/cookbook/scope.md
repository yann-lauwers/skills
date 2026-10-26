# Scope and orient

1. Say the target back to the owner — a request to clean up ADRs reads easily as removing only their citations — and take the owner's word on which ADRs are in. Done when the owner has confirmed it.
2. The owner asks for a ticket for the round → file it on the tracker, with the ADRs' numbers and the acceptance line "`git ls-files <ADR dir>` lists none of them". Done when it exists, or the owner asked for none.
3. Cut a worktree for the round from `origin/<base>` through /worktrunk , then run the repo's setup command there. Done when setup exits 0.
4. Read `GLOSSARY.md` and every ADR in scope whole, by full path in this tree. Done when the read-first gate passes.
5. List what else moves the same files right now — open pull requests and running branches — so the round knows who it will collide with. Done when the list is written in the ticket, or, with no ticket, in the reply.
