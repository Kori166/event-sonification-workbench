# Event Sonification Workbench

A reproducible workbench for converting annotated video datasets into deterministic, traceable
events, cue schedules and PCM audio.

## Project

This repository contains the rebuilt artefact for the MSc Data Science dissertation:

**A Reproducible Workbench for Event-Based Sonification of Annotated Video Datasets**

The workbench is research infrastructure. It is not a validated accessibility, navigation, usability
or assistive system.

The bounded dataset scope is MOT17 and KITTI Tracking. The artefact normalises annotations, maps
events to configurable cues, preserves provenance and supports technical evaluation.

## Status

Stages 0, 1 and 2 are complete. Stage 1 closed on 5 August 2026 after real-data event-package
verification. Stage 2 closed on 6 August 2026 after the complete native-annotation to event to cue
to deterministic stereo PCM WAV chain repeated exactly for real MOT17 and KITTI Tracking data.
Stage 3 closed on 6 August 2026. Milestone 1 froze technical-evaluation contract `0.1.0` and
verified it against a manually calculated synthetic oracle; Milestone 2 applied the unchanged
contract to verified MOT17-02-DPM and KITTI Tracking 0000 evidence chains; Milestone 3 generated and
independently audited report-ready tables, deterministic SVG figures and bounded RQ3 findings. RQ3
is supported by technical case-study evidence for those sequences, the baseline preset/renderer and
the recorded environment. It is not perceptual or participant evidence. Stage 4 Milestone 1 Phase 1
is complete. The Phase 2 synchronised MOT17 inspection slice passed researcher-performed controlled
browser acceptance and merged through PR #36. Phase 3 added and accepted the retained KITTI session
through the same frozen architecture, and PR #38 merged the Stage 4 Milestone 1 release candidate.
Milestone 2 then completed the bounded inspection corrections, passed all 16 final researcher
technical browser checks, and merged through PR #40 as
`b6c8310c9f8a731d2ef374e725ba6f99342e85e1`. Stage 4 is complete; Stage 5 remains planned.

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

Stage 2 converted those same collections into 26,960 MOT17 cues plus 3,043 explicit suppressions,
and 711 KITTI cues plus 378 explicit `DontCare` suppressions. Every scheduled cue rendered, every
source event was accounted for, and independent full runs reproduced all 4 event files, 5 cue files
and 3 audio files byte-for-byte and by SHA-256. The complete environment, hashes, WAV properties,
test results and limitations are recorded in `docs/development/stage-2-closeout.md`.

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

## Cross-dataset retained evidence inspection

The Stage 4 workbench is local, read-only research infrastructure for deterministic and traceable
inspection of the retained annotation-to-sonification evidence. It exposes only two committed,
path-free declarations through Workbench Session Contract `0.1.0`:

- MOT17-02-DPM: `session-mot17-mot17-02-dpm-3707826663b210c6`; and
- KITTI Tracking 0000: `session-kitti_tracking-0000-9cae092175c68109`.

Create a local `.env` from `.env.example` and configure `MOT17_ROOT`, `KITTI_TRACKING_ROOT` and
`STAGE2_EVIDENCE_ROOT`. The dataset roots contain private source imagery; the evidence root contains
the retained `mot17/run-a` and `kitti/run-a` event, cue and audio packages. These values remain local
and ignored. From an installed repository environment, the primary launch command is:

```powershell
python -m event_sonification_workbench.cli inspect-session
```

The command validates both committed declarations and their complete Stage 1-3 chains before serving
`http://127.0.0.1:8765/`. Missing or inconsistent private bindings fail with path-free diagnostic
codes before the port is opened. The service binds only to loopback and never modifies an output.

Use the retained-session selector to inspect either dataset. The source panel shows runtime-bound
frames and recorded Stage 1 boxes; transport controls play the exact retained Stage 2 WAV unchanged;
EVENT, CUE and SUPPRESS lanes follow browser audio `currentTime`; selecting a cue displays its
normalised event, logical native annotation/row, configuration and rendered sample range; technical
cards project the verified Stage 3 report directly. Switching sessions clears image, frame,
playback, timeline, cue, trace, metrics, metadata and error state before loading the selected chain.

Frame presentation uses `frame = floor(audio.currentTime * frame_rate)` and half-open frame
intervals. Subtle divisions and a highlighted interval show frame structure separately from the
exact white playback cursor. Only CUE markers are selectable on the canvas. Selecting one pauses
playback, seeks to its retained start and immediately synchronises the slider and numeric transport
time. Represented source-video boxes and frame cue buttons invoke that same exact retained cue path;
suppressed boxes remain contextual. Selection loads the recorded source frame and presents every
cue retained for that frame as a complete control group. Frame cue controls remain in deterministic
time/track/cue order and are not truncated by the one-second evidence window.

The technical baseline uses event time for when the cue plays, horizontal object position for
left/right placement, vertical object position for pitch and bounding-box area for loudness. It is
not perceptually validated. The class modifier is recorded in provenance for traceability but is not
applied by the current renderer. Bounding-box area is an imperfect
apparent-scale proxy, not depth: pose-dependent pedestrian width can change amplitude without a
meaningful apparent-distance change. Height-based or smoothed-height alternatives are possible
future experiments and are not implemented here.

Repository content includes code, schemas, path-free retained declarations, fixed public test
fixtures and canonical Stage 3 reports. Private source datasets, retained full Stage 1/2 packages
and WAV files remain local. The browser is presentation-only: it does not parse annotations,
normalise events, schedule cues, render audio, evaluate metrics or regenerate canonical evidence.

The service is loopback-only and exposes no write, upload, authentication, database or analytics
feature. It is inspection/demonstration infrastructure, not participant, accessibility, usability,
navigation, perceptual-effectiveness or safety evidence. The MOT17 and KITTI controlled browser
passes are engineering acceptance only; see the Phase 2 and Phase 3 development records. R20 remains
open: the interface does not resolve dense-audio interpretation or establish a perceptual benefit.

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

Independent packages of the same type can be compared exactly:

```powershell
python -m event_sonification_workbench.cli compare-packages `
  --left-package <first-package> `
  --right-package <second-package>
```

The path-free deterministic report covers every expected package file, exact byte equality and
independent SHA-256 values. Any mismatch is named and returns a nonzero status.

## Technical evaluation contract

Stage 3 Milestone 1 defines event coverage/accounting, three timing-error domains, resolved-link
traceability, cue density, half-open interval overlap burden and four separate reproducibility
levels in contract `0.1.0`. Every rate retains its numerator and denominator; zero denominators are
`null`. Suppressed events remain distinct from eligible misses, and traceability requires records
and hashes to agree rather than merely containing plausible identifiers.

The minimum evaluator accepts a prepared, validated event/cue/suppression/render record chain:

```powershell
python -m event_sonification_workbench.cli evaluate-technical `
  --input tests/fixtures/evaluation_oracle/input.json `
  --output outputs/technical_evaluation_report.json
```

It writes canonical JSON with a content-derived evaluation run ID, deterministic diagnostics,
input versions/hashes, timeline, metric counts and output hash scope. The committed fixture is
synthetic: its five events, five cues, one suppression and 10 Hz render timeline are independently
calculated in `tests/fixtures/evaluation_oracle/oracle-calculation.md`. Fault cases cover eligible
misses, orphans, contradictory outcomes, broken provenance and timing displacement.

Milestone 2 adds a strict adapter that joins already verified event, cue and audio package contracts
without recalculating Stage 1 or Stage 2 records:

```powershell
python -m event_sonification_workbench.cli prepare-technical-evaluation `
  --event-package <event-package> `
  --cue-package <cue-package> `
  --audio-package <audio-package> `
  --repeat-event-package <repeat-event-package> `
  --repeat-cue-package <repeat-cue-package> `
  --repeat-audio-package <repeat-audio-package> `
  --output <technical-evaluation-input.json>
```

The assembler checks exact package membership, canonical serialisation, documented hashes, content
identities, ordering, source references and cross-stage links, then writes a content-derived input
identity and hash manifest. Full inputs remain ignored because they contain generated full-sequence
records.

Under the unchanged contract, MOT17 accounts for 30,003 events as 26,960 represented and 3,043
intentionally suppressed, while KITTI accounts for 1,089 events as 711 represented and 378
intentionally suppressed `DontCare` events. Both have zero eligible misses, zero broken links and
complete eligible-event coverage. The rendered timelines contain 1,342.1838698971126 and
46.10894941634241 cues/second respectively; these are descriptive technical values, not listener-
quality judgements. Canonical report SHA-256 values are
`d847e805d0b2d7ccd50cd315bbcecfc0ad525f40e7c4c2013938f955d20f13e5` and
`b5589590a8c645bd7b5654d0318bf90fdb412f987719c26c2374bf3e487f9ff2`.

See `docs/evaluation/evidence/`, the record-level traceability audit and the bounded cross-dataset
summary for every numerator, denominator, timing statistic, overlap value, hash and repeat result.
No perceptual, participant, accessibility, usability, navigation or safety conclusion follows from
these technical metrics. Cross-environment byte identity remains untested.

The audited reporting derivative can be rebuilt entirely from the committed canonical reports:

```powershell
python -m event_sonification_workbench.cli generate-stage3-report-evidence `
  --mot17-report docs/evaluation/evidence/mot17/mot17_technical_evaluation_report.json `
  --kitti-report docs/evaluation/evidence/kitti/kitti_technical_evaluation_report.json `
  --output docs/evaluation/reporting `
  --replace-generated
```

The generator verifies both source hashes and the frozen schema, resolves structural JSON Pointers,
preserves exact canonical raw scalars, applies documented display formatting and audits every table,
figure and claim reference. The committed package contains 134 manifested values, 136 table cells,
20 figure data points and 12 principal claims with zero automated or manual mismatches. Two isolated
fresh builds produced all 24 generator-owned files byte-identically. Exact hashes and the bounded
RQ3 answer are in `docs/evaluation/reporting/` and `docs/development/stage-3-closeout.md`.

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
- versioned evaluation policy/report schemas with explicit rate denominators and null rules;
- a manually calculated synthetic evaluation oracle and deterministic canonical report hash;
- a versioned real-data experiment/environment manifest and verified package-to-evaluator adapter;
- three-run semantic and canonical-byte comparison reports for real MOT17 and KITTI case studies;
- deterministic dataset summaries and selected record-level traceability audits;
- structural presentation-value provenance, deterministic report-ready tables/SVG figures and
  automated plus independent presentation audits;
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
- `docs/evaluation/technical-evaluation-contract-v0.1.0.md`: frozen metric definitions, inputs,
  boundaries, failure policy and deterministic report contract.
- `docs/evaluation/stage-3-real-data-evaluation-protocol.md`: pre-result real-data scope, integrity
  gates, repeat policy and prohibited interpretations.
- `docs/evaluation/evidence/`: canonical reports, machine-readable/CSV summaries, comparison
  reports, input manifests and selected-record audits.
- `docs/evaluation/stage-3-real-data-traceability-audit.md`: deterministic source-to-WAV and
  source-to-suppression selections.
- `docs/evaluation/stage-3-cross-dataset-technical-summary.md`: bounded descriptive comparison.
- `docs/evaluation/reporting/`: deterministic report-ready tables, SVG figures, value manifest,
  claim matrix, bounded RQ3 findings and automated/manual audits.
- `docs/data-model/mot17-adapter.md`: MOT17 format and conversion rules.
- `docs/data-model/kitti-tracking-adapter.md`: KITTI definitions, conversion and `DontCare` policy.
- `docs/decisions/0007-mot17-ground-truth-mapping.md`: mapping decision.
- `docs/decisions/0008-kitti-tracking-mapping-and-schema-v0.2.0.md`: KITTI and schema decision.
- `docs/decisions/0009-collection-validation-policy.md`: diagnostic and report policy.
- `docs/decisions/0010-deterministic-output-package.md`: deterministic package format decision.
- `docs/decisions/0011-versioned-preset-and-cue-schedule.md`: Stage 2 scheduling decision.
- `docs/decisions/0012-deterministic-wav-rendering.md`: renderer, mixing and PCM policy decision.
- `docs/decisions/0013-technical-evaluation-contract.md`: Stage 3 metric and interpretation policy.
- `docs/decisions/0014-real-data-evaluation-evidence.md`: real package reuse, evidence storage and
  supplemental traceability boundary.
- `docs/decisions/0015-audited-reporting-evidence.md`: deterministic presentation, formatting and
  claim-audit policy.
- `docs/decisions/0016-workbench-session-and-inspection-layer.md`: frozen session contract and
  evidence boundary.
- `docs/decisions/0017-local-synchronised-inspection-architecture.md`: local service, single-clock
  frontend and dependency decision.
- `docs/development/milestone-2-mot17-vertical-slice.md`: development and validation evidence.
- `docs/development/milestone-3-kitti-extension.md`: audit, fixture and integration evidence.
- `docs/development/milestone-2-fixture-licence-resolution.md`: fixture licence decision.
- `docs/development/stage-1-closeout.md`: real-data package, repeat-run and quality-gate evidence.
- `docs/development/stage-2-closeout.md`: real event-to-cue-to-WAV hashes, repeat evidence and
  Stage 3 handover.
- `docs/development/stage-3-milestone-1.md`: synthetic-oracle results, quality evidence and limits.
- `docs/development/stage-3-milestone-2-closeout.md`: real-data reports, repeats, quality evidence
  and RQ3 boundary.
- `docs/development/stage-3-closeout.md`: all Stage 3 identities, report-ready hashes, audit and
  quality evidence, bounded RQ3 answer and Stage 4 handover.
- `docs/development/stage-4-milestone-1-phase-2.md`: inspection implementation, private gates,
  browser acceptance state and Phase 3 boundary.
- `docs/project-management/stage-2-checklist.md`: completed Stage 2 implementation and close-out
  gates.
- `docs/project-management/stage-3-checklist.md`: completed contract, real-data and report-ready
  audit gates.
- `tests/fixtures/mot17/README.md`: fixture selection and reproduction evidence.
- `tests/fixtures/kitti/README.md`: KITTI fixture provenance, licence and reproduction evidence.
- `outputs/README.md`: generated-output storage boundary.

## Author

Kori Flowers  
MSc Data Science  
University of the West of England  
Student ID: 24046378
