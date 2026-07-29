# Event Sonification Workbench

A reproducible workbench for converting annotated video datasets into deterministic and traceable audio cues.

## Project Overview

This repository contains the artefact for the MSc project:

**A Reproducible Workbench for Event-Based Sonification of Annotated Video Datasets**

The project will:

1. Convert MOT17 and KITTI Tracking annotations into a common event schema.
2. Map normalised visual events into configurable audio cues.
3. Preserve provenance through records, logs, configuration files and hashes.
4. Evaluate outputs using technical and reproducibility-focused metrics.

The workbench is research infrastructure. It is not presented as a validated accessibility, navigation or assistive system.

## Project Status

**Stage 0: Project Setup is complete.**

**Stage 1: Data Ingestion and Normalisation is in progress.**

Stage 1 Milestone 1 is complete. It added a provisional common event schema, one synthetic source annotation, one manually constructed expected event and automated validation tests. Schema version `0.1.0` will remain provisional until it has been reviewed against real MOT17 and KITTI Tracking rows.

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
│   └── event_sonification_workbench/  # Installable application package
├── tests/
│   └── fixtures/                      # Small fixed and documented test inputs
├── configs/
│   └── schemas/                       # Versioned event schemas
├── docs/
│   ├── data-model/                    # Schema and technical data contracts
│   ├── decisions/                     # Significant project and technical decisions
│   └── project-management/            # Plans, progress, risks and supervision records
├── data/                              # Local datasets, excluded from Git
├── outputs/                           # Generated events, logs, reports and audio
├── README.md
├── pyproject.toml
├── .env.example
└── .gitignore
```

## Data

MOT17 and KITTI Tracking data are stored locally and are not committed to this repository.

Local dataset paths are configured using environment variables documented in `.env.example`. Small fixed fixtures may be committed under `tests/fixtures/` for deterministic automated testing where redistribution is permitted.

The current Milestone 1 fixture is synthetic and contains no copied dataset content. A separate fixed MOT17 fixture remains outstanding.

## Reproducibility

The project uses versioned configuration files, fixed test samples, deterministic processing, stable identifiers, provenance logs, file hashes, automated tests and repeat-run comparisons.

Milestone 1 establishes:

- schema version `0.1.0`;
- deterministic event identifiers;
- canonical event hashing;
- source-file hashing;
- independent checks of time and geometry calculations; and
- an explicit record of schema decisions and unresolved questions.

## Project Management

Project work is recorded through GitHub Issues and commits, together with the files under `docs/project-management/`. Significant technical, methodological and scope decisions are recorded under `docs/decisions/`.

## Installation

```bash
python -m venv .venv
python -m pip install -e ".[dev]"
pytest
```

## Milestone 1 Validation

Run the schema and synthetic-fixture tests with:

```bash
python -m pytest tests/test_event_schema.py tests/test_synthetic_event.py
```

The fixture and its manual derivation are documented in `tests/fixtures/synthetic/README.md`. The schema contract is documented in `docs/data-model/common-event-schema.md`.

## Usage

The current command-line placeholder can be run with:

```bash
event-sonification
```

Dataset-processing commands will be added during the remaining Stage 1 milestones.

## Author

Kori Flowers  
MSc Data Science  
University of the West of England  
Student ID: 24046378
