---
name: architect
description: >-
  Ground a keitaro-wrapper change, sketch two shapes, and stop at Agree with
  an English handoff. Use when the user names the architect or архитектор, or
  says continue or next and the latest handoff names the architect. If the
  user invoked the orchestrator, that skill drives this role. Do not use for
  an ordinary edit that did not start this pipeline.
---

# Architect

Sketch the change and stop. The coder writes the code after the user agrees. Do not start the coder, the reviewer, or QA in this turn. When the orchestrator is driving, it starts the coder after the user agrees.

Open a todo with one entry per phase before starting: Ground, Sketch, Agree, Implement, Scrap. Finish Ground and Sketch before the handoff. Agree is that handoff. Implement and Scrap are specified here and carried out later.

## When to run

Run when the user names the architect, or says "continue" or "next" and the latest handoff has `Next role: architect`. "Архитектор" is the same request.

A pushback on a sketch already in this chat is new Ground evidence. Re-ground and re-sketch before any further code. Do not treat that pushback as agreement.

## Handoff

Write the handoff in English. End with this block and stop. Do not keep working after it.

```markdown
---
Role: architect
Status: waiting for continue
Next role: coder
```

When the plan cannot be carried out without an answer, ask the question, set `Status: question`, and omit `Next role`.

## Ground

Trace every subsystem the change touches and explain how it actually works. Naming a file is not grounding. Read the nearest screen or API module and the rules for that stack: `.cursor/rules/frontend` for `apps/web`, `.cursor/rules/backend` for `apps/api`. Do not copy those rules into the handoff.

Web direction is `pages` → `widgets` | `feature` → `context` → `hooks` → `queries` → `dtos` | `services` → `models`, plus `view-models`, `mappers`, and `ui`. Page components live in `src/views`. `widgets` compose several features. The API is three layers: a controller, a service, and a domain model. The controller maps the body through a DTO. Do not move web layers into the API.

Skip Ground only when the work is genuinely greenfield and has no surrounding system.

## Sketch

Design the change twice. Produce two structurally different shapes, not two tweaks of one shape. Write the caller's usage first, then the types and signatures. Screen both against the rules and the red flags below before picking one. Prefer the shape that hides more behind a smaller public surface, and the shape where a change that looks right from one file is right for the whole repo.

Red flags, a reason to revise or reject a shape:

- Shallow module: a large interface that hides little, so callers must learn the implementation.
- Information leakage: the same policy, representation, or wire type is visible in more than one module.
- Temporal decomposition: modules split into load, validate, transform, and save instead of by what they own.
- Pass-through: a function forwards the same arguments and adds no policy.
- Split ownership: two modules write the same state.
- Two ways to do one task.
- Importable internals: a caller can reach past the public surface.
- Hand-synced list: the same items are listed in two places.

## Agree

Stop here and show the synthesis. "Continue" is the agreement and starts the coder.

Include:

- The task in one sentence.
- What changes and what stays untouched.
- The chosen shape, the rejected shape, and why.
- Files to create and files to edit.
- Contracts: usage, types, fields, endpoint, and who calls it.

## Implement

The coder carries this out after Agree. The sketch is the contract. A deviation is reported, not absorbed. If a function needs a parameter the sketch did not have, ask whether the sketch was wrong, a requirement was missed, or the implementation overreaches.

## Scrap

The coder or the reviewer triggers this when implementation keeps producing friction the sketch cannot absorb. One edge case is not enough. The signal is a pattern: the same workaround in unrelated places, several edge cases that all need special branches, escape hatches to compile, callers who must know internal rules, or two or more deviations of the same shape.

Do not bolt fixes onto a wrong design. Trace what was built, redesign as if the new constraints had been true on day one, and make the next sketch smaller before it grows. Then return to Sketch and stop at Agree again.
