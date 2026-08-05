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

Stage 0 and Stage 1 are complete. Stage 1 closed on 5 August 2026 after real-data package and
repeat-run verification for MOT17 and KITTI Tracking. Stage 2 is active: Milestone 1 provides the
versioned cue schedule and Milestone 2 adds configured deterministic stereo PCM WAV rendering.

Milestone 1 established common schema version `0.1.0`. The cross-dataset review in Milestone 3
introduced schema `0.2.0`, retaining the event shape while allowing native unnormalised confidence
scores. Both the completed MOT17 and KITTI Tracking adapters emit `0.2.0`.

Issues #4, #5 and #6 are closed. Their implementations merged through pull requests #16, #15 and
#17 respectively. Common schema `0.2.0` is current, and validated events can be written to canonical
JSON, fixed-column CSV, run metadata and a provenance log beneath a content-derived run ID.

The close-out converted real sequence `MOT17-02-DPM` into 30,003 valid events and KITTI Tracking
sequence `0000` into 1,089 valid events. Separate repeat runs produced identical run IDs, event
ordering, package bytes and SHA-256 values. MOT17 retained 988 permitted out-of-image geometry
warnings; KITTI produced no warnings. Full evidence is recorded in
`docs/development/stage-1-closeout.md`.

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

## Structured event outputs

Validated sequence events can be written to an ignored deterministic package:

```text
outputs/<run-id>/
|-- events.json
|-- events.csv
|-- run_metadata.json
`-- provenance_log.json
```

The event files use the documented dataset, sequence, frame, track ID, source-row and event-ID
ordering. Package content contains logical source/configuration references and hashes, never private
dataset roots or output-directory paths. It contains no changing wall-clock timestamp.

Run either adapter-to-package command with its private root configured:

```bash
python -m event_sonification_workbench.cli mot17-package \
  --sequence MOT17-02-DPM \
  --output-directory outputs

python -m event_sonification_workbench.cli kitti-package \
  --sequence 0000 \
  --output-directory outputs
```

Both commands parse, collection-validate and then write. They refuse parser errors or invalid
collections. Generated packages remain ignored and must not be committed. The exact format, CSV
columns, hash scopes and overwrite policy are documented in `docs/data-model/output-package.md`.

## Deterministic cue scheduling

Stage 2 Milestone 1 maps a valid schema `0.2.0` event package through the versioned baseline preset:

```bash
python -m event_sonification_workbench.cli schedule-cues \
  --event-package outputs/<stage-1-run-id> \
  --preset configs/sonification/presets/baseline-v0.1.0.json \
  --output-directory outputs
```

The command independently checks package integrity, recorded validation status, schema/semantic
validity and deterministic event order. It refuses incompatible presets, malformed packages and
unsafe paths. Each accepted event becomes exactly one cue or one explicit suppression. The
baseline records class exclusions, low available confidence, frame-stride policy and `DontCare`
treatment rather than silently dropping events.

The ignored content-derived run directory contains:

```text
outputs/<cue-run-id>/
|-- cue_schedule.json
|-- cue_schedule.csv
|-- cue_log.json
|-- suppression_log.json
`-- sonification_metadata.json
```

Outputs preserve source event/file/row and preset identity, use canonical JSON and LF-stable CSV,
and repeat byte-for-byte for identical input and configuration. The baseline values are configurable
technical choices, not perceptual or accessibility findings.
See `docs/data-model/sonification-preset.md` and `docs/data-model/cue-schedule.md`.

## Deterministic WAV rendering

Stage 2 Milestone 2 verifies a cue package before rendering it through renderer configuration
`0.1.0`. In PowerShell:

```powershell
python -m event_sonification_workbench.cli render-audio `
  --cue-package outputs/<cue-run-id> `
  --renderer-config configs/sonification/renderers/baseline-v0.1.0.json `
  --output-directory outputs
```

The ignored content-derived audio run contains `sonification.wav`, `render_log.json` and
`renderer_metadata.json`. The baseline is stereo, 44,100 Hz, signed 16-bit little-endian PCM with
fixed-phase sine cues, linear attack/release and pan, ordered overlap summation and conditional
peak limiting. Time placement uses decimal round-half-up; quantisation occurs after mixing and any
global gain. Identical fixture runs produce identical bytes and hashes in the tested environment.
This is reproducibility evidence for technical behaviour, not evidence of perceptual quality,
accessibility, usefulness or safety. See `docs/data-model/audio-rendering.md`.

## Reproducibility controls

- schema, parser and class-mapping versions;
- deterministic event identifiers and canonical JSON hashes;
- dataset-relative source paths and source-row references;
- source, sequence-metadata, mapping and fixture hashes;
- manifest-driven source-line selection;
- content-derived output run IDs, canonical package JSON and LF-stable CSV;
- versioned preset validation, deterministic cue IDs and complete cue-or-suppression accounting;
- canonical cue/suppression logs and content-derived schedule run IDs;
- versioned renderer configuration, verified cue inputs and content-derived audio run IDs;
- explicit sample placement, envelope, panning, mixing, normalisation and PCM quantisation rules;
- file-level output hashes and path-free run provenance;
- schema, semantic, provenance and determinism tests;
- LF-normalised hashed fixtures; and
- explicit evidence boundaries between fixed CI data and local full-dataset integration data.

## Documentation

- `docs/data-model/common-event-schema.md`: current common schema `0.2.0` contract.
- `docs/data-model/event-validation.md`: single-event and collection validation contract.
- `docs/data-model/output-package.md`: JSON, CSV, metadata and provenance output contract.
- `docs/data-model/sonification-preset.md`: preset schema, baseline formulas and suppression policy.
- `docs/data-model/cue-schedule.md`: schedule input gate, records, files, IDs and hash contract.
- `docs/data-model/audio-rendering.md`: renderer input gate, synthesis, WAV and provenance contract.
- `docs/data-model/mot17-adapter.md`: MOT17 format and conversion rules.
- `docs/data-model/kitti-tracking-adapter.md`: KITTI definitions, conversion and `DontCare` policy.
- `docs/decisions/0007-mot17-ground-truth-mapping.md`: mapping decision.
- `docs/decisions/0008-kitti-tracking-mapping-and-schema-v0.2.0.md`: KITTI and schema decision.
- `docs/decisions/0009-collection-validation-policy.md`: diagnostic and report policy.
- `docs/decisions/0010-deterministic-output-package.md`: deterministic package format decision.
- `docs/decisions/0011-versioned-preset-and-cue-schedule.md`: Stage 2 scheduling decision.
- `docs/decisions/0012-deterministic-wav-rendering.md`: renderer, mixing and PCM policy decision.
- `docs/development/milestone-2-mot17-vertical-slice.md`: development and validation evidence.
- `docs/development/milestone-3-kitti-extension.md`: audit, fixture and integration evidence.
- `docs/development/milestone-2-fixture-licence-resolution.md`: fixture licence decision.
- `docs/development/stage-1-closeout.md`: real-data package, repeat-run and quality-gate evidence.
- `docs/project-management/stage-2-checklist.md`: active Stage 2 implementation gates.
- `tests/fixtures/mot17/README.md`: fixture selection and reproduction evidence.
- `tests/fixtures/kitti/README.md`: KITTI fixture provenance, licence and reproduction evidence.
- `outputs/README.md`: generated-output storage boundary.

## Author

Kori Flowers  
MSc Data Science  
University of the West of England  
Student ID: 24046378
