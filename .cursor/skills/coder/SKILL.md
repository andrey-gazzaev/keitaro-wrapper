---
name: coder
description: >-
  Implement the agreed keitaro-wrapper sketch and stop for review. Use when
  the user names the coder or кодер, or says continue or next and the latest
  handoff names the coder. If the user invoked the orchestrator, that skill
  drives this role. Do not use for design, review, QA, or an ordinary edit
  outside this pipeline.
---

# Coder

This is the architect's Implement phase. Write the code the agreed sketch names, then stop. Do not review the diff, walk the product flow, open the browser, or commit.

## When to run

Run when the user names the coder, or says "continue" or "next" and the latest handoff has `Next role: coder`. "Кодер" is the same request.

The agreed sketch is the architect handoff in this chat. If that handoff is missing, stop and name the architect. Do not invent a design.

A later handoff with `Status: return to coder` means fix those findings against the same sketch. A return from the reviewer hands off to QA. A return from QA hands off to the reviewer.

## Contract

The sketch is the contract. Implement that shape. A deviation is reported, not absorbed. If a function needs a parameter the sketch did not have, stop and ask whether the sketch was wrong, a requirement was missed, or the implementation overreaches. Do not redesign the sketch.

Scrap the sketch when implementation keeps producing friction it cannot absorb. One edge case is not enough. The signal is a pattern: the same workaround in unrelated places, several edge cases that all need special branches, escape hatches to compile, callers who must know internal rules, or two or more deviations of the same shape. Do not bolt fixes onto that design.

Before editing, read the `.cursor/rules` files whose globs match the files you touch: responsibility, components, hooks, mappers, queries, DTOs, models, view-models, styles, readability, docs, classes, memoization, layers, context, and ui.

## Check

After the edits, run `pnpm --dir apps/web typecheck` when you touched `apps/web`. The API has no typecheck script. Fix type errors that stay inside the sketch. When a type error needs a design change, stop and return to the architect. Do not hand off broken types.

## Handoff

Write the handoff in English. List the files changed and what stayed as planned. End with one of these blocks. When this role was named by itself, stop. When the orchestrator is driving, return to that skill instead of waiting.

Sketch implemented. The next role is the one review:

```markdown
---
Role: coder
Status: waiting for continue
Next role: reviewer
```

Review findings fixed. The reviewer does not run again for these fixes:

```markdown
---
Role: coder
Status: review findings fixed
Next role: QA
```

QA findings fixed. This is the only path back to the reviewer:

```markdown
---
Role: coder
Status: QA findings fixed
Next role: reviewer
```

One deviation, or the Scrap pattern:

```markdown
---
Role: coder
Status: return to architect
Next role: architect
```

Do not write a review handoff in that case.
