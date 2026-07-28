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

**Stage 1: Data Ingestion and Normalisation is in progress.** Current work begins with the common event schema, fixed test data, dataset parsers and event validation.

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
├── src/                   # Application source code
├── tests/                 # Automated tests and fixed fixtures
├── configs/               # Schemas and sonification presets
├── docs/
│   ├── decisions/         # Significant project and technical decisions
│   └── project-management/# Plans, progress, risks and supervision records
├── data/                  # Local datasets, excluded from Git
├── outputs/               # Generated events, logs, reports and audio
├── README.md
├── pyproject.toml
├── .env.example
└── .gitignore
```

## Data

MOT17 and KITTI Tracking data are stored locally and are not committed to this repository.

Local dataset paths are configured using environment variables documented in `.env.example`. Small fixed fixtures may be committed under `tests/fixtures/` for deterministic automated testing where redistribution is permitted.

## Reproducibility

The project uses versioned configuration files, fixed test samples, deterministic processing, stable identifiers, provenance logs, file hashes, automated tests and repeat-run comparisons.

## Project Management

Project work is recorded through GitHub Issues and commits, together with the files under `docs/project-management/`. Significant technical, methodological and scope decisions are recorded under `docs/decisions/`.

## Installation

```bash
python -m venv .venv
python -m pip install -e ".[dev]"
pytest
```

## Usage

The current command-line placeholder can be run with:

```bash
event-sonification
```

Dataset-processing commands will be added during Stage 1.

## Author

Kori Flowers  
MSc Data Science  
University of the West of England  
Student ID: 24046378
