# Progress Log

This log records project activity, decisions, problems and next actions. Entries should be brief and added regularly.

## Entry Template

### YYYY-MM-DD

**Work completed**

- 

**Decisions made**

- 

**Problems or risks**

- 

**Actions taken**

- 

**Next actions**

- 

---

## 2026-07-28 — Stage 0 completion

**Work completed**

- Created the fresh `event-sonification-workbench` repository.
- Added the README, Python project configuration, environment example and ignore rules.
- Added the package scaffold, command-line entry point and smoke test.
- Corrected the README structure and installation guidance.
- Added the project plan, progress log, risk register and supervision log.
- Created Stage 1 Issues #1 to #4.
- Marked Stage 0 as complete.

**Decisions made**

- Use GitHub Issues, commits and project records as evidence of project management.
- Keep MOT17 and KITTI Tracking as the core dataset scope.
- Store full datasets locally rather than committing them to GitHub.
- Begin Stage 1 with the common event schema and MOT17 parser.

**Problems or risks**

- CI initially failed because the smoke-test file was empty and no test was collected.
- The previous repository deletion has reduced the remaining development time.

**Actions taken**

- Added a valid package import test and the package files required by `pyproject.toml`.
- Added scope and data-loss risks to the risk register.

**Next actions**

- Begin Stage 1 by defining the common event schema.

---

## 2026-07-28 — Stage 1 initiation

**Work completed**

- Reviewed repository readiness after Stage 0 completion.
- Marked Stage 1 as in progress in the README and project plan.
- Added a Stage 1 work order and completion criteria.
- Added decision records for project scope, dataset storage, Python package layout, implementation order and project-management evidence.
- Reviewed and extended the risk register.

**Decisions made**

- Use a schema-first implementation sequence before dataset-specific parsers are treated as stable.
- Keep the installable Python package under `src/event_sonification_workbench/`.
- Keep full datasets outside Git and commit only small documented test fixtures where permitted.
- Evaluate the workbench technically without making participant-based accessibility claims.

**Problems or risks**

- A schema designed only around MOT17 could require disruptive changes when KITTI Tracking is added.
- Project records may drift from implementation status unless updated when issues are closed.

**Actions taken**

- Added these risks and mitigations to the risk register.
- Recorded significant decisions under `docs/decisions/`.
- Added a Stage 1 checklist and project-management index.

**Next actions**

- Complete Issue #1: define the common event schema.
- Complete Issue #3: create the fixed MOT17 test fixture.
- Implement and test the MOT17 parser under Issue #2.
- Add normalised event validation under Issue #4.
- Create further issues before beginning KITTI parsing and provenance-output implementation.
