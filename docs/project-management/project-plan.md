# Project Plan

## Project

**A Reproducible Workbench for Event-Based Sonification of Annotated Video Datasets**

## Aim

Design, implement and evaluate a reproducible workbench that converts annotated video data into
normalised events, deterministic audio cues and traceable technical outputs.

## Project Stages

| Stage | Main work | Evidence of completion | Status |
|---|---|---|---|
| 0. Project setup | Establish the repository structure, environment, documentation and project tracking | Working package scaffold, CI test, README and project records | Complete, 28 July 2026 |
| 1. Data ingestion and normalisation | Parse MOT17 and KITTI Tracking annotations into a common event schema | Parsers, schema, validation outputs, provenance records and tests | Complete, 5 August 2026 |
| 2. Sonification | Map normalised events into scheduled audio cues | Mapping presets, cue schedules, audio files and logs | Complete, 6 August 2026; real MOT17/KITTI chains reproduced exactly |
| 3. Technical evaluation | Measure coverage, alignment, traceability, cue density, overlap and reproducibility | Evaluation reports, comparison results, audited reporting derivatives and repeat-run checks | Complete, 6 August 2026 |
| 4. Artefact assembly and release | Validate, document and package the complete workbench | Reproducible release, final documentation and tagged version | Active; Milestone 1 Phase 1 validation gate in progress |
| 5. Reporting and viva preparation | Complete the dissertation and prepare the artefact demonstration | Final report, demonstration plan and viva notes | Planned |

## Working Method

The project will be developed iteratively. Work will be recorded through GitHub Issues and commits,
automated tests, configuration and provenance files, the progress log, the risk register,
supervision records and decision records.

## Stage 1 Milestones

| Milestone | Work | Status |
|---|---|---|
| 1. Schema and synthetic fixture | Define a provisional common schema and validate one manually constructed event | Complete, 29 July 2026 |
| 2. MOT17 vertical slice | Create a fixed MOT17 fixture and convert it through the first dataset parser | Complete, 4 August 2026 |
| 3. KITTI extension | Add a fixed KITTI Tracking fixture and parser without changing the downstream interface unnecessarily | Complete, merged through PR #15 on 5 August 2026 |
| 4. Stage 1 quality gate | Validate both adapters, write structured outputs and complete repeat-run checks | Complete, 5 August 2026; real packages and repeat runs verified |

## Milestone 2 Quality Gate

Milestone 2 is complete because:

- the MOT17 ground-truth format is parsed through explicit type conversion;
- a small dataset-derived fixture records its sequence, source rows, selection rationale, hashes,
  attribution and licence;
- the fixed synthetic equivalent produces independently calculated expected common events;
- invalid rows produce structured diagnostics;
- the selected real sequence passes the local parser and event-validation command;
- the complete automated suite passes in CI; and
- Issues #2 and #3 contain evidence for every acceptance criterion.

## Milestone 3 Quality Gate

Milestone 3 is ready for merge only when:

- the actual private KITTI layout and official annotation definitions are recorded;
- the attributed fixture records source rows, deterministic selection, source/fixture hashes and
  licence terms;
- all 17 required fields and optional score are converted explicitly;
- frames, tracks, classes, 2D geometry, truncation, occlusion, confidence and provenance are
  preserved;
- `DontCare` treatment is explicit and tested;
- malformed rows produce coded structured diagnostics;
- schema versioning is reviewed against both adapters;
- the complete selected private sequence passes integration validation;
- normal and complete available suites pass locally; and
- pull-request CI passes with no private paths, media or full dataset files committed.

The implementation, fixture and recorded private integration evidence were merged through pull
request #15. Issue #4 does not revise the adapter implementation.

## Issue #4 Collection Validation Quality Gate

Issue #4 is ready for merge only when:

- complete MOT17 and KITTI collections reuse the schema `0.2.0` single-event checks;
- missing fields, wrong types, duplicate IDs, invalid timestamps and invalid geometry are diagnosed;
- errors and warnings remain explicit and machine-readable;
- report counts and diagnostic order are deterministic;
- canonical report bytes and hashes repeat across identical runs;
- validation leaves supplied event content and order unchanged;
- valid and invalid fixtures and both adapters pass automated tests; and
- pull-request CI passes without committing private paths, datasets or media.

The implementation and acceptance criteria merged through pull request #16. Issue #6 consumes the
validation report without duplicating its policy.

## Issue #6 Structured Output Quality Gate

Issue #6 is ready for merge only when:

- validated MOT17 and KITTI events write to deterministic JSON and CSV;
- all common fields survive JSON output and nested values have a stable CSV encoding;
- event ordering follows dataset, sequence, frame, track ID, source row and event ID;
- metadata records source, parser, mapping, schema, validation and output hashes;
- provenance contains only logical input/configuration paths plus assumptions and decision records;
- repeated runs produce identical IDs, bytes and hashes without wall-clock content;
- unsafe paths, malformed inputs and invalid validation reports are rejected;
- adapter-to-package CLI commands remain inside Stage 1 scope;
- generated fixture/full-dataset run directories remain outside Git; and
- local tests and pull-request CI pass.

The implementation, acceptance evidence and CI merged through pull request #17. The Stage 1
close-out then generated and repeated real MOT17 and KITTI packages without a deterministic
difference.

## Stage 1 Work Order

1. Define the common event schema.
2. Create small fixed annotation fixtures.
3. Implement and test the MOT17 parser.
4. Implement and test the KITTI Tracking parser.
5. Validate normalised event records.
6. Write structured event and provenance outputs.

## Stage 1 Issues

- Issue #1: Define the common event schema. **Complete, 29 July 2026.**
- Issue #2: Implement the MOT17 annotation parser. **Complete, 4 August 2026.**
- Issue #3: Create a fixed MOT17 test fixture. **Complete, 4 August 2026.**
- Issue #4: Validate normalised event records. **Complete, merged through PR #16 on 5 August 2026.**
- Issue #5: Implement the KITTI Tracking annotation parser. **Complete, merged through PR #15 on 5 August 2026.**
- Issue #6: Write normalised event and provenance outputs. **Complete, merged through PR #17 on 5 August 2026.**

## Stage 1 Completion Criteria

Stage 1 is complete because:

- both selected real dataset formats convert into current common schema `0.2.0`;
- both real collections pass validation and write deterministic JSON/CSV packages;
- run metadata and provenance preserve source, parser, schema, mapping and output hashes;
- separate repeat runs have identical IDs, event ordering, bytes and hashes;
- invalid records remain covered by structured validation tests;
- Ruff, both private integrations and the complete 123-test suite pass locally;
- Stage 1 implementation pull requests passed CI; and
- assumptions, warnings, limitations and evidence are documented in
  `docs/development/stage-1-closeout.md`.

Completion was recorded on 5 August 2026. The generated full-data packages remain local and ignored
by Git.

## Stage 2 Complete

Stage 2 is complete and tracked in `docs/project-management/stage-2-checklist.md`. Milestone 1 under
Issue #19 implemented the versioned preset, deterministic event-to-cue mapping, cue schedules,
suppression policy and traceability logs. Milestone 2 under Issue #21 added the versioned
deterministic stereo PCM WAV renderer and merged through PR #22 after successful CI.

### Stage 2 Milestone 1 quality gate

Milestone 1 is ready for merge only when:

- preset schema `0.1.0` and baseline preset `0.1.0` validate with coded errors;
- mapping formulas and configurable constants are documented without perceptual claims;
- every valid schema `0.2.0` event produces one cue or one recorded suppression;
- cue/suppression provenance reaches source event, file, row and exact preset hash;
- schedules, logs, metadata, ordering, IDs, bytes and hashes repeat deterministically;
- both MOT17 and KITTI committed collections pass the common mapper;
- invalid packages, presets, validation status and unsafe paths are rejected;
- normal and complete available tests and pull-request CI pass; and
- no audio, evaluation claims, generated packages or private paths enter the change.

Milestone 1 passed CI and merged through pull request #20 on 5 August 2026.

### Stage 2 Milestone 2 quality gate

Milestone 2 required:

- renderer configuration and every time, envelope, pan, mixing, gain and PCM policy are versioned;
- cue-package files, hashes, run identity, counts, order, cue parameters and preset identity pass a
  strict pre-render gate;
- WAV/log/metadata outputs have deterministic content IDs, bytes and hashes;
- cue/source-event/sample traceability and an explicit empty-schedule result are preserved;
- manual expected samples and an end-to-end committed-fixture chain pass independently;
- complete committed MOT17 and KITTI cue schedules reach the renderer contract;
- normal and complete tests and pull-request CI pass; and
- no generated audio, private data/path or Stage 3/perceptual claim enters the change.

These criteria passed CI and merged through pull request #22 on 5 August 2026. The 6 August
close-out then ran the native-to-event-to-cue-to-WAV chain twice for real `MOT17-02-DPM` and KITTI
Tracking `0000`. All 4 event, 5 cue and 3 audio package files repeated byte-for-byte for both
datasets; all available tests passed. Exact counts, hashes, audio properties and limitations are in
`docs/development/stage-2-closeout.md`.

## Stage 3 Complete Work

Stage 3 begins from verified Stage 1 event packages and Stage 2 cue, suppression, WAV, render-log
and metadata packages. Milestone 1 completed contract `0.1.0`, a minimum evaluator and a manually
calculated synthetic oracle for:

- coverage and complete event accounting;
- temporal alignment;
- cue density and overlap;
- traceability completeness; and
- repeat-run reproducibility.

The frozen design distinguishes coded intentional suppressions from eligible events without cues
and from cues without a resolvable source event. It separates scheduling, render-placement and
end-to-end error, uses half-open overlap intervals, null zero-denominator values and semantic/byte/
audio/configuration repeat levels. The synthetic golden report repeats exactly. Milestone 2 applied
the unchanged contract to MOT17-02-DPM and KITTI Tracking 0000: every valid event received a
recognised outcome, every eligible event was represented, record links resolved, and three reports
per dataset were semantically and byte-identical in the recorded environment. Milestone 3 then
generated report-ready tables and SVG figures from the canonical reports, linked 134 presentation
values by structural path and completed automated and independent audits with zero remaining
mismatches. RQ3 is supported by these bounded real technical case studies; no perceptual,
participant, accessibility, usability, navigation, mobility or safety conclusion follows.

## Stage 3 Milestones

| Milestone | Work | Status |
|---|---|---|
| 1. Evaluation contract and oracle | Freeze metric semantics, implement the minimum evaluator and verify every measure against a manual synthetic oracle | Complete, 6 August 2026 |
| 2. Real-data technical evaluation | Apply unchanged contract `0.1.0` to selected verified MOT17 and KITTI Tracking evidence packages and write deterministic dataset reports | Complete, 6 August 2026 |
| 3. Audited report-ready evidence | Link verified values to canonical reports, audit tables/figures and state bounded RQ3 findings | Complete, 6 August 2026 |

## Stage 4 Active Work

Stage 4 begins from the merged Stage 3 evidence and assembles the deliverable workbench without
changing the established Stage 1-3 research contracts. Milestone 1 is divided into a headless
inspection contract, a synchronised inspection vertical slice and cross-dataset release preparation.
The local interface is a read-only inspection and demonstration layer over verified research outputs;
it is not a participant study or a new evaluation method.

Phase 1 has frozen Workbench Session Contract `0.1.0`, added deterministic session validation,
runtime media binding and path-free diagnostics, and passed PR #28 CI with Ruff clean and 258
non-integration tests passed. The remaining Phase 1 acceptance action is to validate one retained
real MOT17 or KITTI package chain with its actual local media from a clean checkout. Browser work is
not treated as unblocked until that evidence is recorded.

The current milestone remains **Stage 4 Milestone 1: assemble a versioned artefact release candidate
and verify installation, configuration, evidence availability and end-to-end execution from a clean
environment.** Detailed Phase 1-3 gates are recorded in `docs/project-management/stage-4-checklist.md`.

## Key Project Milestones

| Milestone | Target evidence |
|---|---|
| Repository established | Project structure and setup documentation |
| MOT17 pipeline working | Validated MOT17 events produced from a fixed sample |
| KITTI pipeline working | Validated KITTI Tracking events produced from a fixed sample |
| Sonification working | Deterministic cues, WAV output and traceability logs |
| Evaluation complete | Audited technical case-study metrics and bounded RQ3 evidence |
| Artefact frozen | Tagged, documented and reproducible release |
| Submission ready | Final report and tested viva demonstration |

## Scope Control

Core research deliverables remain limited to MOT17, KITTI Tracking, a common event schema,
deterministic sonification, provenance records and technical evaluation. Stage 4 adds a bounded local
inspection interface as artefact assembly and demonstration infrastructure over those existing
outputs; it does not extend the research questions or create new technical/perceptual findings.

Participant studies, validated accessibility/usability/navigation claims, assistive-technology or
safety claims, additional datasets and broader interface evaluation remain future work.
