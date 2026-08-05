# Progress Log

This log records completed work, decisions, problems, actions and next steps. Entries should remain
brief and should be added when the project state changes materially. Detailed milestone records may
be added where a short entry would omit important implementation evidence.

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
- Added decision records for project scope, dataset storage, Python package layout,
  implementation order and project-management evidence.
- Added Stage 1 Issues #5 and #6 for KITTI parsing and structured event and provenance outputs.
- Reviewed and extended the risk register.

**Decisions made**

- A schema-first implementation sequence will be used before dataset-specific parsers are treated
  as stable.
- The installable Python package will remain under `src/event_sonification_workbench/`.
- Full datasets will remain outside Git. Only small documented fixtures may be committed where
  permitted.
- The workbench will be evaluated technically without participant-based accessibility claims.

**Problems or risks**

- A schema designed only around MOT17 could require disruptive changes when KITTI Tracking is
  added.
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
- Added a documented synthetic source annotation and manually constructed expected event under
  `tests/fixtures/synthetic/`.
- Added deterministic event-ID, canonical hashing and event-validation modules under
  `src/event_sonification_workbench/`.
- Added automated tests for schema validity, semantic calculations, source traceability and
  deterministic hashing.
- Added the common-event data-model document and Decision 0006.
- Ran the complete local test suite successfully, with eight tests passing.

**Decisions made**

- The common event will use a flat record to simplify parser outputs and later JSON and CSV export.
- The common frame index will be zero-based. Timestamps will be derived in seconds from the
  declared frame rate.
- Native and common object classes will be stored separately.
- Schema version `0.1.0` will remain provisional until it has been reviewed against both real
  datasets.
- Out-of-frame normalised centres will be permitted and reported as warnings rather than rejected
  automatically.

**Problems or risks**

- The synthetic fixture cannot provide evidence of compatibility with MOT17 or KITTI Tracking.
- The common class vocabulary and treatment of KITTI-specific quality fields remain unresolved.
- Later schema changes could be concealed if the initial schema task is treated as permanently
  complete rather than provisionally complete.

**Actions taken**

- Recorded the provisional status and open questions in the data-model document and Decision 0006.
- Kept the separate MOT17 fixture and parser work outstanding.
- Added an explicit checklist item requiring cross-dataset review before schema version `1.0.0`.

**Next actions**

- Review the provisional schema against the exact MOT17 and KITTI Tracking field definitions.
- Complete the fixed MOT17 fixture under Issue #3.
- Implement the first MOT17 row-to-event vertical slice under Issue #2.
- Revisit Decision 0006 if parser evidence requires a schema change.

---

## 2026-07-29 — Stage 1 Milestone 2 implementation: MOT17 vertical slice

**Work completed**

- Implemented the MOT17 ground-truth adapter and sequence-metadata parser.
- Added the provisional MOT17 class mapping and configuration hashes.
- Added controlled valid and invalid MOT17-format rows for unit testing.
- Added a local `mot17-check` command for parser and event-validation summaries.
- Added deterministic extraction of explicit source rows into a fixture with a provenance manifest.
- Extended event validation to resolve source files from a configured dataset root.
- Added adapter, command-line, fixture-extraction and common-schema integration tests.
- Added Decision 0007, adapter documentation and a detailed Milestone 2 work log.
- Ran the combined Milestone 1 and Milestone 2 local suite successfully, with 20 tests passing.

**Decisions made**

- The adapter will accept the nine-column MOT17 ground-truth format only.
- The provisional implementation converted frames and bounding-box origins. Real-data review on
  4 August 2026 retained frame conversion but superseded the coordinate-origin conversion.
- The MOT17 ground-truth evaluation mark will remain in metadata and will not be used as common
  confidence.
- Structurally valid marked and unmarked rows will be retained during ingestion.
- A real-data fixture and local sequence run are required before Milestone 2 can be completed.

**Problems or risks**

- The earlier branch-building environment did not have access to the local dataset. The files were
  available during the 4 August 2026 real-data review.
- The `conf` name used in format descriptions can be mistaken for detector confidence even though
  the ground-truth value is an evaluation mark.
- MOT17 ground truth and tracker-result files use different field counts.
- A dataset-derived fixture cannot be selected responsibly without inspecting the source rows and
  redistribution conditions.

**Actions taken**

- Recorded the semantic and indexing decisions in Decision 0007.
- Added strict field-count and value validation with structured row diagnostics.
- Added a synthetic format fixture while clearly excluding it from real-data evidence.
- Added a deterministic fixture-extraction command that records source rows and hashes.
- Updated the risk register and milestone completion criteria.

**Next actions**

- Obtain `seqinfo.ini` and `gt/gt.txt` for the selected local MOT17 sequence.
- Inspect and select representative physical rows for the fixed fixture.
- Generate the dataset-derived fixture and expected common events.
- Run `mot17-check` against the real sequence.
- Run the complete suite in CI and then review Issues #2 and #3 for closure.

---

## 2026-08-04 — Stage 1 Milestone 2 real-data verification

**Work completed**

- Inspected `MOT17-02-DPM` sequence metadata and all 30,003 ground-truth rows.
- Recorded a deterministic 12-line real-data selection and both source and generated hashes.
- Added manifest-driven private fixture generation under an ignored directory.
- Replaced the five-row format sample with a 12-row structurally equivalent synthetic fixture.
- Added independently calculated expected-event projections and controlled malformed rows.
- Corrected coordinate preservation, authoritative class support and out-of-frame warnings.
- Added unit, golden, determinism, command-line and private integration tests.
- Completed the MOT17 adapter, mapping, decision, fixture and development documentation.

**Decisions made**

- Native bounding-box coordinates are preserved; only the frame index is converted.
- The ground-truth evaluation mark remains metadata and common confidence remains `null`.
- Native class identifiers outside the authoritative range 1 to 12 are rejected.
- Copied MOT17 rows remain outside Git because redistribution permission is unresolved.
- A committed manifest and synthetic CI fixture provide reproducibility without claiming permission.

**Problems or risks**

- Rebuilt `origin/main` and the legacy local `main` had no common ancestor.
- GitHub CLI was unavailable.
- Windows line endings invalidated the existing synthetic source hash.
- The first full event-validation command timed out because the same source file was re-hashed for
  every event.
- Issue #3 cannot close while the fixture redistribution criterion remains unresolved.

**Actions taken**

- Preserved the legacy worktree artefacts and used the rebuilt remote history without joining it.
- Used connected GitHub operations where the absent CLI would otherwise be required.
- Enforced LF for hashed fixture files and normalised the affected source fixture.
- Cached the compiled schema and source hash within a validation run without removing checks.
- Recorded the licence limitation explicitly and kept dataset-derived rows ignored.

**Validation evidence**

- Normal tests: 45 passed and 1 integration test deselected.
- Real-data integration selection: 1 passed and 45 tests deselected.
- Complete suite: 46 passed twice, with zero failures, skips or pytest warnings.
- Full real sequence: 30,003 valid events, zero invalid events and 988 geometry warnings.
- Fixture generation: 12 rows with SHA-256
  `a4d5ec744f02febec5a2887080cc95c2f49b09189fa600d2e37c3252210f835f`.
- Ruff: passed.
- GitHub Actions CI run 28: passed on implementation head `d17e891`.
- Repeated synthetic conversion: identical order, event IDs, canonical JSON and event hashes.

**Remaining work**

- Complete the final documentation-only branch CI check before merge.
- Issue #2 closed after all parser acceptance criteria were evidenced.
- Keep Issue #3 and Milestone 2 open until the redistribution criterion is resolved.
- Do not begin KITTI implementation until the Milestone 2 status is settled.

**Next actions**

- Publish and review the MOT17 parser changes.
- Resolve the fixture redistribution or acceptance-criterion question recorded in Issue #3.
- Begin Milestone 3 only after Milestone 2 can be marked complete.

---

## 2026-08-05 — Stage 1 Milestone 3 KITTI Tracking extension

**Work completed**

- Audited the configured KITTI Tracking root before implementation and discovered the actual
  `training/label_02` layout, sequences `0000`–`0020`, 17-field rows and missing local terms files.
- Reviewed the official KITTI tracking format, evaluation implementation, sensor rate, copyright,
  attribution and licence sources.
- Selected 12 deterministic rows from training sequence `0000` and recorded original source lines,
  field order, method, source/fixture hashes, metadata, attribution and CC BY-NC-SA 3.0 terms.
- Added separately identified synthetic malformed rows.
- Implemented explicit 17/18-field KITTI parsing, coded structured diagnostics, class mapping,
  common-event conversion, source provenance and sequence-image metadata inspection.
- Preserved `DontCare` as explicit events and retained truncation, occlusion, alpha, 3D geometry,
  rotation and optional scores.
- Added schema `0.2.0`, retaining the event shape and relaxing only the native confidence range.
- Updated the common schema, adapter, decisions, milestone evidence, project plan, checklist, risks,
  fixture documentation and README.

**Decisions made**

- KITTI source frames remain zero-based common frames; timestamps use the official 10 Hz rate.
- Right/bottom coordinates become width/height through subtraction and are treated as continuous
  edges that may equal image width/height.
- `DontCare` rows are not silently filtered; later processing must record any exclusion.
- Occlusion is not converted to a fabricated MOT17-style visibility ratio.
- Optional KITTI scores are preserved without clipping or probability semantics.
- Schema 0.1.0 remains historical; both adapters now emit 0.2.0.

**Problems and actions**

- The process environment did not initially inherit the ignored local root configuration. The
  value was exported only into private integration commands, and no absolute path was committed.
- PowerShell did not provide `Path.GetRelativePath`; audit reporting used a root-relative fallback.
- An initial integration assertion exposed nine boundary alerts. All ended exactly at image width
  or height, so the check was aligned with continuous right/bottom edge geometry and the common
  validator. The final run had zero warnings; truly outside geometry still warns.
- GitHub CLI remained unavailable. Implementation and local evidence were completed; publication
  uses the connected capability if available or remains explicitly blocked.

**Validation evidence**

- Ruff: `ruff check .` passed.
- Non-integration suite: 76 passed, 2 deselected.
- Dedicated KITTI integration: 1 passed.
- All private integrations: 2 passed, 76 deselected.
- Complete available Python suite with both private roots: 78 passed, zero failures or skips.
- KITTI sequence `0000`: 1,089 physical/valid rows, 378 `DontCare`, 0 confidence rows, 0 errors,
  0 final warnings and 1,089 schema/provenance-valid events.
- Fixture: 12 rows; source SHA-256
  `97f772a27181dfc7ef51b3e64b86bd42e682753b6855fdc58d259ecbed501fd4`; fixture SHA-256
  `fe67e4e689ff4431464bf4ee040e79454bb2e9f0e9dd0331a594b9e6a3aab1b7`.
- Repeated fixture conversion produced identical event order, IDs, canonical JSON and hashes.

**Remaining work**

- Audit the final staged scope for private paths, media and undocumented dataset-derived files.
- Commit and push only Milestone 3 changes; preserve unrelated interface work.
- Open a draft pull request and wait for CI before treating the milestone as merge-ready.
- Do not merge until CI, acceptance, provenance and privacy gates all pass.

---

## 2026-08-05 â€” Issue #4 normalised event collection validation

**Work completed**

- Started from the latest `origin/main`, which includes the merged MOT17 and KITTI adapters.
- Refactored validation internals so single-event and collection checks share schema, semantic,
  provenance and canonical-hash logic.
- Added coded error/warning diagnostics with zero-based event indexes and available event/source
  context.
- Added duplicate-ID detection, finite-number protection and collection summary counts.
- Added canonical JSON report writing and exact-byte SHA-256 calculation without runtime state.
- Reused the complete 12-event MOT17 and KITTI fixtures and added declarative synthetic invalid
  collection cases.
- Documented the validation API, codes, deterministic ordering, warning policy and schema decision.

**Decisions made**

- The first event-ID occurrence remains the reference; each later occurrence is invalidated.
- Warning-only events and collections remain valid; out-of-image positive geometry stays preserved.
- Diagnostics follow supplied event order, fixed within-event policy and stable machine codes.
- Common schema `0.2.0` remains unchanged because uniqueness and cross-field arithmetic are
  collection-semantic constraints rather than schema defects.
- Report format and validator versions begin independently at `0.1.0`.

**Problems or risks**

- The requested branch transition initially stopped because unrelated local README and web
  interface changes would have been overwritten. The two tracked edits were temporarily shelved,
  restored after branching and verified; untracked web files were untouched.
- The standalone `ruff` executable was not on this PowerShell PATH. The installed module entry point
  was used instead and returned the same Ruff check.
- The complete pytest invocation skipped both private-data integration tests, so this Issue #4 run
  records fixture-collection evidence rather than new full-dataset integration evidence.

**Validation evidence**

- Targeted event and collection validation: 27 passed.
- Ruff: `python -m ruff check .` passed.
- Non-integration suite: 98 passed, 2 deselected.
- Complete available suite: 98 passed, 2 private integrations skipped.
- Repeated validation produced identical report objects, canonical JSON bytes and SHA-256 hashes.
- Tests confirm that validation does not modify, remove or reorder supplied event collections.

**Next actions**

- Audit the staged scope for local paths, ignored configuration, datasets and media.
- Open a draft pull request that closes Issue #4 and wait for CI before merge.
- Keep Issue #6 event-package output and all sonification/audio work out of this change.
