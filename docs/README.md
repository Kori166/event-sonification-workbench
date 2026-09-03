# Documentation Guide

This page is a navigation route for inspecting the current MSc research artefact. The root
[`README.md`](../README.md) provides the project summary, claim boundary, installation instructions
and direct implementation map.

## Technical Architecture And Data Model

1. [`data-model/common-event-schema.md`](data-model/common-event-schema.md) defines the common event
   structure, validation boundary and MOT17 and KITTI adapter semantics.
2. [`data-model/sonification-and-rendering.md`](data-model/sonification-and-rendering.md) defines the
   frozen baseline mapping, cue and suppression behaviour, and deterministic audio rendering.
3. [`data-model/workbench-session.md`](data-model/workbench-session.md) defines retained session
   identity, runtime binding, validation and read only inspection behaviour.

## Technical Evaluation Evidence

1. [`evaluation/technical-evaluation-contract-v0.1.0.md`](evaluation/technical-evaluation-contract-v0.1.0.md)
   explains the frozen metrics and interpretation boundary.
2. [`evaluation/stage-3-real-data-evaluation-protocol.md`](evaluation/stage-3-real-data-evaluation-protocol.md)
   records the accepted real data evaluation procedure.
3. [`evaluation/stage-3-cross-dataset-technical-summary.md`](evaluation/stage-3-cross-dataset-technical-summary.md)
   summarises the retained MOT17 and KITTI results.
4. [`evaluation/stage-3-real-data-traceability-audit.md`](evaluation/stage-3-real-data-traceability-audit.md)
   documents the end to end traceability audit.
5. [`evaluation/evidence/`](evaluation/evidence/) contains canonical retained reports and manifests.
6. [`evaluation/reporting/README.md`](evaluation/reporting/README.md) explains the audited reporting
   derivatives, tables and figures.

These records contain technical case study evidence only. They do not establish accessibility,
usability, navigation, listener comprehension or safety outcomes.

## Project Management Evidence

[`project-management/README.md`](project-management/README.md) identifies the retained project plan,
progress logs, stage checklists, risk register and supervision record.

## Decision Records

[`decisions/README.md`](decisions/README.md) indexes the architecture, methodology, evidence and
deployment decisions. Later records may supersede earlier decisions without erasing the earlier
rationale.

## Historical Development Evidence

Project management records and decision records preserve the project state, uncertainties and
decisions at the time they were written. Their historical status language is intentional and should
not be read as the current release status. Current status is stated in the root
[`README.md`](../README.md).

The final repository does not retain a separate dissertation source tree or milestone development
directory. Final technical contracts were consolidated under `data-model/`, while chronological
development evidence remains in the project management and decision records above.

## Dataset Attribution

Dataset ownership, citations, identified terms and deployment scope are recorded in the retained
hosted bundle attribution notice, which a running workbench exposes at `/dataset-attribution`.
Dataset terms are separate from licensing of project authored source code.
