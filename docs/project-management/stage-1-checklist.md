# Stage 1 Checklist

## Data Ingestion and Normalisation

### Milestone 1: schema and synthetic fixture

- [x] Provisional common event schema `0.1.0` defined under `configs/schemas/`.
- [x] Schema conventions and fields documented.
- [x] Significant schema decisions recorded in Decision 0006.
- [x] One synthetic source annotation and manually constructed expected event committed.
- [x] Structural, arithmetic, deterministic-ID and provenance validation tests pass locally.
- [ ] Schema reviewed against real MOT17 and KITTI Tracking rows before version `1.0.0`.

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
- [ ] Redistribution permission established or Issue #3 acceptance criteria revised explicitly.
- [ ] Issues #2 and #3 closed with acceptance-criterion evidence.

### Remaining Stage 1 work

- [ ] KITTI Tracking fixture documented and committed where permitted.
- [ ] KITTI Tracking parser implemented and tested.
- [ ] Common schema reviewed against both real dataset adapters.
- [ ] Normalised event validation extended for remaining dataset-specific requirements.
- [ ] Event and provenance outputs written in structured formats.
- [ ] Dataset-specific assumptions documented.
- [ ] All Stage 1 automated tests pass in CI.
- [ ] Progress log and risk register reviewed at Stage 1 completion.

Stage 1 is complete only when the completion criteria in `project-plan.md` are satisfied. Parser
implementation alone does not complete Milestone 2 or Stage 1.
