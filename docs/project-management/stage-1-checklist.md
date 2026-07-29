# Stage 1 Checklist

## Data Ingestion and Normalisation

### Milestone 1: schema and synthetic fixture

- [x] Provisional common event schema `0.1.0` defined under `configs/schemas/`.
- [x] Schema conventions and fields documented.
- [x] Significant schema decisions recorded in Decision 0006.
- [x] One synthetic source annotation and manually constructed expected event committed under `tests/fixtures/synthetic/`.
- [x] Structural, arithmetic, deterministic-ID and provenance validation tests pass locally.
- [ ] Schema reviewed against real MOT17 and KITTI Tracking rows before version `1.0.0`.

### Remaining Stage 1 work

- [ ] MOT17 fixture documented and committed where permitted.
- [ ] MOT17 parser implemented and tested.
- [ ] KITTI Tracking fixture documented and committed where permitted.
- [ ] KITTI Tracking parser implemented and tested.
- [ ] Normalised event validation extended for dataset-specific requirements.
- [ ] Event and provenance outputs written in structured formats.
- [ ] Dataset-specific assumptions documented.
- [ ] All Stage 1 automated tests pass in CI.
- [ ] README usage guidance updated for dataset-processing commands.
- [ ] Progress log and risk register reviewed at Stage 1 completion.

Stage 1 is complete only when the completion criteria in `project-plan.md` are satisfied. Completion of Milestone 1 does not complete Issues #2 to #6 or Stage 1 as a whole.
