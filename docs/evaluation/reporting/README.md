# Reporting Evidence

## Purpose

This folder contains concise, readable summaries and tables derived from the Stage 3 technical evaluation evidence. The evidence in [`../evidence/`](../evidence/) remains authoritative. These files neither rerun the evaluation nor redefine its measures.

## Contents

- [`results-summary.md`](results-summary.md) explains the method, main findings, interpretation and limitations.
- [`reporting-audit.md`](reporting-audit.md) records the checks applied when values were transferred into the reporting files.
- [`reporting-manifest.json`](reporting-manifest.json) records source identities, exact retained results, claim boundaries and generated-file hashes.
- [`tables/`](tables/) contains the three result tables.

## Reproducing The Reporting Files

From the repository root, run:

```bash
event-sonification generate-stage3-report-evidence --output docs/evaluation/reporting --generator-commit ad4e3f82a7d9e625c87f419a5f84d2fd6bb1cc77 --replace-generated
```

The command verifies the report hashes and identities before writing anything. Given the same evidence and generator identity, repeated runs produce the same bytes.

## Evidence Boundary

The retained evaluation covers two selected cases: MOT17-02-DPM and KITTI Tracking 0000. Both use one fixed baseline mapping and one renderer. Repeatability claims apply only to the recorded Stage 3 environment.

No participant, perceptual, usability, accessibility, navigation or safety evaluation was performed. Density and overlap are technical measures of generated audio load; they are not evidence of listener difficulty or effectiveness. Cross-platform byte identity was not tested.
