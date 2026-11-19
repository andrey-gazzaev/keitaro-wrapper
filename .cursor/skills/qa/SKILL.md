---
name: qa
description: >-
  Run keitaro-wrapper tests and the web browser flow, then stop with an
  English report. Use when the user names QA, or says continue or next and
  the latest handoff names QA. If the user invoked the orchestrator, that
  skill drives this role. Do not use for design, implementation, review, or
  an ordinary edit outside this pipeline.
---

# QA

Run the checks and write the report. Do not edit code, review the design, or commit.

## When to run

Run when the user names QA, or says "continue" or "next" and the latest handoff has `Next role: QA`.

That handoff is the reviewer's `Status: ready for QA`, or the coder's `Status: review findings fixed`. Both mean the review already happened. If the review has not happened, stop and name the reviewer. Run anyway when the user explicitly says to skip review.

## Checks

Run the tests for the packages the change touches.

API tests use the in-memory SQLite database from `tests/conftest.py`:

```bash
cd apps/api && .venv/bin/pytest
```

Web tests use Vitest and Testing Library:

```bash
cd apps/web && pnpm test
```

When the change touches the UI, exercise the flow in the browser at http://127.0.0.1:5173. Cover the affected path, neighboring screens that share the state, and the empty and error states.

A failure is a report. Do not fix it.

## Handoff

Write the handoff in English. Say what ran, what passed, and what failed. End with one of these blocks. When this role was named by itself, stop. When the orchestrator is driving, return to that skill instead of waiting.

A failure:

```markdown
---
Role: QA
Status: return to coder
Next role: coder
```

A pass:

```markdown
---
Role: QA
Status: done
```
