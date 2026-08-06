# Stage 1 Checklist

## Data Ingestion and Normalisation

### Milestone 1: schema and synthetic fixture

- [x] Provisional common event schema `0.1.0` defined under `configs/schemas/`.
- [x] Schema conventions and fields documented.
- [x] Significant schema decisions recorded in Decision 0006.
- [x] One synthetic source annotation and manually constructed expected event committed.
- [x] Structural, arithmetic, deterministic-ID and provenance validation tests pass locally.
- [x] Schema reviewed against real MOT17 and KITTI Tracking rows; version `0.2.0` decision recorded.

### Milestone 2: MOT17 vertical slice

- [x] Nine-column MOT17 ground-truth rows parsed through explicit type conversion.
- [x] `seqinfo.ini` metadata parsed and validated.
- [x] One-based source frames converted to zero-based common frames.
- [x] Native bounding-box coordinates preserved and the decision documented.
- [x] MOT17 evaluation mark preserved without mislabelling it as confidence.
- [x] Versioned MOT17 class mapping added.
- [x] Invalid rows produce structured diagnostics.
- [x] Twelve-row synthetic MOT17-format fixture, golden projection and parser tests added.
- [x] Local `mot17-check` command added.
- [x] Manifest-driven private dataset-fixture generation and hash verification added.
- [x] MOT17 conversion rules and difficulties recorded.
- [x] Latest implementation head passes the automated CI suite.
- [x] Dataset-derived MOT17 selection documented with source lines and hashes.
- [x] Private fixture generated and verified under a Git-ignored path.
- [x] Expected common events independently calculated for the synthetic equivalent.
- [x] Selected real MOT17 sequence passes `mot17-check`.
- [x] Real-data integration test passes locally with provenance validation.
- [x] Official MOTChallenge licence terms reviewed and attribution recorded.
- [x] Twelve-row dataset-derived fixture committed with its licence notice.
- [x] Issues #2 and #3 closed with acceptance-criterion evidence.

### Milestone 3: KITTI Tracking extension

- [x] Local KITTI root inspected before implementation; actual layout and 21 annotation files recorded.
- [x] Official frame, track, class, truncation, occlusion, angle, 2D/3D geometry, score and `DontCare` definitions reviewed.
- [x] Twelve-row deterministic KITTI fixture committed with attribution and CC BY-NC-SA 3.0 notice.
- [x] Source line numbers, selection method, source hash and fixture hash recorded and tested.
- [x] Synthetic malformed rows committed separately from dataset-derived rows.
- [x] Seventeen required fields and optional score parsed through explicit type conversion.
- [x] Frames, tracks, classes, 2D geometry, truncation, occlusion, score and provenance preserved.
- [x] `DontCare` retained as a documented and tested event rather than silently discarded.
- [x] Invalid field counts, numbers, boxes, frames, tracks, classes, truncation and occlusion produce coded diagnostics.
- [x] Schema reviewed against both adapters; version `0.2.0` relaxes only native confidence range.
- [x] Unit, malformed-row, mapping, time, geometry, quality, determinism and fixture-integrity tests pass locally.
- [x] Full private sequence `0000` integration passes with 1,089 valid rows, 0 errors and 0 warnings.
- [x] Milestone merged through pull request #15.

### Milestone 4: normalised event collection validation

- [x] Existing schema and single-event validation inspected and reused.
- [x] Every supplied event is checked against common schema version `0.2.0`.
- [x] Duplicate IDs, invalid timestamps, boxes, areas and normalised geometry are diagnosed.
- [x] Diagnostics contain stable codes, severity, event index and available provenance context.
- [x] Error and warning severity remains distinct; warning-only collections remain valid.
- [x] Deterministic report counts, ordering, canonical JSON and SHA-256 are implemented.
- [x] Validation does not modify, remove or reorder supplied events.
- [x] Valid complete MOT17 and KITTI fixture collections are covered by tests.
- [x] Missing-field, wrong-type, duplicate, timestamp, box and multi-error fixtures are covered.
- [x] Schema `0.2.0` remains unchanged because collection validation found no schema defect.
- [x] Pull-request CI passed and Issue #4 merged through pull request #16.

### Milestone 5: deterministic event and provenance outputs

- [x] Existing adapters, schema, collection validation and canonical hashing are reused.
- [x] Packages contain `events.json`, `events.csv`, `run_metadata.json` and `provenance_log.json`.
- [x] Run IDs contain no time or randomness and are derived from deterministic content.
- [x] Events sort by dataset, sequence, frame, lexical track ID, source row and event ID.
- [x] JSON preserves every common event field through canonical UTF-8 serialisation.
- [x] CSV uses the schema field order, LF endings and canonical nested JSON cells.
- [x] Run metadata records dataset, sequence, source, parser, mapping, schema and output hashes.
- [x] Provenance records logical inputs, configuration hashes, assumptions and decisions.
- [x] Absolute local paths and unsafe output directories are rejected.
- [x] Repeated MOT17 and KITTI fixture runs produce identical bytes, run IDs and hashes.
- [x] `mot17-package` and `kitti-package` CLI commands parse, validate and write packages.
- [x] Common schema `0.2.0` remains unchanged because no event-record defect was found.
- [x] Pull-request CI passed and Issue #6 merged through pull request #17.

### Milestone 6: Stage 1 close-out

- [x] KITTI Tracking fixture documented and committed under the official dataset licence.
- [x] KITTI Tracking parser implemented and tested.
- [x] Common schema reviewed against both real dataset adapters.
- [x] Single-event and collection-level normalised event validation implemented for both adapters.
- [x] Event and provenance outputs merged in deterministic structured formats.
- [x] Dataset-specific assumptions documented.
- [x] Real `MOT17-02-DPM` package contains 30,003 valid schema `0.2.0` events.
- [x] Real KITTI Tracking `0000` package contains 1,089 valid schema `0.2.0` events.
- [x] Both packages contain JSON, CSV, run metadata and provenance with source/configuration hashes.
- [x] Separate repeated runs have identical run IDs, event order, bytes and SHA-256 values.
- [x] Ruff, 121 non-integration tests, both private integrations and all 123 tests pass locally.
- [x] Stage 1 implementation CI passed through pull request #17 and close-out CI passed through
  pull request #18.
- [x] Assumptions and limitations are documented in the Stage 1 close-out record.
- [x] Progress log and risk register reviewed at Stage 1 completion.

Stage 1 completion criteria are satisfied as of 5 August 2026. At that close-out, Stage 2 was the
next active stage and no sonification implementation was claimed by this checklist. Stage 2 was
subsequently completed on 6 August 2026; see `docs/development/stage-2-closeout.md`.
