# Stage 1 Close-out

## Status and scope

Stage 1, Data Ingestion and Normalisation, completed on 5 August 2026. This close-out verifies the
merged pipeline against private real data for the selected MOT17 and KITTI Tracking sequences. It
covers parsing, common schema `0.2.0`, collection validation, deterministic JSON/CSV output, run
metadata, provenance, hashes and repeated execution.

Issues #4, #5 and #6 are closed as completed. Pull requests #16, #15 and #17 respectively are
merged into `main`. Schema `configs/schemas/event.schema.v0.2.0.json` remains current; the close-out
found no schema defect.

This work does not implement event-to-cue mapping, cue scheduling, suppression, audio rendering or
technical evaluation. Those concerns remain in Stages 2 and 3.

## Private-data boundary

Commands used `MOT17_ROOT` and `KITTI_TRACKING_ROOT`, loaded locally without printing or recording
their values. Packages contain dataset-relative source/configuration references only. Full-data
packages remain below ignored `outputs/` and are not committed.

## Real package results

### MOT17

Command sequence: `MOT17-02-DPM`; normalised source sequence: `mot17-02-dpm`.

| Field | Actual result |
|---|---|
| Run ID | `run-mot17-mot17-02-dpm-03074d7ff016652e` |
| Event count | 30,003 |
| Validation | `valid` |
| Error count | 0 |
| Warning count | 988 |
| Schema version | `0.2.0` |
| Parser version | `0.1.0` |
| Source-file SHA-256 | `2e3ecb488da8886d3200d402b2b08890c6d2879923839444e9b74fa43a551440` |
| `events.json` SHA-256 | `880232f6ea0696a8c74600f51fe46e8221ff8ee40536dbef4570921a8779b96e` |
| `events.csv` SHA-256 | `2b4b5e3dac8e70661719b555fc6578a088e8b3aa18758f99447d3137dd43f3ee` |
| `run_metadata.json` SHA-256 | `e247260608d4aaac72f2b5d3e3a602ebe29d7b8e8d2dedd10a2320b6456c7bee` |
| `provenance_log.json` SHA-256 | `6b44534de1c9ffb9f1f4b7f2d033fa954e08c4dab219e68d8333ef649f55ae5f` |

The collection is valid because warnings are permitted and do not invalidate events. All 988 are
the documented `bbox_outside_image` condition: MOT17 boxes that extend beyond the declared image
boundary are retained unchanged rather than clipped or removed.

### KITTI Tracking

Command and normalised source sequence: `0000`.

| Field | Actual result |
|---|---|
| Run ID | `run-kitti_tracking-0000-94a4cdc57ff00109` |
| Event count | 1,089 |
| Validation | `valid` |
| Error count | 0 |
| Warning count | 0 |
| Schema version | `0.2.0` |
| Parser version | `0.1.0` |
| Source-file SHA-256 | `97f772a27181dfc7ef51b3e64b86bd42e682753b6855fdc58d259ecbed501fd4` |
| `events.json` SHA-256 | `542389e4a783380191fdc228b83c37309fa4d483d58913978881ee3cfb6f57a2` |
| `events.csv` SHA-256 | `5068c491c8feace0ba39b91f9398e7b96b6310174c5d63b28a1792c4d8fb0db5` |
| `run_metadata.json` SHA-256 | `89cefd74709226303257f6c315368b75b8bb52e84c4c473c03f0f5bf9a37a47b` |
| `provenance_log.json` SHA-256 | `916703854628b24b0503a56f5bb754204691fe6aa517169fadb3dd5bc2968325` |

### Preserved configuration evidence

| Configuration | Version | SHA-256 |
|---|---:|---|
| Common event schema | `0.2.0` | `a78a6d9a97c9257741678dcbb9422153026507f64f8010a6366122ce72397680` |
| MOT17 class mapping | `0.1.0` | `1bd22ee6b313396a16589ae10356e7de569546872ef4a4687a9610cbbb29aeac` |
| KITTI Tracking class mapping | `0.1.0` | `49ff366b6768ab3803dd0dd125c7ad2092a0eff298400485dd6b311c612c1b14` |
| MOT17 sequence metadata | n/a | `5c9a86813ed1e4bf640b11785e9dc51f443712d721f9cc5e334b7e0f21606ad6` |

For each run, the physical SHA-256 values match the metadata/provenance entries within their
documented hash scopes. Each package contains exactly `events.json`, `events.csv`,
`run_metadata.json` and `provenance_log.json`. Event counts agree between metadata and JSON, and
events are ordered by dataset, sequence, frame, track ID, source row and event ID.

## Reproducibility result

Each package command was run a second time into a separate ignored temporary output root. The
second-run package was compared with the primary package before the workspace comparison directory
was removed.

| Check | MOT17 | KITTI Tracking |
|---|---:|---:|
| Same run ID | Pass | Pass |
| Same deterministic event order | Pass | Pass |
| Byte-identical `events.json` | Pass | Pass |
| Byte-identical `events.csv` | Pass | Pass |
| Byte-identical `run_metadata.json` | Pass | Pass |
| Byte-identical `provenance_log.json` | Pass | Pass |
| Identical hashes for all four files | Pass | Pass |

No reproducibility difference or output defect was found.

## Quality checks

Both private roots were active for the integration and complete-suite commands; neither private
integration was skipped.

| Command | Actual result |
|---|---|
| `python -m ruff check .` | Passed: `All checks passed!` |
| `python -m pytest -m "not integration"` | 121 passed, 2 deselected in 13.43 s |
| `python -m pytest -m integration` | 2 passed, 121 deselected in 58.24 s |
| `python -m pytest` | 123 passed in 66.44 s |

## Problems encountered

- The desktop process did not inherit the two root variables. Only `MOT17_ROOT` and
  `KITTI_TRACKING_ROOT` were loaded from the ignored local environment file into each command
  process; values were never printed or written to evidence.
- Local `main` contained independent unpublished history and could not be fast-forwarded. The
  close-out branch was created directly from fetched `origin/main`, leaving local history intact.
- An initial one-second command wrapper expired before real package generation completed. Both
  package commands were rerun to completion, and evidence was read from the generated packages.
- Recursive deletion of the comparison directory was blocked by the execution safety policy. It
  was verified and moved out of the workspace into the system temporary area instead.

## Limitations carried forward

- Close-out evidence covers the selected real sequences, not every sequence in either dataset.
- The 988 MOT17 out-of-image warnings are retained source geometry; downstream mapping must not
  mistake them for conversion errors or silently clip them.
- KITTI sequence `0000` contains no optional confidence-score rows, so real score preservation
  remains supported by parser fixtures and tests rather than this sequence.
- Full-data packages are private local evidence and are intentionally absent from Git.
- MOT17 fixture redistribution remains governed by the explicit licence risk in the risk register.
- Schema `0.2.0` is current but is not renamed to `1.0.0` merely because Stage 1 closed.
- No sonification, audio output or technical evaluation exists as a result of this close-out.

## Completion criteria

| Stage 1 criterion | Evidence | Result |
|---|---|---:|
| Both datasets convert into schema `0.2.0` | Real package metadata and 31,092 total events | Satisfied |
| Both collections pass validation | MOT17 valid with 0 errors; KITTI valid with 0 errors | Satisfied |
| JSON and CSV are written | Exact four-file membership in both packages | Satisfied |
| Metadata and provenance are written | Both files present with matching output hashes | Satisfied |
| Source and configuration hashes are preserved | Recorded source, schema, mapping and sequence hashes | Satisfied |
| Repeated runs are deterministic | Same IDs, order, bytes and all file hashes | Satisfied |
| All available tests pass | Ruff, 121 unit/fixture tests, 2 private integrations, 123 total | Satisfied |
| Assumptions and limitations are documented | Adapter docs, decisions, risks and this record | Satisfied |

All Stage 1 completion criteria are satisfied. Stage 2 is the next active stage and remains
unimplemented at this close-out point. Stage 2 was subsequently completed on 6 August 2026; see
`docs/development/stage-2-closeout.md`.
