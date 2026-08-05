# Event Sonification Workbench

A reproducible workbench for converting annotated video datasets into deterministic, traceable
events and later audio cues.

## Project

This repository contains the rebuilt artefact for the MSc Data Science dissertation:

**A Reproducible Workbench for Event-Based Sonification of Annotated Video Datasets**

The workbench is research infrastructure. It is not a validated accessibility, navigation, usability
or assistive system.

The bounded dataset scope is MOT17 and KITTI Tracking. The artefact will normalise annotations,
map events to configurable cues, preserve provenance and support technical evaluation.

## Status

Stage 0 is complete. Stage 1 is in progress.

Milestone 1 established common schema version `0.1.0`. The cross-dataset review in Milestone 3
introduced schema `0.2.0`, retaining the event shape while allowing native unnormalised confidence
scores. Both the completed MOT17 and KITTI Tracking adapters emit `0.2.0`.

Issue #4 extends the existing single-event checks to complete event collections. It reports stable,
structured schema, semantic, duplicate-ID and warning diagnostics without modifying event records.
Reports contain deterministic counts and ordered diagnostics and can be written as canonical JSON
with a repeatable SHA-256 hash.

Stage 1 remains incomplete until collection validation passes pull-request CI and the separately
scoped structured event and provenance output work in Issue #6 is complete.

## Repository structure

```text
event-sonification-workbench/
|-- configs/
|   |-- class-mappings/
|   `-- schemas/
|-- docs/
|   |-- data-model/
|   |-- decisions/
|   |-- development/
|   `-- project-management/
|-- src/event_sonification_workbench/
|   `-- adapters/
|-- tests/
|   `-- fixtures/
|-- .env.example
|-- pyproject.toml
`-- README.md
```

## Data configuration

Full datasets remain outside Git. Copy `.env.example` to `.env` and configure local roots. `.env`
is excluded from version control.

```text
MOT17_ROOT=
KITTI_TRACKING_ROOT=
```

MOT17 provenance paths are logical dataset-relative values such as
`MOT17/train/MOT17-02-DPM/gt/gt.txt`. Events do not contain private absolute paths.
KITTI provenance paths are rooted at `KITTI_TRACKING_ROOT`, for example
`training/label_02/0000.txt`, and likewise exclude private absolute paths.

## Installation

```bash
python -m venv .venv
python -m pip install -e ".[dev]"
```

## MOT17 parser

The parser accepts nine-column MOT17 training ground truth and reads sequence values from
`seqinfo.ini`. It converts one-based source frames to zero-based common frames. Native box
coordinates and dimensions are preserved. The evaluation mark remains dataset-specific metadata,
and common confidence is `null`.

Run the preferred real sequence check with `MOT17_ROOT` configured:

```bash
python -m event_sonification_workbench.cli mot17-check \
  --sequence MOT17-02-DPM
```

The command reports parsed rows, validation results and warnings. It does not write event packages.

## KITTI Tracking parser

The parser accepts 17-field KITTI Tracking rows and the optional eighteenth score. It retains
zero-based source frames, converts left/top/right/bottom coordinates to left/top/width/height,
preserves native and common classes, and records truncation, occlusion, observation angle, 3D
geometry and rotation in metadata. Optional scores are preserved without rescaling.

`DontCare` rows are not silently discarded: they become `dont_care` events with track `-1`, native
geometry and `metadata.is_dont_care = true`. The private integration test reads
`KITTI_TRACKING_ROOT` and skips clearly when it is unavailable.

## MOT17 fixture decision

A fixed 12-row extract from `MOT17-02-DPM` is committed under
`tests/fixtures/mot17/dataset-derived/`. The official MOTChallenge website states that datasets
provided on the site are published under Creative Commons Attribution-NonCommercial-ShareAlike 3.0.
The fixture notice records attribution, licence terms, selected source lines and hashes.

The manifest-driven command can reproduce the same fixture from a configured local dataset:

```bash
python -m event_sonification_workbench.cli mot17-fixture \
  --manifest tests/fixtures/mot17/manifest.json \
  --output .local-fixtures/mot17
```

Normal CI also uses a 12-row structurally equivalent synthetic fixture with independently calculated
expected events and deliberately malformed rows.

## KITTI fixture decision

`tests/fixtures/kitti/` contains 12 attributed annotation rows selected deterministically from
training sequence `0000`, plus a manifest containing source line numbers, the selection algorithm,
source/fixture hashes and sequence metadata. KITTI publishes the dataset under Creative Commons
Attribution-NonCommercial-ShareAlike 3.0; the fixture README and licence notice preserve that
attribution and the requested CVPR 2012 citation. No images, video or full annotation file is
included. Synthetic malformed rows are marked separately as project-authored data.

## Validation

Single events and complete MOT17 or KITTI Tracking event collections can be checked against common
schema `0.2.0`. Collection validation preserves input order, treats errors as invalidating, retains
warnings as permitted findings and can write a canonical `validation_report.json`. See
`docs/data-model/event-validation.md` for the API, diagnostic codes and ordering policy.

Run lint and normal tests without requiring the private datasets:

```bash
python -m ruff check .
python -m pytest -m "not integration"
```

Run the complete available suite, including integrations when their roots are configured:

```bash
python -m pytest
```

The integration tests use `MOT17_ROOT` and `KITTI_TRACKING_ROOT` independently and skip clearly when
their private datasets are unavailable. A skip is not evidence of a private-data pass. The CI
workflow runs the non-integration tests and lint checks for pull requests and pushes to `main`.

## Reproducibility controls

- schema, parser and class-mapping versions;
- deterministic event identifiers and canonical JSON hashes;
- dataset-relative source paths and source-row references;
- source, sequence-metadata, mapping and fixture hashes;
- manifest-driven source-line selection;
- schema, semantic, provenance and determinism tests;
- LF-normalised hashed fixtures; and
- explicit evidence boundaries between fixed CI data and local full-dataset integration data.

## Documentation

- `docs/data-model/common-event-schema.md`: provisional common schema contract.
- `docs/data-model/event-validation.md`: single-event and collection validation contract.
- `docs/data-model/mot17-adapter.md`: MOT17 format and conversion rules.
- `docs/data-model/kitti-tracking-adapter.md`: KITTI definitions, conversion and `DontCare` policy.
- `docs/decisions/0007-mot17-ground-truth-mapping.md`: mapping decision.
- `docs/decisions/0008-kitti-tracking-mapping-and-schema-v0.2.0.md`: KITTI and schema decision.
- `docs/decisions/0009-collection-validation-policy.md`: diagnostic and report policy.
- `docs/development/milestone-2-mot17-vertical-slice.md`: development and validation evidence.
- `docs/development/milestone-3-kitti-extension.md`: audit, fixture and integration evidence.
- `docs/development/milestone-2-fixture-licence-resolution.md`: fixture licence decision.
- `tests/fixtures/mot17/README.md`: fixture selection and reproduction evidence.
- `tests/fixtures/kitti/README.md`: KITTI fixture provenance, licence and reproduction evidence.

## Author

Kori Flowers  
MSc Data Science  
University of the West of England  
Student ID: 24046378
