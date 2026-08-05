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
- [ ] Pull-request CI passes and Issue #5 acceptance evidence is reviewed.

### Remaining Stage 1 work

- [x] KITTI Tracking fixture documented and committed under the official dataset licence.
- [x] KITTI Tracking parser implemented and tested.
- [x] Common schema reviewed against both real dataset adapters.
- [x] Normalised event validation extended for KITTI-specific requirements.
- [ ] Event and provenance outputs written in structured formats.
- [x] Dataset-specific assumptions documented.
- [ ] All Stage 1 automated tests pass in CI.
- [ ] Progress log and risk register reviewed at Stage 1 completion.

Stage 1 is complete only when the completion criteria in `project-plan.md` are satisfied. Completion
of the MOT17 milestone does not complete Stage 1.
