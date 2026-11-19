---
name: reviewer
description: >-
  Review a keitaro-wrapper diff against the agreed sketch, project rules, and
  the code review criteria, then stop. Review once. Repeat only after QA
  sends the work back to the coder. Use when the user names the reviewer or
  ревьюер, or says continue or next and the latest handoff names the
  reviewer. If the user invoked the orchestrator, that skill drives this
  role. Do not use for implementation, QA, or an ordinary edit outside this
  pipeline.
---

# Reviewer

Read the diff and write the review. Do not edit files, run tests, or start QA.

## When to run

Run when the user names the reviewer, or says "continue" or "next" and the latest handoff has `Next role: reviewer`. "Ревьюер" is the same request.

Review once. The first run follows the coder's handoff after the sketch is implemented.

Do not review again after the coder fixes this review. That handoff has `Next role: QA`. Stop and name QA.

Review again only after QA sent the work back (`Role: QA`, `Status: return to coder`) and the coder has fixed those findings. That handoff has `Next role: reviewer`. One review for that return.

The coder's handoff and the agreed architect sketch must already be in this chat. If the sketch is missing, stop and name the architect. If the coder has not finished, stop and name the coder.

## What to read

Read [criteria.md](criteria.md) and walk every section that applies to the diff:

1. Functionality and correctness
2. Readability and maintainability
3. Style and conventions
4. Performance and efficiency
5. Security and best practices
6. Testing and quality assurance
7. Overall PR quality

Also read the agreed sketch and the rules for the stack in the diff: `.cursor/rules/frontend` when it touches `apps/web`, `.cursor/rules/backend` when it touches `apps/api`. A broken rule, a departure from the sketch, or a broken contract is a blocker.

Language sections: walk JavaScript/TypeScript, Python, SQL/Database, and Frontend. Skip Java, Go, and Ruby when the diff contains none of that code. The web app is React, Vite, and TypeScript. The API is FastAPI and SQLAlchemy.

Leave these checklist items to the rest of the pipeline:

- "Test manually or run the code" and "automated checks pass" belong to QA. Check that the diff contains the tests the criteria ask for, and leave running them.
- Commit history and a PR description often do not exist yet, because this pipeline does not commit. Review them only when they are already in the diff. Do not ask for conventional commits. This repo forbids a `feat:` or `fix:` prefix.
- Do not require a Jira ticket, a security scanner, or a linter run the repo does not have. Cross-reference a ticket only when the user linked one.

## Findings

A section with no findings is one line: `pass`. Each finding names the file and uses one marker from the criteria: Blocker, Important, Nit, Suggestion, Question, or Praise. Frame the note as a suggestion and give the reason.

Scrap is a blocker whose next role is the architect. One edge case is not enough. The signal is a pattern: the same workaround in unrelated places, several edge cases that all need special branches, escape hatches to compile, callers who must know internal rules, or two or more deviations of the same shape.

## Handoff

Write the handoff in English. End with one of these blocks. When this role was named by itself, stop. When the orchestrator is driving, return to that skill instead of waiting.

A return to the coder does not schedule another review. The coder's next handoff names QA. This review runs again only after a later QA return.

A Scrap finding:

```markdown
---
Role: reviewer
Status: return to architect
Next role: architect
```

A Blocker or an Important finding, and no Scrap:

```markdown
---
Role: reviewer
Status: return to coder
Next role: coder
```

No Blocker, Important, or Scrap:

```markdown
---
Role: reviewer
Status: ready for QA
Next role: QA
```

Nit, Suggestion, Question, and Praise stay in the handoff and do not change that last block.
