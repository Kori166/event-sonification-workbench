# Progress Log

This log records completed work, decisions, problems, actions and next steps. Entries should remain brief and should be added when the project state changes materially.

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

- Created the new `event-sonification-workbench` repository.
- Added the README, Python project configuration, environment example and ignore rules.
- Added the package scaffold, command-line entry point and smoke test.
- Corrected the README structure and installation guidance.
- Added the project plan, progress log, risk register and supervision log.
- Created Stage 1 Issues #1 to #4.
- Marked Stage 0 as complete.

**Decisions made**

- GitHub Issues, commits and project records will provide evidence of project management.
- MOT17 and KITTI Tracking remain the core dataset scope.
- Full datasets will be stored locally rather than committed to GitHub.
- Stage 1 will begin with the common event schema and MOT17 parser.

**Problems or risks**

- CI initially failed because the smoke-test file was empty and no test was collected.
- The previous repository deletion reduced the remaining development time.

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
- Added Stage 1 Issues #5 and #6 for KITTI parsing and structured event and provenance outputs.
- Reviewed and extended the risk register.

**Decisions made**

- A schema-first implementation sequence will be used before dataset-specific parsers are treated as stable.
- The installable Python package will remain under `src/event_sonification_workbench/`.
- Full datasets will remain outside Git. Only small documented fixtures may be committed where permitted.
- The workbench will be evaluated technically without participant-based accessibility claims.

**Problems or risks**

- A schema designed only around MOT17 could require disruptive changes when KITTI Tracking is added.
- GitHub Issues and project records could drift from the actual implementation status.

**Actions taken**

- Added these risks and mitigations to the risk register.
- Recorded the significant decisions under `docs/decisions/`.
- Added a Stage 1 checklist and project-management index.

**Next actions**

- Complete Issue #1 by defining the common event schema.
- Complete Issue #3 by creating the fixed MOT17 test fixture.
- Implement and test the MOT17 parser under Issue #2.
- Implement the KITTI Tracking parser under Issue #5.
- Add validation and provenance outputs under Issues #4 and #6.

---

## 2026-07-29 — Stage 1 Milestone 1: schema and synthetic fixture

**Work completed**

- Added provisional common event schema version `0.1.0` under `configs/schemas/`.
- Added a documented synthetic source annotation and manually constructed expected event under `tests/fixtures/synthetic/`.
- Added deterministic event-ID, canonical hashing and event-validation modules under `src/event_sonification_workbench/`.
- Added automated tests for schema validity, semantic calculations, source traceability and deterministic hashing.
- Added the common-event data-model document and Decision 0006.
- Ran the complete local test suite successfully, with eight tests passing.

**Decisions made**

- The common event will use a flat record to simplify parser outputs and later JSON and CSV export.
- The common frame index will be zero-based. Timestamps will be derived in seconds from the declared frame rate.
- Native and common object classes will be stored separately.
- Schema version `0.1.0` will remain provisional until it has been reviewed against both real datasets.
- Out-of-frame normalised centres will be permitted and reported as warnings rather than rejected automatically.

**Problems or risks**

- The synthetic fixture cannot provide evidence of compatibility with MOT17 or KITTI Tracking.
- The common class vocabulary and treatment of KITTI-specific quality fields remain unresolved.
- Later schema changes could be concealed if the initial schema task is treated as permanently complete rather than provisionally complete.

**Actions taken**

- Recorded the provisional status and open questions in the data-model document and Decision 0006.
- Kept the separate MOT17 fixture and parser work outstanding.
- Added an explicit checklist item requiring cross-dataset review before schema version `1.0.0`.

**Next actions**

- Review the provisional schema against the exact MOT17 and KITTI Tracking field definitions.
- Complete the fixed MOT17 fixture under Issue #3.
- Implement the first MOT17 row-to-event vertical slice under Issue #2.
- Revisit Decision 0006 if parser evidence requires a schema change.
