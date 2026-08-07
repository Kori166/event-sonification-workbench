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

---

## 2026-08-05 — Issue #6 deterministic event and provenance outputs

**Work completed**

- Started from the latest `origin/main`, including the merged Issue #4 collection validator.
- Reused the common canonical JSON, hashing, parser and validation components to add one output
  writer rather than a parallel pipeline.
- Added canonical `events.json`, fixed-column LF-delimited `events.csv`, `run_metadata.json` and
  `provenance_log.json` under a content-derived run ID.
- Added deterministic cross-adapter ordering, logical-only source/configuration references,
  output hashes, validation summaries, conversion assumptions and decision-record references.
- Added MOT17 and KITTI package CLI commands that parse, validate and write only valid collections.
- Covered both complete committed fixtures, nested CSV values, field preservation, ordering,
  repeated-run byte identity, metadata, provenance, hashes and unsafe input/output rejection.
- Documented output format version `0.1.0`; common event schema `0.2.0` remains unchanged.

**Decisions made**

- The run ID is derived from deterministic input identities and event-output hashes; wall-clock
  time, machine paths and randomness are excluded.
- Events use the required `(dataset, sequence, frame, track_id, source_row, event_id)` ordering;
  string track IDs retain common-schema lexical semantics for both adapters.
- Nested CSV values use the shared canonical JSON representation.
- `run_metadata.json` cannot embed its own hash without recursion, so its exact-byte hash is
  returned by the writer while metadata records the scope explicitly.
- Existing deterministic run directories may contain only the four expected regular files.

**Problems and actions**

- The repository virtual environment initially had Ruff and pytest but lacked the declared
  `jsonschema` runtime dependency, so the first non-integration run stopped during collection with
  nine `ModuleNotFoundError` reports. Installing the repository's declared `.[dev]` dependencies
  into that ignored environment repaired it; no dependency files required changes.
- Both complete-suite integration tests skipped clearly because private dataset roots were not
  available to that test process. No private-data results or full-dataset output claims were made.
- Unrelated local web-interface and launcher changes remain outside this Issue #6 scope.

**Validation evidence**

- Output-package coverage: 23 tests passed as part of each final suite run.
- Ruff: `ruff check .` passed.
- Non-integration suite after environment repair: 121 passed, 2 deselected.
- Complete available suite: 121 passed, 2 private-data integrations skipped.
- Reversing supplied fixture events and writing to separate roots produced identical run IDs,
  bytes and SHA-256 values for all four package files.

**Outcome recorded at close-out**

- Issue #6 was isolated from interface work, passed CI and merged through pull request #17.
- The following close-out entry supersedes the earlier pending Stage 1 status.

---

## 2026-08-05 - Stage 1 close-out

**Work completed**

- Confirmed Issues #4, #5 and #6 are closed and pull requests #16, #15 and #17 are merged.
- Confirmed common event schema `0.2.0` remains current.
- Generated ignored real-data packages for `MOT17-02-DPM` and KITTI Tracking `0000`.
- Verified exact four-file membership, validation, physical/output hashes, sorted events and absence
  of the private root strings in package content.
- Repeated both package commands in a separate ignored location and compared all four files byte by
  byte before moving the comparison artefacts out of the workspace.
- Reviewed Stage 1 criteria, project status and risks; prepared a planning-only Stage 2 checklist.

**Real package evidence**

- MOT17: run `run-mot17-mot17-02-dpm-03074d7ff016652e`; 30,003 valid events; 0 errors;
  988 permitted `bbox_outside_image` warnings; schema `0.2.0`; parser `0.1.0`.
- MOT17 hashes: source `2e3ecb488da8886d3200d402b2b08890c6d2879923839444e9b74fa43a551440`;
  JSON `880232f6ea0696a8c74600f51fe46e8221ff8ee40536dbef4570921a8779b96e`; CSV
  `2b4b5e3dac8e70661719b555fc6578a088e8b3aa18758f99447d3137dd43f3ee`; metadata
  `e247260608d4aaac72f2b5d3e3a602ebe29d7b8e8d2dedd10a2320b6456c7bee`; provenance
  `6b44534de1c9ffb9f1f4b7f2d033fa954e08c4dab219e68d8333ef649f55ae5f`.
- KITTI: run `run-kitti_tracking-0000-94a4cdc57ff00109`; 1,089 valid events; 0 errors;
  0 warnings; schema `0.2.0`; parser `0.1.0`.
- KITTI hashes: source `97f772a27181dfc7ef51b3e64b86bd42e682753b6855fdc58d259ecbed501fd4`;
  JSON `542389e4a783380191fdc228b83c37309fa4d483d58913978881ee3cfb6f57a2`; CSV
  `5068c491c8feace0ba39b91f9398e7b96b6310174c5d63b28a1792c4d8fb0db5`; metadata
  `89cefd74709226303257f6c315368b75b8bb52e84c4c473c03f0f5bf9a37a47b`; provenance
  `916703854628b24b0503a56f5bb754204691fe6aa517169fadb3dd5bc2968325`.

**Reproducibility and validation evidence**

- Both repeats produced the same run ID, deterministic event ordering, identical metadata and
  byte-identical JSON, CSV, metadata and provenance files with the same hashes.
- `python -m ruff check .`: passed.
- `python -m pytest -m "not integration"`: 121 passed, 2 deselected.
- `python -m pytest -m integration`: 2 passed, 121 deselected; neither integration skipped.
- `python -m pytest`: 123 passed.

**Problems and limitations**

- The desktop process did not inherit the roots, so only the two allowed variables were loaded into
  command processes from the ignored local environment file without printing their values.
- Local `main` had separate unpublished history; the branch was based directly on fetched
  `origin/main` without changing that history.
- MOT17 retains 988 permitted out-of-image source boxes. Selected-sequence evidence does not claim
  every sequence was converted, and generated full-data packages remain local and ignored.
- Sonification, audio rendering and evaluation remain unimplemented.

**Next actions**

- Publish the documentation-only close-out pull request and require its CI to pass before merge.
- Begin Stage 2 from versioned preset and deterministic cue-mapping design; do not treat the new
  checklist as completed implementation.

---

## 2026-08-05 - Stage 2 Milestone 1 cue scheduling

**Work completed**

- Created and assigned Issue #19 for versioned presets and deterministic cue schedules.
- Started from fetched `origin/main` on `stage-2/milestone-1-cue-scheduling` while preserving
  unrelated local interface changes outside milestone scope.
- Added preset schema `0.1.0` and baseline preset `0.1.0` with explicit bounds, mapping methods,
  class modifiers, suppression policy, priority and event order.
- Added structured preset diagnostics and exact-file/configuration hashes.
- Reused Stage 1 validation, ordering, canonical JSON, CSV and SHA-256 code for package consumption
  and deterministic cue output.
- Added cue/suppression accounting, stable cue IDs, content-derived run IDs, canonical JSON logs,
  fixed LF CSV and path-free metadata.
- Added `schedule-cues` with strict event-package, validation, schema, preset and output-path gates.
- Added a five-event synthetic fixture with hand-calculated expected cues/suppressions and tests
  against the complete committed MOT17 and KITTI collections.
- Documented formulas, constants, confidence semantics, suppression treatment, file contracts,
  limitations and Decision 0011. Common event schema `0.2.0` remains unchanged.

**Decisions made**

- Normalised mapping inputs clamp to `[0, 1]`; cue parameters round using preset precision.
- Class modifiers remain explicit renderer inputs and do not silently alter another cue parameter.
- Each event yields exactly one cue or one suppression record in preset-defined priority.
- A verified Stage 1 package is revalidated without reopening private dataset files; default event
  validation still verifies physical source existence and hash.
- Preset settings are technical configuration and carry no perceptual or accessibility claim.

**Problems and actions**

- GitHub CLI remained unavailable; the connected GitHub capability created Issue #19.
- Unrelated README, web and launcher work was retained without staging it into this milestone.
- The package gate was tightened to compare `events.csv` bytes with the shared Stage 1 serialiser,
  in addition to recorded hashes and schema/semantic validation.

**Validation evidence**

- `python -m ruff check .`: passed.
- `python -m pytest -m "not integration"`: 144 passed, 2 deselected.
- `python -m pytest`: 144 passed, 2 private-data integrations skipped clearly.
- Focused preset/scheduler tests: 23 passed within the final suite.
- Separate output roots produced identical cue run IDs, order, bytes and file hashes.

**Next actions**

- Audit and stage only Issue #19 implementation and documentation files.
- Open pull request `Stage 2: add deterministic cue scheduling` and require CI before merge.
- Keep audio rendering and technical evaluation outside this milestone.

---

## 2026-08-05 - Stage 2 Milestone 2 deterministic WAV rendering

**Work completed**

- Confirmed Milestone 1 merged through PR #20 and created assigned Issue #21.
- Added renderer schema/configuration `0.1.0` with coded validation diagnostics.
- Added strict cue-package integrity, identity, count, ordering, parameter and preset verification.
- Implemented Decimal half-up sample placement, fixed-phase sine synthesis, linear envelopes/pan,
  ordered overlap summation, conditional peak gain and explicit PCM16 conversion.
- Added minimal deterministic WAV, canonical render log and renderer metadata beneath a
  content-derived audio run ID, including a zero-frame empty-schedule policy.
- Added a manual three-cue fixture/oracle, committed-fixture end-to-end chain and complete committed
  MOT17/KITTI compatibility tests without committing generated audio.
- Documented the renderer/WAV contract, Decision 0012, project status and evidence boundary.

**Decisions made**

- Cue end samples are exclusive and all second-to-sample conversions use Decimal half-up.
- Baseline pan is linear balance; class modifier is retained only for traceability in policy 0.1.0.
- Global target-peak gain applies only when needed; PCM quantisation follows mixing and gain.
- Empty valid schedules produce a zero-frame WAV rather than failing.
- Cross-platform byte identity is not claimed beyond environments actually tested.

**Problems and risks**

- GitHub CLI remained unavailable, so the connected GitHub capability created Issue #21.
- Complete pytest skipped two private-data integrations; skips are not treated as evidence of pass.
- Floating-point/libm differences near quantisation boundaries remain a monitored portability risk.

**Validation evidence**

- `python -m ruff check .`: passed.
- `python -m pytest -m "not integration"`: 178 passed, 2 deselected.
- `python -m pytest`: 178 passed, 2 private-data integration tests skipped clearly.
- 34 audio-renderer tests passed within the final suites.
- Repeated separate fixture outputs had identical run IDs, WAV/JSON bytes and SHA-256 hashes.
- Actual manual fixture WAV SHA-256:
  `041aa0be80f18ddc770cf0fee1cd4c426509972cc4d386eee72b7b2397081beb`.

**Next actions**

- Audit and stage only Issue #21 changes, preserving unrelated interface work.
- Open draft pull request `Stage 2: add deterministic WAV rendering`, closing Issue #21.
- Require CI and acceptance evidence before merge; leave Stage 3 evaluation out of this branch.

---

## 2026-08-06 - Stage 2 close-out

**Work completed**

- Confirmed PR #22 merged at `488e4eb70c8faf7527b327926b3b2ebc4e1af957`, its CI workflow
  concluded successfully and Issue #21 closed.
- Ran two independent full native-annotation to event-package to cue-package to audio-package chains
  for real MOT17 `MOT17-02-DPM` and KITTI Tracking `0000` data.
- Added a reusable exact package-comparison command because the repository had no existing utility;
  it reports stable path-free byte/hash results and exits nonzero for mismatches.
- Independently verified package loaders, declared and calculated hashes, event order, unique IDs,
  cue/suppression accounting, cue and render logs, source file/row links and WAV headers/PCM peaks.
- Recorded exact run IDs, all 24 output-file hashes, configuration hashes, counts, audio properties,
  environment, problems and limitations in `docs/development/stage-2-closeout.md`.
- Marked Stage 2 complete and Stage 3 technical evaluation as the next active stage without adding
  metrics, thresholds or evaluation claims.

**Actual real-data evidence**

- MOT17: 30,003 valid events, 0 errors, 988 warnings, 26,960 cues, 3,043 coded suppressions
  and 26,960 rendered cues. WAV: 885,822 stereo frames at 44,100 Hz; peak limiting applied.
- KITTI Tracking: 1,089 valid events, 0 errors/warnings, 711 cues, 378 coded `DontCare`
  suppressions and 711 rendered cues. WAV: 680,022 stereo frames at 44,100 Hz; no limiting needed.
- For both datasets, independent runs reproduced the same event/cue/audio run IDs and exact bytes
  and hashes for all four event files, five cue files and three audio files.
- Both datasets had zero eligible events without cues, zero unlinked cues and zero source-location
  or render-link mismatches.
- Generated content contained no configured private root, username or OneDrive marker and remained
  beneath an ignored `.local-fixtures/` tree.

**Quality evidence**

- `python -m ruff check .`: passed.
- `python -m pytest -m "not integration"`: 184 passed, 2 deselected.
- `python -m pytest -m integration`: 2 passed, 184 deselected; neither private test skipped.
- Cue-scheduling/renderer/comparison focused tests: 55 passed.
- `python -m pytest`: 186 passed with no skips.

**Problems and limitations**

- The first evidence-audit command used two incorrect configuration-schema paths; it was corrected
  and rerun, after which every configuration hash matched. No package defect was found.
- Full MOT17 runs were slower than fixture tests but completed twice without reusing output trees.
- Byte identity is established for Windows `10.0.26200`, AMD64 and Python `3.14.3`, not for an
  untested platform/runtime.
- Baseline mapping/rendering remains a technical reference. Perceptual quality, accessibility,
  participant evidence and technical metric results remain untested.

**Next actions**

- Begin Stage 3 by defining formulas, units, denominators and controlled fixtures for coverage,
  alignment, density/overlap, traceability and reproducibility metrics.
- Preserve the distinction between intentional suppressions, eligible events without cues and
  unlinked cues in every evaluation report.
- Do not claim participant, perceptual, accessibility or safety outcomes from technical measures.

---

## 2026-08-06 - Stage 3 Milestone 1 close-out

**Work completed**

- Confirmed the Stage 2 close-out merged through PR #23 and began from clean merged `main` state.
- Added schema-validated technical-evaluation contract/report format `0.1.0` and Decision 0013.
- Implemented deterministic event accounting/coverage, three timing domains, resolved-link
  traceability, density, half-open overlap and four-level reproducibility reports.
- Added a canonical CLI report writer with content-derived evaluation identity and explicit input/
  output hash scopes.
- Authored a five-event, five-cue, one-suppression 10 Hz oracle and calculated every expected rate,
  sample, interval, percentile, density and overlap value before freezing the golden report.
- Added named miss, orphan, conflicting-outcome, unknown-suppression, broken-provenance,
  one-sample-displacement, empty, zero-duration and malformed tests.
- Updated the README, project plan, Stage 3 checklist, risk register and milestone close-out without
  adding real-data or perceptual findings.

**Decisions made**

- Intentional suppressions are outside eligible-coverage misses; a valid event with no explicit
  outcome is eligible and missed.
- Multiple cues may represent one event, but cue plus suppression is a conflicting outcome.
- Rates always include numerator/denominator and use null for zero denominators.
- Timing uses source, schedule and rendered sample references separately with renderer half-up
  rounding; p95 is nearest rank.
- Rendered zero-based duration and integer half-open intervals are preferred for density/overlap.
- Semantic, byte, audio and configuration repeat evidence remain separate and environment-bounded.

**Actual synthetic evidence**

- Oracle coverage: eligible `4/4`, source representation `4/5`, suppression `1/5`, accounting
  `5/5`, missed `0/4`.
- Peak concurrency 2; overlap and excess concurrency 1.2 seconds; both normalised values 0.4.
- Evaluation run ID: `evaluation-synthetic-evaluation_oracle-e1ee06d3a671ee1b`.
- Canonical report SHA-256:
  `b5bcf1fc39987dfd7b61475e67d075312bd060f6dfb8adf2fa3f8300badaf908`.

**Quality evidence**

- `python -m ruff check .`: passed.
- Focused evaluation suite: 25 passed.
- `python -m pytest -m "not integration"`: 209 passed, 2 deselected.
- `python -m pytest -m integration`: 2 skipped because private root variables were unavailable;
  skips are not pass evidence.
- `python -m pytest`: 209 passed, 2 skipped for those unavailable roots.
- Current-Ruff format check passed for all three changed Python files. No static type checker is
  configured or installed; whole-repository format checking exposes older out-of-scope drift.

**Problems and limitations**

- The original checkout contained unrelated interface files. They were preserved separately and
  a clean worktree prevented them entering this branch.
- The milestone CLI consumes prepared validated record-chain input; verified real-package input
  preparation belongs to Milestone 2.
- No MOT17/KITTI technical evaluation was run. RQ3 remains incomplete.
- No cross-environment, perceptual, participant, accessibility, usability, navigation or safety
  result is claimed.

**Next actions**

- Run Stage 3 Milestone 2 against selected verified real MOT17 and KITTI Tracking evidence packages
  using unchanged contract `0.1.0`.
- Produce repeated deterministic dataset-level reports and investigate every diagnostic before
  interpretation.

---

## 2026-08-06 - Stage 3 Milestone 2 real-data technical evaluation

**Work completed**

- Started from clean `main` commit `c1b3d676`, preserving the unrelated dirty checkout and both
  stashes in place.
- Wrote the evaluation protocol before metric calculation and added a schema-validated experiment
  manifest plus path-free environment manifest.
- Verified both retained Stage 2 event/cue/audio chains for MOT17-02-DPM and KITTI 0000 against
  exact file membership, canonical serialisation, all documented hashes, identities, ordering,
  accounting and cross-stage links; no chain was regenerated.
- Added a strict package-to-evaluator assembler, content-derived input/hash manifest, focused CI
  fixtures and a private cross-stage integration test.
- Ran frozen contract `0.1.0` three times per dataset in isolated directories and generated
  canonical reports, JSON/CSV/Markdown summaries, three-run comparisons and deterministic
  record-level audits.
- Committed a bounded cross-dataset technical summary, Decision 0014, excluded-evidence inventory
  and Milestone 2 close-out without committing private/full-data inputs or WAVs.

**Actual real-data evidence**

- MOT17: 30,003 valid events; 26,960 represented; 3,043 intentionally suppressed; 0 missed or
  excluded; report ID `evaluation-mot17-mot17-02-dpm-2636a438409d649e`; report SHA-256
  `d847e805d0b2d7ccd50cd315bbcecfc0ad525f40e7c4c2013938f955d20f13e5`.
- KITTI: 1,089 valid events; 711 represented; 378 intentionally suppressed `DontCare` events; 0
  missed or excluded; report ID `evaluation-kitti_tracking-0000-d997cdc8f6467c1d`; report SHA-256
  `b5589590a8c645bd7b5654d0318bf90fdb412f987719c26c2374bf3e487f9ff2`.
- Both eligible-event coverage and accounting completeness rates were 1.0; all contract
  traceability rates and supplemental resolved mapping/schedule/WAV checks were 1.0; no broken link
  or evaluation diagnostic was recorded.
- MOT17/KITTI cue density was 1342.1838698971126/46.10894941634241 cues per second; peak
  concurrency was 203/24; normalised overlap burden was 160.0620643876535/4.533073929961089.
- All six reports were semantically and byte-identical within their dataset. Comparison-report
  hashes are `a21990ef56e1e82516babf248c7ac782384ba39cb88b896a25fc30da2a8b38b7`
  and `42205454e27c1df71669e1d2b75c1928d2986232e46ed4e48fb08c4d9940dd79`.

**Quality evidence**

- `python -m ruff check .`: exit 0.
- `python -m pytest tests/test_technical_evaluation.py -q`: 26 passed.
- `python -m pytest -m "not integration"`: 231 passed, 3 deselected.
- `python -m pytest -m integration`: 3 passed, 231 deselected; no private test skipped.
- `python -m pytest`: 234 passed with no skip or deselection.

**Problems and decisions**

- A four-minute tool timeout yielded no integration result; the unchanged test and final matrices
  completed under longer bounds.
- One unsafe `..` output argument was correctly rejected and produced no accepted report. Resolved
  regular paths were then used.
- Native/common MOT17 sequence identity was clarified before accepted assembly. A superseded KITTI
  pre-correction input remains ignored and inventoried.
- KITTI's emitted summary filename link and lossless diagnostic-array retention were corrected;
  affected real summaries were rebuilt twice with identical bytes.
- No contract defect was found, and no definition, denominator, threshold or schema was tuned after
  observing results.

**Evidence boundary and next action**

- RQ3 is now supported by real technical case-study evidence for the selected sequences, baseline
  preset/renderer and recorded environment. No perceptual, participant, accessibility, usability,
  navigation, mobility, safety or cross-environment byte-identity result is claimed.
- Next: Stage 3 Milestone 3: convert the verified technical-evaluation evidence into audited
  report-ready tables, figures and bounded RQ3 findings, with every presented value linked to its
  canonical source report.

---

## 2026-08-06 - Stage 3 Milestone 3 audited reporting and close-out

**Work completed**

- Began from `origin/main` merge commit `5fcab3ad8465f960e1a217063deb8fa82314fa93` in a new clean
  worktree and branch, leaving the dirty original checkout and both preserved stashes untouched.
- Recalculated the two canonical report hashes, validated both documents against the frozen report
  schema and confirmed report/run/contract/experiment/environment identities plus summary and repeat-
  comparison agreement before generating presentation material.
- Defined the display-format and interpretation policy in Decision 0015 and the reporting README.
- Added a deterministic CLI generator that verifies source/configuration hashes, resolves structural
  JSON Pointers, preserves canonical raw values, generates CSV/Markdown/SVG derivatives and rejects
  private paths or an unauditable presentation.
- Generated three principal tables, a complete timing supplement, three source-data CSV files,
  three SVG figures, table/figure captions, a presentation-value manifest, bounded RQ3 method and
  findings, a claim-to-evidence matrix, a replacement note and automated/hash audits.
- Added 21 focused tests for source hashes/schema, pointer failures, direct/derived values,
  formatting/nulls, table/figure/claim completeness, SVG determinism, source preservation, private-
  path detection, repeat bytes and the CLI.
- Rendered and visually inspected all SVGs, independently recalculated every principal presentation
  row/data point and reconciled the Stage 3 checklist, plan, README, risk register and close-out.

**Evidence and audit results**

- Canonical MOT17 report SHA-256:
  `d847e805d0b2d7ccd50cd315bbcecfc0ad525f40e7c4c2013938f955d20f13e5`.
- Canonical KITTI report SHA-256:
  `b5589590a8c645bd7b5654d0318bf90fdb412f987719c26c2374bf3e487f9ff2`.
- Reporting manifest SHA-256:
  `5de4e72aa9dc014aa714a206879a3f5674abf1b1400c0f0fc5198761e0a73c66`.
- Terminal generated-file hash-manifest SHA-256:
  `ee7c773fc14274f69f69a74878795c297e0a3d928fdc1c705221f3cd72b3942d`.
- Automated audit: pass; 134 values, 104 direct, 30 derived, 136 table cells, 20 figure
  data points, 12 claims, zero mismatch/missing/formatting/private-path findings.
- Independent audit: pass; all 68 table rows, 20 figure data points, 12 claims, seven captions and
  23 terminal file hashes checked with zero remaining mismatch.
- Two separate empty-directory CLI builds: exit 0, identical 24-file sets and byte-identical content.

**Quality evidence**

- `python -m ruff check .`: exit 0.
- `python -m pytest tests/test_technical_evaluation.py -q`: 26 passed.
- `python -m pytest -m "not integration"`: 252 passed, 3 deselected.
- Final `python -m pytest -m integration` with all private roots: 3 passed, 252 deselected; no skip.
- Final `python -m pytest` with all private roots: 255 passed; no skip or deselection.

**Problems and decisions**

- Initial Figure 1 visual inspection found an overlapping count/axis label and a redundant MOT17
  label. The SVG layout was fixed before evidence was accepted.
- Independent arithmetic found one binary-float last-digit difference for KITTI normalised overlap
  burden. Canonical raw scalars are now preserved while declared formula results are checked with a
  bounded representation tolerance.
- Early manual-audit scripts contained one Markdown-row indexing error and one whitespace-sensitive
  phrase check; corrected audit-side checks passed and did not alter evidence.
- An integration invocation without configured roots skipped three tests, and a two-root invocation
  passed two while skipping the retained-chain test. Neither was reported as pass evidence; final
  configured runs used all three roots and had no skips.
- Contract `0.1.0`, canonical reports, dataset logic, preset and renderer were not changed or rerun.

**Boundary and next action**

- Stage 3 technical evaluation is complete within the selected case-study and recorded-environment
  scope. RQ3 is supported by audited technical evidence, not participant or perceptual evidence.
- No accessibility, usability, navigation, mobility, safety or cross-environment byte-identity result
  is claimed. The overall project is not yet submission-ready.
- Next: Stage 4 Milestone 1 - assemble a versioned artefact release candidate and verify
  installation, configuration, evidence availability and end-to-end execution from a clean
  environment.

---

## 2026-08-07 - Stage 4 Milestone 1 Phase 1 headless inspection contract

**Work completed**

- Began Stage 4 from merged Stage 3 `main` and kept browser/UI implementation out of Phase 1.
- Added Workbench Session Contract `0.1.0`, field-level documentation, Decision 0016, the Stage 4
  checklist and a headless `workbench.session` validator.
- Added deterministic session identity, cross-stage package/hash checks, optional Stage 3 report
  verification, runtime-only media binding and path-free machine-readable diagnostics.
- Added an explicit `workbench` package interface and six focused tests covering valid loading,
  cross-package mismatch, declared hash tampering, unavailable evaluation and runtime-path privacy.
- Opened PR #28 and used pull-request CI as the clean-checkout quality gate.
- Reconciled the project plan, project-management index, risk register and Stage 4 development record
  with the new inspection-layer scope and evidence boundary.

**Decisions made**

- The browser will consume already validated sessions and remain read-only with respect to Stage 1-3
  evidence.
- Runtime roots and media paths are excluded from `session_id`; content and configuration identities
  determine the deterministic session identity.
- The Stage 4 interface is artefact inspection/demonstration infrastructure, not participant or
  perceptual evidence and not an extension of the research questions.
- The existing verified-chain logic is reused rather than duplicated; its current private API use is
  recorded for review before the final release candidate.

**Problems and actions**

- PR #28 CI run 71 failed only at Ruff with three `TRY004` findings in `workbench/session.py`.
- The affected invalid-type branches were corrected to raise `TypeError`, with matching exception
  handling. No Stage 1-3 contract or research logic changed.
- CI run 72 then passed. The first failed run did not execute pytest and is not used as test-pass
  evidence.

**Validation evidence**

- PR #28 CI run 72 environment: Ubuntu 24.04, Python 3.11.15.
- `ruff check .`: passed with no findings.
- `python -m pytest -m "not integration"`: 258 passed, 3 deselected.
- `tests/test_workbench_session.py`: 6 passed within the successful non-integration suite.
- Editable installation of `.[dev]` succeeded, including the new `workbench` package.

**Remaining work**

- CI cannot access the ignored retained Stage 1/2 package chains or private dataset media, so it
  cannot satisfy the final Phase 1 real-chain acceptance action.
- Validate one retained MOT17-02-DPM or KITTI Tracking 0000 package chain with its actual local media
  from a clean checkout, repeat the validation and confirm the same `session_id`.
- Confirm that diagnostics and exported session data remain free of absolute local paths, usernames
  and machine-specific state.

**Next actions**

- Keep browser/UI implementation blocked until the retained real-chain Phase 1 acceptance action is
  recorded as passed.
- After that gate, merge PR #28 and begin Phase 2 with one synchronised inspection vertical slice.
