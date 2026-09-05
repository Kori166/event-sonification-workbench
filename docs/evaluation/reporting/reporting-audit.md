# Reporting Audit

## Purpose

A separate read-only reporting check was used to confirm that values transferred from the retained Stage 3 evidence into these reporting outputs remained consistent. It checked correspondence and provenance and it did not repeat the technical evaluation.

## Checks

| Check | Result |
|---|---:|
| Source reports checked | 2 |
| Headline source values checked | 20 |
| Calculations checked independently from their operands | 8 |
| Values displayed across the three tables checked | 64 |
| Written claim boundaries checked | 12 |
| Retained generated-file hashes checked | 6 |
| Mismatches remaining | 0 |

The check distinguished eligible-event coverage from source representation, retained the small non-zero MOT17 decimal-second timing differences, and confirmed that both the tables and summary use the values. A second clean generation produced identical files.

## Result

The compact reporting package passed with no mismatch, missing source, private-path or claim-boundary failure. Its manifest identifies the two source reports and records hashes for every other retained reporting file.

## Corrections

An earlier check found that KITTI overlap burden could differ in its final binary-float digit when recalculated. The generator now preserves the exact scalar while checking the calculation within numerical tolerance. This clean-up also removed a stale hash list that named figure files no longer present.

## Scope Limitations

This audit verifies transfer, calculation, file identity and evidence limits. It does not establish participant outcomes, perceptual quality, accessibility, usability, navigation benefit, safety or repeatability outside the recorded environment.
