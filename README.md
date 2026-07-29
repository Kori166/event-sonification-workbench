# Event Sonification Workbench

A reproducible workbench for converting annotated video datasets into deterministic and traceable
audio cues.

## Project Overview

This repository contains the artefact for the MSc project:

**A Reproducible Workbench for Event-Based Sonification of Annotated Video Datasets**

The project will:

1. Convert MOT17 and KITTI Tracking annotations into a common event schema.
2. Map normalised visual events into configurable audio cues.
3. Preserve provenance through records, logs, configuration files and hashes.
4. Evaluate outputs using technical and reproducibility-focused metrics.

The workbench is research infrastructure. It is not presented as a validated accessibility,
navigation or assistive system.

## Project Status

**Stage 0: Project Setup is complete.**

**Stage 1: Data Ingestion and Normalisation is in progress.**

Stage 1 Milestone 1 is complete. It established provisional schema version `0.1.0`, a manually
constructed event and deterministic validation tests.

Stage 1 Milestone 2 is in progress. The MOT17 ground-truth adapter, class mapping, controlled
format fixture, local validation command and automated tests have been implemented. A
MOT17-derived fixture and real-sequence run remain required before the milestone can be marked
complete.

## Project Stages

1. Project setup
2. Data ingestion and normalisation
3. Sonification mapping and cue generation
4. Technical evaluation
5. Artefact assembly, validation and release
6. Reporting and viva preparation

## Repository Structure

```text
event-sonification-workbench/
├── src/
│   └── event_sonification_workbench/
│       └── adapters/                   # Dataset-specific ingestion adapters
├── tests/
│   └── fixtures/                       # Small fixed and documented test inputs
├── configs/
│   ├── class-mappings/                 # Versioned source-to-common class mappings
│   └── schemas/                        # Versioned event schemas
├── docs/
│   ├── data-model/                     # Schema and adapter contracts
│   ├── decisions/                      # Significant project and technical decisions
│   └── project-management/             # Plans, progress, risks and work records
├── data/                               # Local datasets, excluded from Git
├── outputs/                            # Generated events, logs, reports and audio
├── README.md
├── pyproject.toml
├── .env.example
└── .gitignore
```

## Data

MOT17 and KITTI Tracking data are stored locally and are not committed to this repository.
Local dataset paths are configured through environment variables documented in `.env.example`.

Small fixtures may be committed under `tests/fixtures/` where redistribution is permitted. The
current `mot17_format` fixture is synthetic. It tests parser behaviour but does not provide evidence
of compatibility with a real MOT17 release.

## Reproducibility

The project uses versioned configuration files, fixed test samples, deterministic processing,
stable identifiers, provenance records, file hashes, automated tests and repeat-run comparisons.

Current controls include:

- schema version `0.1.0`;
- deterministic event identifiers and canonical event hashing;
- source-file, sequence-metadata and class-mapping hashes;
- explicit frame and coordinate conversion rules;
- structured row-level parser diagnostics; and
- a deterministic fixture-extraction manifest.

## Project Management

Project work is recorded through GitHub Issues and commits, together with the files under
`docs/project-management/`. Significant technical, methodological and scope decisions are
recorded under `docs/decisions/`.

## Installation

```bash
python -m venv .venv
python -m pip install -e ".[dev]"
pytest
```

## MOT17 Local Check

The command below parses and validates one local training sequence without writing output files:

```bash
event-sonification mot17-check \
  --source-root "/path/to/MOT17/train" \
  --sequence-dir "/path/to/MOT17/train/MOT17-02-DPM"
```

The command prints a JSON summary and returns a non-zero status when parsing or event validation
fails. Further details are provided in `docs/data-model/mot17-adapter.md`.

## MOT17 Fixture Extraction

After representative physical rows have been inspected, a documented fixture can be extracted:

```bash
event-sonification mot17-fixture \
  --source-root "/path/to/MOT17/train" \
  --sequence-dir "/path/to/MOT17/train/MOT17-02-DPM" \
  --rows "1,2,250,251" \
  --output-root "tests/fixtures/mot17"
```

The row numbers are examples only. The selected rows and rationale must be based on the inspected
source data.

## Tests

Run the complete suite with:

```bash
python -m pytest
```

The current local suite combines the Milestone 1 schema tests with MOT17 adapter, validation,
command-line and fixture-extraction tests.

## Author

Kori Flowers  
MSc Data Science  
University of the West of England  
Student ID: 24046378
