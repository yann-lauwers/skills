---
name: loop-me
description: >-
  Grills the specs for a workflow being built in this workspace — inputs, outputs, where it stops,
  what it does when a step fails. Use on "loop me", "grill the workflow", "spec this automation",
  "what should this workflow do", "what could I delegate", a repeatable process to be built, or
  before authoring a workflow, cron or multi-step automation from an unspecified brief or writing
  a `workflows/*.md` spec. Not for a non-workflow design — /grilling ; not for a Workflow tool
  script — /workflow-authoring ; not for arming a settled recurring run — /schedule or /loop .
argument-hint: "[workflow]"
---

# Loop Me

- Run a stateful /grilling session whose only output is workflow specs; create, edit and delete specs as the grilling resolves them.

## The loop lens

- Loop — a recurring pattern in the user's life: their career, their week, their morning, one repeated activity; loops within loops show how predictable its activities are, which makes them worth delegating.
- Find loops worth specifying, and propose ones the user hasn't noticed.
- Workflow — the spec of one loop; the loop is the workflow's running instance.
- Workflows are the source of truth.

## Vocabulary

- Reach for a term only when a workflow calls for it; never a checklist.
- Mandate nothing structural: a workflow needs no AI, no checkpoint and no schedule unless the grilling shows it does.
- Trigger — what fires each run: an event (a new email, a new issue) or a schedule (every morning); an event is usually the more efficient.
- Checkpoint — a point where the user is asked to verify or decide.
- Push right — defer the checkpoint as far as it goes: maximal work first, so the user is asked once, late, with everything prepared.
- Brief — what a checkpoint presents: a tight, decision-ready summary of what was produced and why, linking to the asset itself; never the raw output or a draft.

## Definition of done

- A spec is done when an implementer agent could build it without asking a single question; grill until then.

## The workspace

- `workflows/*.md` — one spec per workflow.
- `NOTES.md` — raw notes on the user's world: the tools they use, the channels they process, and their own terms for both.
- `NOTES.md` empty or thin → interview the user about their world before specifying anything.
- A fuzzy term surfacing → sharpen it into a canonical one and record it in `NOTES.md`.
