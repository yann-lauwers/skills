---
name: persona-forging
description: >-
  Builds a persona for an agent, or for the main session out of the owner's own transcripts, and
  lands it in the target's file. Use on "give this agent a personality", "create a persona", "make
  it talk like X", "build my persona", "tune your voice", "you sound wrong", or a real or fictional
  figure an agent should become; also when an agent's voice or register is about to be set by hand
  rather than derived from evidence. Not for an agent's mandate, tools, model or description —
  /managing-harness .
---

# Persona Forging

Owns who an agent, or the main session, is: one grid filled from evidence, then landed in the target's file.

## Routing table

| Intent | Read |
| --- | --- |
| IF the subject is the owner, or anyone whose words this machine already holds | THEN `cookbook/mine-transcripts.md` |
| IF the subject is a real public figure, or a fictional one | THEN `cookbook/research-a-figure.md` |
| IF the source lane left grid rows empty or surfaced contradictions | THEN § Grilling lane |
| IF the Register row has to be chosen | THEN § The benchmark |
| IF every grid row holds an answer | THEN § Landing it |

## Order

- Every persona runs one source lane, then the grilling; never either alone.
- The source lane settles how the figure talks · the grilling settles which parts of that survive contact with the work.
- Pick the source lane by where the material lives; both lanes fill the same grid.
- Source lane before grilling → never spend a user turn on a question the evidence answers.

## Grilling lane

- Run /grilling over the grid, one question at a time, each carrying a recommended answer.
- It covers every grid row the source lane could not fill, and every contradiction it surfaced.

## The grid

- A persona is complete when every row holds an answer.
- A row nobody can fill → ask it in the grilling; never ship a blank row.

| Row | What it settles |
| --- | --- |
| Name | what the agent calls itself, and what it answers when asked who it is |
| Source | which lane produced the material, and what it was drawn from |
| Register | the level, fixed by § The benchmark — never by an adjective |
| Praise policy | whether it evaluates the person it is talking to, and how |
| Lean policy | whether it leads with a recommendation or lays out a neutral menu |
| Humour bar | what a joke is allowed to cost |
| How it disagrees | the move it makes when the evidence contradicts the user |
| Ritual | anything it does at a fixed moment — an opening, a sign-off — and the register exception that permits it |
| Vocabulary | names, address forms, catchphrases, the words it reaches for |
| Refuses to | the behaviours it will not produce, whatever it is asked |
| Failure mode | how this persona drifts when it degrades, so the agent can self-correct |

- An agent's job mandate, a reviewer's adversarial brief included, is never a grid row → it stays in the job; the persona settles voice and how a finding is delivered.

## The benchmark

- Never offer a register as a label, a level number or an adjective.
- Write the same reply four times, once per candidate register, across three scenarios:
  1. The user proposes something with a real flaw → tests whether the persona can criticise.
  2. Work is finished and needs reporting → tests density, evidence, and what it shows.
  3. The user is wrong and the persona has the evidence → tests whether disagreement survives the register at all.
- Then score each register on what it costs, in a table.
- The user picks a written reply, never a description of one.
- Scenario 3 decides most personas → a warm register loses disagreement before anything else, and only a written reply shows the loss.

## Landing it

1. Fill the grid.
2. Write the persona in the agent-file shape the target uses: an opening paragraph naming who it is · the numbered policies under a heading · the failure mode in the paragraph after them · an examples section carrying one ✅ per policy and one ❌ per failure mode.
3. A policy with no written example → write one before landing.
4. Route the edit through /managing-harness , which owns the agent contract.
5. Dogfood it: run the agent once on real work and read the output against the grid.

## Scope

- A persona covers character only: voice · register · humour · refusals · failure mode.
- An agent's mandate, tool list, model and the comprehension floor every reply inherits → the agent contract and canon, via /managing-harness ; name them, edit neither.
