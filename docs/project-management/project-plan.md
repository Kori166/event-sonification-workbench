# Project Plan

## Project Aim

Design, implement and evaluate a reproducible workbench that converts annotated video data into a
common event schema, deterministic audio cues and traceable technical outputs.

## Research Questions

**RQ1:** How can public annotated video datasets be transformed into a common event schema suitable
for event-based sonification?

**RQ2:** How can normalised visual events be mapped into deterministic and traceable audio cues?

**RQ3:** How can event-based sonification outputs be evaluated using technical metrics for coverage,
alignment, traceability and reproducibility?

## Project Stages

| Stage | Purpose | Principal outputs and evidence | Final status |
|---|---|---|---|
| 0. Project Setup | Establish the repository, environment and project controls | Package scaffold, automated smoke test, repository guidance, project plan, progress log, risk register and decision records | Complete, 28 July 2026 |
| 1. Data Ingestion and Normalisation | Transform MOT17 and KITTI Tracking annotations into the common event schema | Dataset-specific adapters, schema, fixtures, validation, deterministic event packages, provenance and [Stage 1 checklist](stage-1-checklist.md) | Complete, 5 August 2026 |
| 2. Sonification | Map validated events into cues and render deterministic audio | Baseline preset, cue and suppression records, PCM WAV renderer, traceability logs, repeated real-data chains and [Stage 2 checklist](stage-2-checklist.md) | Complete, 6 August 2026 |
| 3. Technical Evaluation | Evaluate retained outputs using the technical contract | Synthetic oracle, two real-data reports, repeat comparisons, concise audited reporting tables, compact claim boundaries and [Stage 3 checklist](stage-3-checklist.md) | Complete, 6 August 2026 |
| 4. Artefact Assembly, Validation and Release | Assemble and validate the read-only inspection workbench without changing the research pipeline | Retained session contract, two-session catalogue, inspection service, browser interface, technical browser acceptance, release checks and [Stage 4 checklist](stage-4-checklist.md) | Complete, 18 August 2026 |
| 5. Reporting and Viva Preparation | Prepare the dissertation, artefact submission material and focused viva explanation | Final report candidate, artefact documentation, evidence reconciliation and viva preparation | Report and artefact prepared for submission; viva preparation ongoing |

Completion dates above are supported by the [canonical progress log](progress-log.md) and stage
checklists. They record completion of the defined stage gates rather than a claim that later
maintenance or presentation refinement could not occur.

## Principal Milestones

| Milestone | Evidence and outcome | Status |
|---|---|---|
| Research foundation established | The 7 April supervision record established report structure, literature, objectives, methodology and evaluation as explicit workstreams | Complete, 7 April 2026 |
| Research scope refined | The 29 May supervision record reduced the work to three research questions, clarified MOT17 and KITTI Tracking, and made common event normalisation central to RQ1 | Complete, 29 May 2026 |
| Common event pipeline completed | Both dataset-specific adapters, common validation and deterministic event packages passed the Stage 1 gate | Complete, 5 August 2026 |
| Deterministic sonification completed | The baseline generated traceable cue, suppression and PCM WAV packages with same-environment repeatability | Complete, 6 August 2026 |
| Technical evaluation completed | The contract, synthetic oracle, audited reporting evidence and bounded RQ3 findings passed the Stage 3 gate | Complete, 6 August 2026 |
| Two retained dataset cases evaluated | MOT17-02-DPM and KITTI Tracking sequence 0000 were evaluated as bounded case studies | Complete, 6 August 2026 |
| Inspection workbench completed | Both retained sessions passed headless, integration and researcher-controlled technical browser checks | Complete, 18 August 2026 |
| Submission and viva preparation | The report and artefact were prepared for submission; final submission remains researcher controlled and viva preparation continues | In progress |

## Working Method

Development used bounded iterative stages supported by:

- GitHub Issues and pull requests for scoped implementation and review;
- automated tests, including configured real-data integration tests;
- versioned technical contracts and configuration;
- the [canonical progress log](progress-log.md) and stage checklists;
- the [risk register](risk-register.md);
- verified [supervision feedback](supervision-log.md); and
- significant methodological and technical [decision records](../decisions/).

Issues, pull requests and commits retain lower-level engineering history. This plan records the final
stage structure, principal milestones, scope and status rather than repeating those acceptance
criteria.

## Scope Control

The completed project is bounded to:

- MOT17 and KITTI Tracking, with one retained sequence from each used for technical evaluation;
- one common event schema and dataset-specific adapters;
- one baseline mapping, cue and suppression policy;
- one deterministic PCM WAV renderer;
- technical evaluation of coverage, alignment, traceability, density, overlap and repeatability;
- same-environment repeatability rather than cross-platform byte identity; and
- a read-only workbench for inspecting retained evidence.

The project does not include a participant study and does not establish accessibility, usability,
navigation, perceptual effectiveness or safety. It does not claim compatibility with every annotated
video dataset or validate the workbench as assistive technology.

## Final Status

The research implementation, technical evaluation and read-only workbench are complete. The final
report and artefact are prepared for submission. Repository records retain the technical
evidence, explicit scope limits and the project history.

Final submission is not recorded as complete because no repository evidence confirms that it has
occurred. Viva preparation remains ongoing.
