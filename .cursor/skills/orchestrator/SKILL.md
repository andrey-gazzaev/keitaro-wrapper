---
name: orchestrator
description: >-
  Drive the keitaro-wrapper pipeline from architect through coder, reviewer,
  and QA. Use when the user names the orchestrator or оркестратор, or says
  continue or next after a handoff this skill produced. Do not use when the
  user named a single role, or for an ordinary edit outside this pipeline.
---

# Orchestrator

One entry for the pipeline. The role skills describe the work. This skill decides which role runs next. A role named by itself still stops after its own handoff. Do not take over a chat that started with a single role.

## When to run

Run when the user names the orchestrator, or says "continue" or "next" after a handoff this skill produced. "Оркестратор" is the same request.

A single role name means that role runs alone. Do not drive the rest.

## Drive

Read the current role's skill and do its work. Write that role's handoff, then start the role in `Next role` in the same turn. The user does not type continue between coder, reviewer, and QA. Do not commit.

1. Follow [architect](../architect/SKILL.md) through Agree. Stop and show the synthesis. Continue is the agreement.
2. Follow [coder](../coder/SKILL.md). `Next role: reviewer` goes to step 3. `Next role: QA` goes to step 4. That second path is the coder fixing this review, and it skips the reviewer.
3. Follow [reviewer](../reviewer/SKILL.md) once. `Next role: coder` returns to step 2, and the following coder handoff names QA, so go to step 4. Do not review those fixes. `Next role: architect` returns to step 1 and stops again at Agree. `Next role: QA` goes to step 4.
4. Follow [qa](../qa/SKILL.md). A failure returns to step 2, and that coder handoff names the reviewer. That is the only repeat of step 3. `Status: done` stops the pipeline. Do not commit.

## Stop and wait

Stop, even while driving, when:

- The architect's status is `question`.
- The architect is at Agree, until the user continues.
- The same return, to the coder or the architect, happens a second time for the same findings. Report that and wait.
- QA status is done.

A pushback on the sketch is new Ground evidence. Re-ground, re-sketch, and stop at Agree again.
