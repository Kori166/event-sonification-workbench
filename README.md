# Event Sonification Workbench

A reproducible workbench for converting annotated video datasets into deterministic and traceable audio cues.

## Project Overview

This repository contains the artefact for the MSc project:

**A Reproducible Workbench for Event-Based Sonification of Annotated Video Datasets**

The project will develop a pipeline that:

1. Converts annotations from datasets such as MOT17 and KITTI Tracking into a common event schema.
2. Maps normalised visual events into configurable audio cues.
3. Records provenance through event records, cue logs, suppression logs, configuration files and hashes.
4. Evaluates the outputs using technical and reproducibility-focused metrics.

The workbench is being developed as research infrastructure. It is not presented as a validated accessibility, navigation or assistive system.

## Project Status

The repository is currently at **Stage 0: Project Setup**.

Current work includes:

- establishing the repository structure;
- defining the development environment;
- documenting the project scope;
- creating the project plan and task backlog;
- preparing configuration, testing and reproducibility conventions.

No experimental findings or completed implementation are claimed at this stage.

## Planned Project Stages

1. Project setup
2. Data ingestion and normalisation
3. Sonification mapping and cue generation
4. Technical evaluation
5. Artefact assembly, validation and release
6. Reporting and viva preparation

## Planned Repository Structure

```text
event-sonification-workbench/
├── src/                   # Application source code
├── tests/                 # Automated tests and test fixtures
├── configs/               # Schemas and sonification presets
├── docs/                  # Technical and project documentation
├── data/                  # Local dataset directories, excluded from Git
├── outputs/               # Generated events, logs, reports and audio
├── README.md
├── pyproject.toml
├── .env.example
└── .gitignore

Data

MOT17 and KITTI Tracking data will be stored locally and will not be committed to this repository.

Local dataset paths will be configured using environment variables documented in .env.example.

Generated outputs such as audio files, event records and evaluation reports will also be excluded from version control unless they are deliberately retained as small test fixtures or reference outputs.

Reproducibility

The project will support reproducibility through:

versioned configuration files;
deterministic processing;
fixed test samples;
stable event and cue identifiers;
recorded software and dataset versions;
provenance and suppression logs;
file hashes;
automated tests;
repeat-run output comparison.
Project Management

Project work will be managed using GitHub Issues and a GitHub Project board.

Supporting records will be stored under:

docs/project-management/
├── project-plan.md
├── progress-log.md
├── risk-register.md
└── supervision-log.md

Issues, commits and tests will be linked where possible to provide a traceable record of planning, implementation and evaluation.

Installation

Installation instructions will be added once the initial Python package and dependencies have been established.

Usage

Command-line usage examples will be added when the first end-to-end pipeline is implemented.

Author

Kori Flowers
MSc Data Science
University of the West of England
Student ID: 24046378