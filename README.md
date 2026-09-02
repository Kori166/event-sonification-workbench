# Event Sonification Workbench

A reproducible workbench for converting annotated video tracking data into normalised events, deterministic audio cues, traceable PCM audio and technically evaluated outputs.

This repository contains the MSc Data Science project:

**A Reproducible Workbench for Event-Based Sonification of Annotated Video Datasets**

The workbench is research infrastructure. It is **not** a validated accessibility, navigation, usability or assistive system.

## Try the Workbench

### Hosted Workbench

[**Open Live Workbench →**](https://event-sonification-workbench.onrender.com/)

The hosted read-only workbench provides one-click inspection of the two retained technical evaluation cases:

- **MOT17-02-DPM**
- **KITTI Tracking sequence 0000**

The deployment uses the verified retained evidence and bounded deployment package produced for the project. It provides convenient inspection of the research artefact and does not constitute additional usability, accessibility or perceptual evaluation.

### Hosted Deployment

The public Render deployment provides read-only inspection of the retained MOT17 and KITTI evaluation sessions. It does not regenerate research outputs.

The bounded deployment package can be rebuilt with:

```bash
python scripts/build_hosted_workbench_bundle.py --acknowledge-media-redistribution
```

The package is verified using its SHA-256 before being served. Dataset redistribution terms must be reviewed before publishing source media.

Render configuration is defined in `render.yaml`.

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

The pipeline preserves source identity and provenance so that generated cues and suppressions can be traced back to the source annotation, configuration and rendered sample range.

The bounded dataset cases used in the completed technical evaluation are:

- **MOT17-02-DPM**
- **KITTI Tracking sequence 0000**

## Quick Access

| Looking for | Location |
|---|---|
| Workbench source code | [`src/event_sonification_workbench/`](src/event_sonification_workbench/) |
| Dissertation working manuscript | [`docs/dissertation/working-manuscript.md`](docs/dissertation/working-manuscript.md) |
| Dissertation chapters | [`docs/dissertation/chapters/`](docs/dissertation/chapters/) |
| Canonical technical evaluation evidence | [`docs/evaluation/evidence/`](docs/evaluation/evidence/) |
| Report-ready tables and figures | [`docs/evaluation/reporting/`](docs/evaluation/reporting/) |
| Technical evaluation contract | [`docs/evaluation/technical-evaluation-contract-v0.1.0.md`](docs/evaluation/technical-evaluation-contract-v0.1.0.md) |
| Common event schema documentation | [`docs/data-model/common-event-schema.md`](docs/data-model/common-event-schema.md) |
| Design decisions | [`docs/decisions/`](docs/decisions/) |
| Project plan | [`docs/project-management/project-plan.md`](docs/project-management/project-plan.md) |
| Progress log | [`docs/project-management/progress-log.md`](docs/project-management/progress-log.md) |
| Risk register | [`docs/project-management/risk-register.md`](docs/project-management/risk-register.md) |
| Stage checklists | [`docs/project-management/`](docs/project-management/) |
| Automated tests and fixtures | [`tests/`](tests/) |

## Project Status

| Stage | Status |
|---|---|
| 0. Project setup | Complete |
| 1. Data ingestion and normalisation | Complete |
| 2. Sonification | Complete |
| 3. Technical evaluation | Complete |
| 4. Artefact assembly and release | Complete |
| 5. Reporting and viva preparation | In progress |

Stage 5 Phases A-D are complete. Remaining work is limited to researcher-controlled review, viva preparation, final submission packaging and submission. Full stage history is recorded in [`docs/project-management/project-plan.md`](docs/project-management/project-plan.md).

## Repository Structure

```text
event-sonification-workbench/
├── configs/                         # schemas, mappings and renderer configuration
├── docs/
│   ├── data-model/                  # technical contracts and formats
│   ├── decisions/                   # architecture and research decisions
│   ├── development/                 # milestone and close-out evidence
│   ├── dissertation/                # working manuscript, chapters and audits
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
- audited report-ready tables and figures;
- dissertation source material and audit records;
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
- rendered sample-range information; and
- technical metrics projected directly from the verified Stage 3 report.

Selecting a cue or suppression pauses playback and seeks to the retained outcome time. Cue inspection includes its rendered sample range; suppression inspection shows the retained reason and has no Render stage.

## Reproducing The Processing Pipeline

The commands below are the main processing path. Detailed contracts and field definitions are linked from the relevant documentation rather than duplicated here.

### 1. Create Validated Event Packages

```bash
python -m event_sonification_workbench.cli mot17-package \
  --sequence MOT17-02-DPM \
  --output-directory outputs

python -m event_sonification_workbench.cli kitti-package \
  --sequence 0000 \
  --output-directory outputs
```

See [`docs/data-model/output-package.md`](docs/data-model/output-package.md).

### 2. Schedule Cues And Suppressions

```bash
python -m event_sonification_workbench.cli schedule-cues \
  --event-package outputs/<stage-1-run-id> \
  --preset configs/sonification/presets/baseline-v0.1.0.json \
  --output-directory outputs
```

Each accepted valid event produces either one cue or one explicit suppression record.

See [`docs/data-model/sonification-preset.md`](docs/data-model/sonification-preset.md) and [`docs/data-model/cue-schedule.md`](docs/data-model/cue-schedule.md).

### 3. Render Deterministic Audio

```bash
python -m event_sonification_workbench.cli render-audio \
  --cue-package outputs/<cue-run-id> \
  --renderer-config configs/sonification/renderers/baseline-v0.1.0.json \
  --output-directory outputs
```

The baseline renderer produces stereo 44.1 kHz signed 16-bit PCM audio with deterministic sample placement under the recorded configuration.

See [`docs/data-model/audio-rendering.md`](docs/data-model/audio-rendering.md).

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
- audited links between canonical results and dissertation tables/figures.

Detailed evidence is recorded under [`docs/development/`](docs/development/) and [`docs/evaluation/`](docs/evaluation/).

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

- [`docs/data-model/common-event-schema.md`](docs/data-model/common-event-schema.md)
- [`docs/data-model/mot17-adapter.md`](docs/data-model/mot17-adapter.md)
- [`docs/data-model/kitti-tracking-adapter.md`](docs/data-model/kitti-tracking-adapter.md)
- [`docs/data-model/sonification-preset.md`](docs/data-model/sonification-preset.md)
- [`docs/data-model/audio-rendering.md`](docs/data-model/audio-rendering.md)
- [`docs/evaluation/technical-evaluation-contract-v0.1.0.md`](docs/evaluation/technical-evaluation-contract-v0.1.0.md)
- [`docs/development/stage-1-closeout.md`](docs/development/stage-1-closeout.md)
- [`docs/development/stage-2-closeout.md`](docs/development/stage-2-closeout.md)
- [`docs/development/stage-3-closeout.md`](docs/development/stage-3-closeout.md)
- [`docs/project-management/project-plan.md`](docs/project-management/project-plan.md)

## Author

Kori Flowers  
MSc Data Science  
University of the West of England  
Student ID: 24046378