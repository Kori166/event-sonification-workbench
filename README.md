# Event Sonification Workbench

A reproducible workbench for converting annotated video tracking data into normalised events, deterministic audio cues, traceable PCM audio and technically evaluated outputs.

This repository contains the MSc Data Science project:

**A Reproducible Workbench for Event Based Sonification of Annotated Video Datasets**

The workbench is research infrastructure. It is **not** a validated accessibility, navigation, usability or assistive system.

## Try The Workbench

### Hosted Workbench

[**Open Live Workbench →**](https://event-sonification-workbench.onrender.com/)

The hosted read-only workbench provides one-click inspection of the two retained technical evaluation cases:

- **MOT17-02-DPM**
- **KITTI Tracking sequence 0000**

The deployment uses the retained evidence and bounded deployment package produced for the project. It provides convenient inspection of the research artefact and does not constitute additional usability, accessibility or perceptual evaluation.

Availability depends on the external Render service. If the hosted service is sleeping or unavailable,
use the full local workbench described below. The deployment verifies and extracts a 234 MiB retained
bundle before its health endpoint becomes available, so a cold start can be slow.

### Full Local Workbench

The complete research workbench uses locally obtained MOT17 and KITTI Tracking media together with retained Stage 1-3 evidence packages. These large/private artefacts are deliberately not stored in Git.

See [Full Local Setup](#full-local-setup) below.

---

## What The Workbench Does

The implemented research workflow is:

```text
MOT17 / KITTI annotations
        ↓
dataset-specific adapters
        ↓
common event schema 0.2.0
        ↓
validated event packages
        ↓
versioned sonification mapping
        ↓
cues + explicit suppressions
        ↓
deterministic stereo PCM WAV
        ↓
technical evaluation
        ↓
read-only inspection workbench
```

The pipeline preserves source identity and provenance so that generated cues and suppressions can be traced back to the source annotation, configuration and, for cues, rendered sample range.

The bounded dataset cases used in the completed technical evaluation are:

- **MOT17-02-DPM**
- **KITTI Tracking sequence 0000**

## Quick Access

| Looking For | Location |
|---|---|
| Marker documentation route | [`docs/README.md`](docs/README.md) |
| Workbench source code | [`src/event_sonification_workbench/`](src/event_sonification_workbench/) |
| Canonical technical evaluation evidence | [`docs/evaluation/evidence/`](docs/evaluation/evidence/) |
| Report-ready summary and tables | [`docs/evaluation/reporting/`](docs/evaluation/reporting/) |
| Technical evaluation contract | [`docs/evaluation/technical-evaluation-contract-v0.1.0.md`](docs/evaluation/technical-evaluation-contract-v0.1.0.md) |
| Common event schema and adapter contracts | [`docs/data-model/common-event-schema.md`](docs/data-model/common-event-schema.md) |
| Sonification and rendering contract | [`docs/data-model/sonification-and-rendering.md`](docs/data-model/sonification-and-rendering.md) |
| Workbench session contract | [`docs/data-model/workbench-session.md`](docs/data-model/workbench-session.md) |
| Design decisions | [`docs/decisions/`](docs/decisions/) |
| Project plan | [`docs/project-management/project-plan.md`](docs/project-management/project-plan.md) |
| Progress log | [`docs/project-management/progress-log.md`](docs/project-management/progress-log.md) |
| Risk register | [`docs/project-management/risk-register.md`](docs/project-management/risk-register.md) |
| Stage checklists | [`docs/project-management/`](docs/project-management/) |
| Automated tests and fixtures | [`tests/`](tests/) |

### Marker Inspection Route

For a concise inspection of the submitted artefact:

1. Read the project boundary and architecture on this page.
2. Review the [common event schema and adapter contract](docs/data-model/common-event-schema.md).
3. Review the [sonification and rendering contract](docs/data-model/sonification-and-rendering.md).
4. Inspect the [technical evaluation summary](docs/evaluation/stage-3-cross-dataset-technical-summary.md)
   and [canonical evidence](docs/evaluation/evidence/).
5. Open the [retained session contract](docs/data-model/workbench-session.md), then inspect the
   browser workbench locally or through the hosted deployment when available.
6. Use the [documentation index](docs/README.md) for decisions and project management evidence.

### Direct Component Map

| Component | Implementation |
|---|---|
| MOT17 adapter | [`src/event_sonification_workbench/adapters/mot17.py`](src/event_sonification_workbench/adapters/mot17.py) |
| KITTI Tracking adapter | [`src/event_sonification_workbench/adapters/kitti_tracking.py`](src/event_sonification_workbench/adapters/kitti_tracking.py) |
| Common event validation | [`src/event_sonification_workbench/event_validation.py`](src/event_sonification_workbench/event_validation.py) |
| Sonification preset validation | [`src/event_sonification_workbench/sonification/preset.py`](src/event_sonification_workbench/sonification/preset.py) |
| Cue scheduling and suppression | [`src/event_sonification_workbench/sonification/scheduler.py`](src/event_sonification_workbench/sonification/scheduler.py) |
| Deterministic audio renderer | [`src/event_sonification_workbench/sonification/audio_renderer.py`](src/event_sonification_workbench/sonification/audio_renderer.py) |
| Technical evaluation input | [`src/event_sonification_workbench/technical_evaluation_input.py`](src/event_sonification_workbench/technical_evaluation_input.py) |
| Technical evaluator | [`src/event_sonification_workbench/technical_evaluation.py`](src/event_sonification_workbench/technical_evaluation.py) |
| Reporting evidence generator | [`src/event_sonification_workbench/reporting_evidence.py`](src/event_sonification_workbench/reporting_evidence.py) |
| Retained session validation | [`src/event_sonification_workbench/workbench/session.py`](src/event_sonification_workbench/workbench/session.py) |
| Inspection model and service | [`src/event_sonification_workbench/workbench/inspection.py`](src/event_sonification_workbench/workbench/inspection.py), [`server.py`](src/event_sonification_workbench/workbench/server.py) |
| Browser interface | [`index.html`](src/event_sonification_workbench/workbench/static/index.html), [`app.js`](src/event_sonification_workbench/workbench/static/app.js) |

## Project Status

| Stage | Status |
|---|---|
| 0. Project Setup | Complete |
| 1. Data Ingestion and Normalisation | Complete |
| 2. Sonification | Complete |
| 3. Technical Evaluation | Complete |
| 4. Artefact Assembly, Validation and Release | Complete |
| 5. Reporting and Viva Preparation | Report and artefact prepared for submission; viva preparation ongoing |

The technical artefact and technical evaluation are complete. The report and artefact are prepared
for submission. Remaining activity is researcher controlled submission and viva preparation. Full
historical stage status is preserved in
[`docs/project-management/project-plan.md`](docs/project-management/project-plan.md).

## Repository Structure

```text
event-sonification-workbench/
├── configs/                         # schemas, mappings and renderer configuration
├── docs/
│   ├── data-model/                  # consolidated technical contracts
│   ├── decisions/                   # architecture and research decisions
│   ├── evaluation/                  # canonical Stage 3 evidence and reporting outputs
│   └── project-management/          # plan, progress, risks and stage records
├── src/event_sonification_workbench/
│   ├── adapters/                    # MOT17 and KITTI Tracking adapters
│   └── workbench/                   # read-only inspection service and browser UI
├── tests/                           # unit, contract, fixture and integration tests
├── .env.example
├── pyproject.toml
└── README.md
```

## What Is Included In Git

The repository contains the material needed to inspect the implementation and its documented technical evidence:

- Python source code;
- event, preset, renderer and evaluation schemas;
- deterministic mapping and rendering configuration;
- fixed public/synthetic test fixtures;
- automated tests;
- canonical Stage 3 technical evaluation reports;
- audited report-ready summary and tables;
- consolidated technical documentation;
- design decisions and project-management evidence; and
- path-free retained workbench session declarations.

The following remain outside Git:

- full MOT17 and KITTI Tracking datasets;
- source video/image sequences;
- complete generated Stage 1 and Stage 2 packages;
- retained full WAV files; and
- machine-specific paths or local environment settings.

This boundary keeps the repository portable and avoids treating externally obtained datasets or retained large outputs as ordinary source files.

## Installation

### Requirements

- Python **3.11 or later**
- Git
- A supported modern browser for the inspection interface

Clone and enter the repository:

```bash
git clone https://github.com/Kori166/event-sonification-workbench.git
cd event-sonification-workbench
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it.

**Windows PowerShell**

```powershell
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux**

```bash
source .venv/bin/activate
```

Install the project and development dependencies:

```bash
python -m pip install -e ".[dev]"
```

## Run The Repository Tests

Run linting and the normal test suite without private datasets:

```bash
python -m ruff check .
python -m pytest -m "not integration"
```

Run the complete available suite when local dataset/evidence roots are configured:

```bash
python -m pytest
```

Integration tests use the configured external roots and skip when those resources are unavailable. A skipped integration test is not evidence that the private-data path passed.

## Full Local Setup

The complete inspection workbench requires three local roots.

Copy the example environment file:

**Windows PowerShell**

```powershell
Copy-Item .env.example .env
```

**macOS / Linux**

```bash
cp .env.example .env
```

Configure:

```text
MOT17_ROOT=
KITTI_TRACKING_ROOT=
STAGE2_EVIDENCE_ROOT=
```

Where:

- `MOT17_ROOT` points to the locally obtained MOT17 dataset;
- `KITTI_TRACKING_ROOT` points to the locally obtained KITTI Tracking dataset; and
- `STAGE2_EVIDENCE_ROOT` points to the retained event, cue and audio evidence tree used by the accepted Stage 3/4 sessions.

The `.env` file is ignored by Git and must not be committed.

### Launch The Local Workbench

From the installed repository environment:

```bash
python -m event_sonification_workbench.cli inspect-session
```

Then open:

```text
http://127.0.0.1:8765/
```

Before serving the interface, the command validates the retained Stage 1-3 evidence chain. Missing or inconsistent local bindings fail before the service is opened.

The browser interface is read-only. It does not parse annotations, regenerate events, schedule new cues, render new audio or recalculate evaluation metrics.

## Using The Inspection Workbench

The workbench exposes the retained MOT17 and KITTI Tracking sessions through the same inspection architecture.

It provides:

- source-frame display with recorded bounding boxes;
- playback of the retained Stage 2 audio;
- synchronised EVENT, CUE and SUPPRESS timeline lanes;
- frame-scoped cue controls;
- cue- and suppression-to-source provenance inspection;
- rendered sample-range information for cues; and
- technical metrics projected directly from the retained Stage 3 report.

Selecting a cue or suppression pauses playback and seeks to the retained outcome time. Cue inspection includes its rendered sample range; suppression inspection shows the retained reason and has no Render stage.

## Reproducing The Processing Pipeline

The commands below are the main processing path. Detailed contracts and field definitions are consolidated in the technical documentation rather than repeated here.

### 1. Create Validated Event Packages

```bash
python -m event_sonification_workbench.cli mot17-package \
  --sequence MOT17-02-DPM \
  --output-directory outputs

python -m event_sonification_workbench.cli kitti-package \
  --sequence 0000 \
  --output-directory outputs
```

See [`docs/data-model/common-event-schema.md`](docs/data-model/common-event-schema.md).

### 2. Schedule Cues And Suppressions

```bash
python -m event_sonification_workbench.cli schedule-cues \
  --event-package outputs/<stage-1-run-id> \
  --preset configs/sonification/presets/baseline-v0.1.0.json \
  --output-directory outputs
```

Each accepted valid event produces either one cue or one explicit suppression record.

See [`docs/data-model/sonification-and-rendering.md`](docs/data-model/sonification-and-rendering.md).

### 3. Render Deterministic Audio

```bash
python -m event_sonification_workbench.cli render-audio \
  --cue-package outputs/<cue-run-id> \
  --renderer-config configs/sonification/renderers/baseline-v0.1.0.json \
  --output-directory outputs
```

The baseline renderer produces stereo 44.1 kHz signed 16-bit PCM audio with deterministic sample placement under the recorded configuration.

See [`docs/data-model/sonification-and-rendering.md`](docs/data-model/sonification-and-rendering.md).

### 4. Run Technical Evaluation

A small committed synthetic oracle can be evaluated directly:

```bash
python -m event_sonification_workbench.cli evaluate-technical \
  --input tests/fixtures/evaluation_oracle/input.json \
  --output outputs/technical_evaluation_report.json
```

The full real-data evaluation uses prepared and verified event, cue, suppression and render evidence. Metric semantics are frozen in [`docs/evaluation/technical-evaluation-contract-v0.1.0.md`](docs/evaluation/technical-evaluation-contract-v0.1.0.md).

## Technical Evaluation Evidence

Under Technical Evaluation Contract `0.1.0`:

- MOT17-02-DPM contains **30,003** valid events, represented by **26,960** cues and **3,043** intentional suppressions;
- KITTI Tracking 0000 contains **1,089** valid events, represented by **711** cues and **378** intentional suppressions;
- both cases have zero eligible misses under the frozen policy;
- cue and suppression provenance resolves through the retained evidence chain; and
- repeated packages, audio and reports were identical in the recorded evaluation environment.

These are technical case-study findings. They do **not** establish perceptual effectiveness, usability, accessibility, navigation benefit, safety or cross-platform byte identity.

Canonical results are stored in [`docs/evaluation/evidence/`](docs/evaluation/evidence/). Audited report-ready derivatives are stored in [`docs/evaluation/reporting/`](docs/evaluation/reporting/).

## Reproducibility Controls

The implementation uses:

- versioned schemas, presets, renderer and evaluation contracts;
- deterministic event, cue and run identifiers;
- canonical JSON and stable CSV serialisation;
- logical dataset-relative provenance paths;
- file and configuration SHA-256 hashes;
- explicit cue-or-suppression accounting;
- sample-level rendering logs;
- manual-oracle and injected-fault evaluation tests;
- repeat-run package, audio and report comparisons; and
- deterministic reporting derivatives with source and generated-file hashes.

Detailed evidence is retained under [`docs/evaluation/`](docs/evaluation/) and [`docs/project-management/`](docs/project-management/), with final technical contracts under [`docs/data-model/`](docs/data-model/).

The retained Stage 3 evaluation environment is recorded in
[`configs/evaluation/stage-3-real-data-environment-v0.1.0.json`](configs/evaluation/stage-3-real-data-environment-v0.1.0.json).
It records Windows on AMD64, CPython 3.14.3, jsonschema 4.26.0, pytest 9.1.1 and Ruff 0.16.1.
The byte identity claim is limited to that recorded environment. CI separately exercises the public
test path on Python 3.11.

The compact reporting manifest records the source-report hashes, retained values, claim boundaries,
generator identity and hashes of the readable reporting files. Its README gives the exact rebuild
command used for the retained package.

## Hosted Deployment

The public Render deployment provides read-only inspection of the retained MOT17 and KITTI evaluation sessions. It does not regenerate research outputs.

The bounded deployment package can be rebuilt with:

```bash
python scripts/build_hosted_workbench_bundle.py --acknowledge-media-redistribution
```

The package is verified using its SHA-256 before being served. Dataset redistribution terms must be
reviewed before publishing source media. The retained bundle contains its attribution notice, and a
running workbench exposes that notice at `/dataset-attribution`.

Render configuration is defined in [`render.yaml`](render.yaml). Deployment requires the externally
configured `WORKBENCH_BUNDLE_URL` and `WORKBENCH_BUNDLE_SHA256` values. The process downloads and
verifies the complete bundle, validates both retained sessions, binds to Render's `PORT`, and then
exposes `/api/sessions` as its health endpoint. Startup fails closed if the source, hash, archive or
session evidence is unavailable or inconsistent.

Check availability with:

```bash
curl --fail --show-error https://event-sonification-workbench.onrender.com/api/sessions
```

At the repository cleanup validation on 3 September 2026, a cold request to `/api/sessions`
returned HTTP 200 after 192.3 seconds. This verified the deployed service and both retained session
summaries, but also confirmed that a cold start can exceed three minutes. The local inspection route
remains available when immediate access is required.

## Scope And Limitations

The completed research is deliberately bounded:

- two selected tracking sequences were evaluated;
- the common schema was tested against MOT17 and KITTI Tracking rather than all annotation formats;
- one frozen baseline sonification mapping and renderer were evaluated;
- no participant study was conducted;
- cue density and overlap are technical output properties, not measures of intelligibility;
- bounding-box area is an imperfect apparent-scale input and is not true depth;
- browser acceptance was engineering inspection, not usability testing; and
- byte-identical reproduction has only been established in the recorded execution environment.

Participant evaluation, alternative mappings, density-control strategies, additional annotation formats and cross-platform reproducibility remain future work.

## Key Documentation

For deeper technical detail, begin with:

- [`docs/README.md`](docs/README.md)
- [`docs/data-model/common-event-schema.md`](docs/data-model/common-event-schema.md)
- [`docs/data-model/sonification-and-rendering.md`](docs/data-model/sonification-and-rendering.md)
- [`docs/data-model/workbench-session.md`](docs/data-model/workbench-session.md)
- [`docs/evaluation/technical-evaluation-contract-v0.1.0.md`](docs/evaluation/technical-evaluation-contract-v0.1.0.md)
- [`docs/evaluation/stage-3-cross-dataset-technical-summary.md`](docs/evaluation/stage-3-cross-dataset-technical-summary.md)
- [`docs/project-management/project-plan.md`](docs/project-management/project-plan.md)
- [`docs/project-management/progress-log.md`](docs/project-management/progress-log.md)

## Author

Kori Flowers  
MSc Data Science  
University of the West of England  
Student ID: 24046378
