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