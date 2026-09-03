# Stage 1 Checklist

## Data Ingestion and Normalisation

### Milestone 1: Schema and Synthetic Fixture

- [x] Defined provisional common event schema `0.1.0` under `configs/schemas/`.
- [x] Documented the schema fields and conventions.
- [x] Recorded significant schema decisions in Decision 0006.
- [x] Added one synthetic source annotation with a manually calculated expected event.
- [x] Added validation tests covering structure, arithmetic, deterministic IDs and provenance.
- [x] Reviewed the schema against real MOT17 and KITTI Tracking rows and recorded the move to version `0.2.0`.

### Milestone 2: MOT17 Vertical Slice

- [x] Parsed the nine column MOT17 ground truth format using explicit type conversion.
- [x] Parsed and validated `seqinfo.ini` metadata.
- [x] Converted one based source frames to zero based common frames.
- [x] Preserved native bounding box coordinates and documented the decision.
- [x] Preserved the MOT17 evaluation mark without treating it as a confidence score.
- [x] Added a versioned MOT17 class mapping.
- [x] Added structured diagnostics for invalid rows.
- [x] Added a twelve row synthetic MOT17 fixture, expected output and parser tests.
- [x] Added the local `mot17-check` command.
- [x] Added manifest based private fixture generation and hash verification.
- [x] Documented MOT17 conversion rules and known difficulties.
- [x] Confirmed the implementation passed the automated CI suite.
- [x] Documented the selected MOT17 data with source lines and hashes.
- [x] Generated and verified the private fixture in a Git ignored location.
- [x] Independently calculated the expected common events for the synthetic fixture.
- [x] Confirmed the selected real MOT17 sequence passed `mot17-check`.
- [x] Confirmed the real data integration test passed with provenance validation.
- [x] Reviewed the official MOTChallenge licence terms and recorded attribution.
- [x] Committed the twelve row dataset fixture with its licence notice.
- [x] Closed Issues #2 and #3 with evidence against their acceptance criteria.

### Milestone 3: KITTI Tracking Extension

- [x] Inspected the local KITTI data before implementation and recorded its layout and 21 annotation files.
- [x] Reviewed the official definitions for frames, tracks, classes, truncation, occlusion, angle, 2D and 3D geometry, score and `DontCare`.
- [x] Added a deterministic twelve row KITTI fixture with attribution and a CC BY-NC-SA 3.0 notice.
- [x] Recorded and tested source line numbers, selection method, source hash and fixture hash.
- [x] Kept malformed synthetic rows separate from dataset derived rows.
- [x] Parsed all seventeen required fields and the optional score using explicit type conversion.
- [x] Preserved frames, tracks, classes, 2D geometry, truncation, occlusion, score and provenance.
- [x] Kept `DontCare` as a valid recorded event rather than silently removing it.
- [x] Added coded diagnostics for invalid fields, values, boxes, frames, tracks, classes, truncation and occlusion.
- [x] Reviewed the schema against both adapters. Version `0.2.0` only required a change to the native confidence range.
- [x] Added tests for parsing, mapping, timing, geometry, quality, determinism and fixture integrity.
- [x] Confirmed the full private KITTI sequence `0000` passed with 1,089 valid rows, 0 errors and 0 warnings.
- [x] Merged the milestone through pull request #15.

### Milestone 4: Normalised Event Collection Validation

- [x] Reused the existing schema and individual event validation.
- [x] Checked every event against common schema version `0.2.0`.
- [x] Added checks for duplicate IDs, invalid timestamps, boxes, areas and normalised geometry.
- [x] Added stable diagnostic codes with severity, event index and provenance context where available.
- [x] Kept errors and warnings separate so collections containing only warnings remain valid.
- [x] Made report counts, ordering, canonical JSON and SHA-256 values deterministic.
- [x] Confirmed validation does not modify, remove or reorder events.
- [x] Added tests for complete valid MOT17 and KITTI fixture collections.
- [x] Added fixtures covering missing fields, incorrect types, duplicates, timestamps, boxes and multiple errors.
- [x] Kept schema `0.2.0` unchanged because collection validation found no schema defect.
- [x] Confirmed CI passed and merged Issue #4 through pull request #16.

### Milestone 5: Deterministic Event and Provenance Outputs

- [x] Reused the existing adapters, schema, collection validation and canonical hashing.
- [x] Produced packages containing `events.json`, `events.csv`, `run_metadata.json` and `provenance_log.json`.
- [x] Derived run IDs from deterministic content with no time based or random values.
- [x] Applied a stable event order using dataset, sequence, frame, track ID, source row and event ID.
- [x] Preserved every common event field in canonical UTF-8 JSON.
- [x] Used schema field order, LF endings and stable nested JSON values in CSV output.
- [x] Recorded dataset, sequence, source, parser, mapping, schema and output hashes in run metadata.
- [x] Recorded logical inputs, configuration hashes, assumptions and decisions in provenance records.
- [x] Rejected absolute local paths and unsafe output directories.
- [x] Confirmed repeated MOT17 and KITTI fixture runs produced identical bytes, run IDs and hashes.
- [x] Added `mot17-package` and `kitti-package` CLI commands to parse, validate and write packages.
- [x] Kept common schema `0.2.0` unchanged because no event record defect was found.
- [x] Confirmed CI passed and merged Issue #6 through pull request #17.

### Milestone 6: Stage 1 Completion

- [x] Documented and committed the KITTI Tracking fixture under the official dataset licence.
- [x] Implemented and tested the KITTI Tracking parser.
- [x] Reviewed the common schema against both real dataset adapters.
- [x] Implemented validation for individual events and complete collections.
- [x] Produced deterministic event and provenance outputs.
- [x] Documented dataset specific assumptions.
- [x] Confirmed the real `MOT17-02-DPM` package contains 30,003 valid schema `0.2.0` events.
- [x] Confirmed the real KITTI Tracking `0000` package contains 1,089 valid schema `0.2.0` events.
- [x] Confirmed both packages contain JSON, CSV, run metadata and provenance with source and configuration hashes.
- [x] Confirmed repeated runs produced identical run IDs, event order, bytes and SHA-256 values.
- [x] Confirmed Ruff, 121 non integration tests, both private integrations and all 123 tests passed locally.
- [x] Confirmed Stage 1 implementation CI passed through pull request #17 and final Stage 1 CI passed through pull request #18.
- [x] Retained assumptions and limitations in the common event documentation, progress log and risk register.
- [x] Reviewed the progress log and risk register at Stage 1 completion.

