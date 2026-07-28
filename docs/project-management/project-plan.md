# Project Plan

## Project

**A Reproducible Workbench for Event-Based Sonification of Annotated Video Datasets**

## Aim

Design, implement and evaluate a reproducible workbench that converts annotated video data into normalised events, deterministic audio cues and traceable technical outputs.

## Project Stages

| Stage | Main work | Evidence of completion | Status |
|---|---|---|---|
| 0. Project setup | Repository structure, environment, documentation and project tracking | Working package scaffold, CI test, README and project records | Complete, 28 July 2026 |
| 1. Data ingestion and normalisation | Parse MOT17 and KITTI Tracking annotations into a common event schema | Parsers, schema, validation outputs, provenance records and tests | In progress, started 28 July 2026 |
| 2. Sonification | Map normalised events into scheduled audio cues | Mapping presets, cue schedules, audio files and logs | Planned |
| 3. Technical evaluation | Measure coverage, alignment, traceability, cue density, overlap and reproducibility | Evaluation reports, comparison results and repeat-run checks | Planned |
| 4. Artefact assembly and release | Validate, document and package the complete workbench | Reproducible release, final documentation and tagged version | Planned |
| 5. Reporting and viva preparation | Complete the dissertation and prepare the artefact demonstration | Final report, demonstration plan and viva notes | Planned |

## Working Method

The project will be developed iteratively. Work will be recorded through GitHub Issues and commits, automated tests, configuration and provenance files, the progress log, the risk register, supervision records and decision records.

## Stage 1 Work Order

1. Define the common event schema.
2. Create small fixed annotation fixtures.
3. Implement and test the MOT17 parser.
4. Implement and test the KITTI Tracking parser.
5. Validate normalised event records.
6. Write structured event and provenance outputs.

## Stage 1 Issues

- Issue #1: Define the common event schema.
- Issue #2: Implement the MOT17 annotation parser.
- Issue #3: Create a fixed MOT17 test fixture.
- Issue #4: Validate normalised event records.
- Issue #5: Implement the KITTI Tracking annotation parser.
- Issue #6: Write normalised event and provenance outputs.

## Stage 1 Completion Criteria

Stage 1 will be complete when:

- both selected dataset formats can be converted into the shared schema;
- fixed fixtures and automated parser tests pass in CI;
- invalid records are reported through structured validation results;
- output records preserve source dataset, sequence, file and conversion information; and
- the implementation and assumptions are documented.

## Key Milestones

| Milestone | Target evidence |
|---|---|
| Repository established | Project structure and setup documentation |
| MOT17 pipeline working | Validated MOT17 events produced from a fixed sample |
| KITTI pipeline working | Validated KITTI Tracking events produced from a fixed sample |
| Sonification working | Deterministic cues, WAV output and traceability logs |
| Evaluation complete | Technical metrics and preset comparisons |
| Artefact frozen | Tagged, documented and reproducible release |
| Submission ready | Final report and tested viva demonstration |

## Scope Control

Core deliverables are limited to MOT17, KITTI Tracking, a common event schema, deterministic sonification, provenance records and technical evaluation.

Participant studies, accessibility claims, interactive interfaces and additional datasets are outside the core MSc scope and will be treated as future work.
