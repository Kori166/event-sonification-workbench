# Progress Log

I use this log to record completed work, decisions, problems, actions and next steps. I will keep entries brief and add them when the project state changes materially.

## Entry Template

### YYYY-MM-DD

**Work completed**

- I ...

**Decisions made**

- I decided ...

**Problems or risks**

- I identified ...

**Actions taken**

- I ...

**Next actions**

- I will ...

---

## 2026-07-28 — Stage 0 completion

**Work completed**

- I created the fresh `event-sonification-workbench` repository.
- I added the README, Python project configuration, environment example and ignore rules.
- I added the package scaffold, command-line entry point and smoke test.
- I corrected the README structure and installation guidance.
- I added the project plan, progress log, risk register and supervision log.
- I created Stage 1 Issues #1 to #4.
- I marked Stage 0 as complete.

**Decisions made**

- I decided to use GitHub Issues, commits and project records as evidence of project management.
- I kept MOT17 and KITTI Tracking as the core dataset scope.
- I decided to store full datasets locally rather than commit them to GitHub.
- I decided to begin Stage 1 with the common event schema and MOT17 parser.

**Problems or risks**

- I found that CI initially failed because the smoke-test file was empty and no test was collected.
- I recognised that the previous repository deletion had reduced the remaining development time.

**Actions taken**

- I added a valid package import test and the package files required by `pyproject.toml`.
- I added scope and data-loss risks to the risk register.

**Next actions**

- I will begin Stage 1 by defining the common event schema.

---

## 2026-07-28 — Stage 1 initiation

**Work completed**

- I reviewed repository readiness after Stage 0 completion.
- I marked Stage 1 as in progress in the README and project plan.
- I added a Stage 1 work order and completion criteria.
- I added decision records for project scope, dataset storage, Python package layout, implementation order and project-management evidence.
- I added Stage 1 Issues #5 and #6 for KITTI parsing and structured event and provenance outputs.
- I reviewed and extended the risk register.

**Decisions made**

- I decided to use a schema-first implementation sequence before treating dataset-specific parsers as stable.
- I kept the installable Python package under `src/event_sonification_workbench/`.
- I decided to keep full datasets outside Git and commit only small documented fixtures where permitted.
- I decided to evaluate the workbench technically without making participant-based accessibility claims.

**Problems or risks**

- I identified a risk that a schema designed only around MOT17 could require disruptive changes when I add KITTI Tracking.
- I identified a risk that GitHub Issues and project records could drift from the actual implementation status.

**Actions taken**

- I added these risks and mitigations to the risk register.
- I recorded the significant decisions under `docs/decisions/`.
- I added a Stage 1 checklist and project-management index.

**Next actions**

- I will complete Issue #1 by defining the common event schema.
- I will complete Issue #3 by creating the fixed MOT17 test fixture.
- I will implement and test the MOT17 parser under Issue #2.
- I will implement the KITTI Tracking parser under Issue #5.
- I will add validation and provenance outputs under Issues #4 and #6.

---

## 2026-07-29 — Stage 1 Milestone 1: schema and synthetic fixture

**Work completed**

- I added provisional common event schema version `0.1.0` under `configs/schemas/`.
- I added a documented synthetic source annotation and manually constructed expected event under `tests/fixtures/synthetic/`.
- I added deterministic event-ID, canonical hashing and event-validation modules under `src/event_sonification_workbench/`.
- I added automated tests for schema validity, semantic calculations, source traceability and deterministic hashing.
- I added the common-event data-model document and Decision 0006.
- I ran the complete local test suite successfully, with eight tests passing.

**Decisions made**

- I decided to keep the common event as a flat record to simplify parser outputs and later JSON and CSV export.
- I decided to use a zero-based common frame and derive timestamps in seconds from the declared frame rate.
- I decided to store native and common object classes separately.
- I retained schema version `0.1.0` as provisional until I have reviewed it against both real datasets.
- I decided to permit out-of-frame normalised centres and report them as warnings rather than reject potentially valid truncated annotations.

**Problems or risks**

- I cannot use the synthetic fixture as evidence of compatibility with MOT17 or KITTI Tracking.
- I still need to resolve the common class vocabulary and treatment of KITTI-specific quality fields.
- I could conceal later schema changes if I treat the initial schema task as permanently closed rather than provisionally complete.

**Actions taken**

- I recorded the provisional status and open questions in the data-model document and Decision 0006.
- I kept the separate MOT17 fixture and parser work outstanding.
- I added an explicit checklist item requiring cross-dataset review before schema version `1.0.0`.

**Next actions**

- I will review the provisional schema against the exact MOT17 and KITTI Tracking field definitions.
- I will complete the fixed MOT17 fixture under Issue #3.
- I will implement the first MOT17 row-to-event vertical slice under Issue #2.
- I will revisit Decision 0006 if parser evidence requires a schema change.
