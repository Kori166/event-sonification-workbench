# Event Sonification Workbench

A reproducible research workbench for converting annotated video tracking data into normalised events, deterministic audio cues and traceable technical outputs.

This repository contains the MSc Data Science project:

**A Reproducible Workbench for Event Based Sonification of Annotated Video Datasets**

The workbench is **research infrastructure**. It is not a validated accessibility, navigation, usability or assistive system.

## First Steps & Installation

### 1. Open The Hosted Workbench

[**Open Live Workbench**](https://event-sonification-workbench.onrender.com/)

The hosted workbench provides read only inspection of the two evaluated cases:

- **MOT17-02-DPM**
- **KITTI Tracking sequence 0000**

The deployment is hosted on Render's free service, so a cold start can take several minutes.

### 2. Follow The Evidence Route

| What To Inspect | Location |
|---|---|
| Documentation index | [`docs/README.md`](docs/README.md) |
| Technical results summary | [`docs/evaluation/stage-3-dataset-results-summary.md`](docs/evaluation/stage-3-dataset-results-summary.md) |
| Evaluation evidence | [`docs/evaluation/evidence/`](docs/evaluation/evidence/) |
| Common event schema | [`docs/data-model/common-event-schema.md`](docs/data-model/common-event-schema.md) |
| Sonification and rendering contract | [`docs/data-model/sonification-and-rendering.md`](docs/data-model/sonification-and-rendering.md) |
| Workbench session contract | [`docs/data-model/workbench-session.md`](docs/data-model/workbench-session.md) |
| Technical Evaluation Contract | [`docs/evaluation/technical-evaluation-contract-v0.1.0.md`](docs/evaluation/technical-evaluation-contract-v0.1.0.md) |
| Project management evidence | [`docs/project-management/README.md`](docs/project-management/README.md) |
| Design and research decisions | [`docs/decisions/README.md`](docs/decisions/README.md) |
| Source code | [`src/event_sonification_workbench/`](src/event_sonification_workbench/) |
| Automated tests | [`tests/`](tests/) |
| Dataset attribution | [`dataset_attribution.md`](dataset_attribution.md) |

For a short inspection, the recommended route is:

1. Open the hosted workbench.
2. Inspect both retained dataset sessions.
3. Review the technical results summary.
4. Review the common event and sonification contracts.
5. Use the documentation index for evaluation, project management and decision evidence.

---

## Project Overview

Annotated tracking datasets describe objects frame by frame, but datasets use different formats, labels and metadata. This makes direct reuse in one sonification workflow difficult.

The project addresses three research questions:

1. **Normalisation:** How can public annotated video datasets be transformed into a common event schema suitable for event based sonification?
2. **Mapping:** How can normalised visual events be mapped into deterministic and traceable audio cues?
3. **Evaluation:** How can event based sonification outputs be evaluated using technical metrics for coverage, alignment, traceability and reproducibility?

The implemented workflow is:

```text
MOT17 / KITTI annotations
        ↓
dataset specific adapters
        ↓
common event schema 0.2.0
        ↓
validated event packages
        ↓
versioned sonification mapping
        ↓
audio cues or explicit suppressions
        ↓
deterministic stereo PCM audio
        ↓
technical evaluation
        ↓
read only inspection workbench
```

An **event** is one valid object observation in one video frame.

A **cue** is the scheduled audio representation of an eligible event.

A **suppression** records why a valid event was deliberately not sonified.

Every valid event therefore has an explicit processing outcome rather than silently disappearing from the pipeline.

---

## Evaluated Cases

The final technical evaluation used:

- **MOT17-02-DPM**
- **KITTI Tracking sequence 0000**

Each dataset has its own adapter because the native annotation formats and meanings differ. Both adapters produce the same common event schema, allowing the later mapping, rendering and evaluation stages to remain shared.

The evaluated baseline uses:

| Component | Version |
|---|---|
| Common event schema | `0.2.0` |
| Baseline sonification mapping | `0.1.0` |
| Audio renderer | `0.1.0` |
| Technical Evaluation Contract | `0.1.0` |
| Workbench Session Contract | `0.1.0` |

---

## Key Technical Results

| Metric | MOT17-02-DPM | KITTI Tracking 0000 |
|---|---:|---:|
| Valid events | 30,003 | 1,089 |
| Generated cues | 26,960 | 711 |
| Intentional suppressions | 3,043 | 378 |
| Missed eligible events | 0 | 0 |
| Event accounting | 100% | 100% |
| Eligible event coverage | 100% | 100% |
| Cue traceability | 100% | 100% |
| Suppression traceability | 100% | 100% |
| Cue density | 1,342.18 cues/s | 46.11 cues/s |
| Normalised overlap burden | 160.06 | 4.53 |

Cue placement matched the intended audio sample positions exactly in both retained cases.

Repeated event packages, cue packages and WAV files were byte identical within the recorded evaluation environment. Repeated evaluator and reporting runs also reproduced identical outputs.

These are **technical findings only**. They do not establish whether the generated sounds are understandable, useful or comfortable for listeners.

Full results are available in:

- [`docs/evaluation/stage-3-dataset-results-summary.md`](docs/evaluation/stage-3-dataset-results-summary.md)
- [`docs/evaluation/evidence/`](docs/evaluation/evidence/)
- [`docs/evaluation/reporting/`](docs/evaluation/reporting/)

---

## What The Workbench Shows

The browser workbench provides read-only inspection of retained research outputs.

It includes:

- source frames with recorded bounding boxes
- retained generated audio
- synchronised EVENT, CUE and SUPPRESS timeline lanes
- frame level cue selection
- cue and suppression provenance
- source event information
- rendered audio sample ranges
- technical evaluation metrics
- retained session and configuration information

Selecting a cue or suppression moves the inspection view to its recorded time. A cue can be traced through its source event, mapping and rendered sample range. A suppression can be traced to its source event and recorded reason.

The interface does **not** regenerate or modify research results. Processing and evaluation occur separately, and the workbench displays the retained outputs.

---

## Repository Structure

```text
event-sonification-workbench/
├── configs/                         # schemas and versioned configurations
├── docs/
│   ├── data-model/                  # technical contracts
│   ├── decisions/                   # design and research decisions
│   ├── evaluation/                  # evaluation evidence and reporting
│   └── project-management/          # plan, progress, risks and stage records
├── scripts/                         # supporting build and deployment scripts
├── src/event_sonification_workbench/
│   ├── adapters/                    # MOT17 and KITTI adapters
│   ├── sonification/                # cue generation and rendering
│   └── workbench/                   # inspection service and browser interface
├── tests/                           # automated tests and fixtures
├── .env.example
├── CITATION.cff
├── dataset_attribution.md
├── pyproject.toml
├── render.yaml
└── README.md
```

### Evidence Kept In Git

The repository contains:

- source code
- schemas and versioned configurations
- synthetic and public test fixtures
- automated tests
- technical contracts
- evaluation reports
- audited reporting outputs
- decision records
- project plans and progress records
- risk and supervision records
- stage acceptance checklists
- path independent workbench session declarations

Large or externally obtained research material remains outside Git, including:

- complete MOT17 and KITTI datasets
- full source image sequences
- complete generated Stage 1 and Stage 2 packages
- retained full WAV files
- private machine paths and local environment settings

This keeps the repository portable while avoiding unnecessary redistribution of external datasets and large generated files.

---

## Local Installation

The hosted workbench is the simplest route for inspection.

A complete local workbench additionally requires locally obtained MOT17 and KITTI data and the retained Stage 2 evidence tree.

### Requirements

- Python 3.11 or later
- Git
- a modern web browser

Clone the repository:

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

Install the project:

```bash
python -m pip install -e ".[dev]"
```

---

## Run The Tests

The public test route does not require the full private dataset copies:

```bash
python -m ruff check .
python -m pytest -m "not integration"
```

To run the complete available suite:

```bash
python -m pytest
```

Integration tests require the external dataset and evidence locations described below. They skip when those resources are not available.

A skipped integration test should not be interpreted as a successful private data integration test.

---

## Full Local Workbench

Copy `.env.example` to `.env`.

**Windows PowerShell**

```powershell
Copy-Item .env.example .env
```

**macOS / Linux**

```bash
cp .env.example .env
```

Configure the three external roots:

```text
MOT17_ROOT=
KITTI_TRACKING_ROOT=
STAGE2_EVIDENCE_ROOT=
```

Where:

- `MOT17_ROOT` points to the locally obtained MOT17 dataset
- `KITTI_TRACKING_ROOT` points to the locally obtained KITTI Tracking dataset
- `STAGE2_EVIDENCE_ROOT` points to the retained event, cue and audio evidence used by the accepted sessions

The `.env` file is ignored by Git and should not be committed.

Launch the inspection workbench:

```bash
python -m event_sonification_workbench.cli inspect-session
```

Then open:

```text
http://127.0.0.1:8765/
```

The retained evidence chain is validated before the interface is served. Missing or inconsistent bindings cause the launch to fail rather than displaying an unverified session.

---

## Reproducing The Processing Pipeline

### 1. Create Validated Event Packages

MOT17:

```bash
python -m event_sonification_workbench.cli mot17-package --sequence MOT17-02-DPM --output-directory outputs
```

KITTI Tracking:

```bash
python -m event_sonification_workbench.cli kitti-package --sequence 0000 --output-directory outputs
```

Schema and adapter details:

[`docs/data-model/common-event-schema.md`](docs/data-model/common-event-schema.md)

### 2. Generate Cues And Suppressions

```bash
python -m event_sonification_workbench.cli schedule-cues --event-package outputs/<stage-1-run-id> --preset configs/sonification/presets/baseline-v0.1.0.json --output-directory outputs
```

Each accepted valid event produces either one cue or one explicit suppression.

### 3. Render Audio

```bash
python -m event_sonification_workbench.cli render-audio --cue-package outputs/<cue-run-id> --renderer-config configs/sonification/renderers/baseline-v0.1.0.json --output-directory outputs
```

The baseline renderer produces deterministic 44.1 kHz stereo 16-bit PCM audio under the recorded configuration.

Mapping and rendering details:

[`docs/data-model/sonification-and-rendering.md`](docs/data-model/sonification-and-rendering.md)

### 4. Check The Technical Evaluator

A committed synthetic test case can be evaluated without the real datasets:

```bash
python -m event_sonification_workbench.cli evaluate-technical --input tests/fixtures/evaluation_oracle/input.json --output outputs/technical_evaluation_report.json
```

Metric definitions are fixed in:

[`docs/evaluation/technical-evaluation-contract-v0.1.0.md`](docs/evaluation/technical-evaluation-contract-v0.1.0.md)

The retained real-data evaluation uses the verified event, cue, suppression and renderer evidence produced for the two evaluated cases.

---

## Reproducibility And Traceability

The project uses:

- versioned schemas, mapping, renderer and evaluation rules
- deterministic identifiers
- stable output ordering and serialisation
- SHA-256 file and configuration hashes
- source annotation provenance
- explicit cue or suppression accounting
- sample level renderer logs
- a manually checked evaluation case
- deliberate fault injection tests
- repeat run package, audio and report comparisons
- retained evaluation evidence

The recorded Stage 3 environment is stored in:

[`configs/evaluation/stage-3-real-data-environment-v0.1.0.json`](configs/evaluation/stage-3-real-data-environment-v0.1.0.json)

The byte identity result is limited to the recorded execution environment. Cross-platform byte identical reproduction was not tested.

---

## Project Management Evidence

Planning and development evidence is retained separately from the final technical contracts.

The index is:

[`docs/project-management/README.md`](docs/project-management/README.md)

It links to:

- project plan and milestones
- progress log
- supervision log
- risk register
- Stage 1 to Stage 4 acceptance checklists
- detailed Stage 4 integration evidence

GitHub issues, pull requests and commits provide lower level implementation history.

Significant technical, methodological and scope decisions are indexed in:

[`docs/decisions/README.md`](docs/decisions/README.md)

---

## Scope And Limitations

The project deliberately has a bounded technical scope:

- only MOT17-02-DPM and KITTI Tracking 0000 were evaluated
- compatibility with every annotated video format is not claimed
- one baseline mapping and renderer were evaluated
- no participant study was conducted
- cue density and overlap measure technical audio load, not listener difficulty
- bounding box area represents apparent image size, not true object distance
- browser checks assessed intended engineering behaviour, not usability
- the workbench is a read only inspection layer rather than a live processing interface
- cross-platform byte identical reproducibility was not tested

Participant evaluation, alternative sonification mappings, density control methods, additional annotation formats, live annotation inputs and cross-platform testing remain possible future work.

---

## Attribution And Provenance

Dataset attribution and deployment boundaries are recorded in:

[`dataset_attribution.md`](dataset_attribution.md)

Project citation metadata is provided in:

[`CITATION.cff`](CITATION.cff)

Source files include technical reference and provenance information where external libraries, APIs or technical documentation materially informed the implementation.

---

## Author

**Kori Flowers**  
MSc Data Science  
University of the West of England  
Student ID: 24046378