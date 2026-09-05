# 0015: Verified Evaluation Results

## Status

Accepted for Stage 3 Milestone 3 on 6 August 2026.

## Context

Stage 3 Milestone 2 produced technical evaluation reports for the retained MOT17 and KITTI cases using Technical Evaluation Contract `0.1.0`.

These reports contain the main numerical evidence used to describe the technical behaviour of the workbench.

The results need to remain traceable to the original evaluation evidence so that values, calculations and interpretations can be checked.

## Decision

The Stage 3 evaluation reports will remain the main numerical source for technical findings.

The identity and integrity of each report must be verified using its recorded schema and hash.

Technical findings may use:

* values taken directly from the evaluation reports
* values calculated from recorded evaluation data
* appropriately rounded values for presentation

Where a value is calculated or rounded, the original value and calculation must remain traceable.

Direct values and calculated values must remain distinguishable.

The reports must not be changed to support a later interpretation.

## Interpretation Rules

Source representation and eligible event coverage remain separate measures because they answer different questions and use different denominators.

Timing is considered in both audio samples and seconds.

Exact sample placement means that cues were placed at their expected integer sample positions.

A very small difference expressed in decimal seconds does not necessarily contradict exact sample placement.

Comparisons between MOT17 and KITTI are limited to descriptive technical differences for:

* the selected dataset sequences
* the fixed sonification preset
* the fixed renderer
* the recorded software environment

The results do not show that one dataset, mapping or audio output is better for listeners.

## Rationale

Using the Stage 3 reports as the main evidence source preserves a clear link between the evaluation process and the findings drawn from it.

Keeping original values alongside any calculated or displayed values also prevents rounding or later interpretation from changing the underlying evidence.

This allows the technical results to be checked without changing the evaluation method or the retained source evidence.

## Consequences

* Technical findings must remain traceable to the Stage 3 evaluation reports.
* Rounded values do not replace the original exact values.
* Small non zero values must not be treated as zero without justification.
* `null` values remain different from numerical zero.
* Technical Evaluation Contract `0.1.0` remains unchanged.
* The evaluation reports remain unchanged.
* Comparisons between datasets remain descriptive and limited to the tested cases.
* The results provide technical evidence only.
* No participant, perceptual, accessibility, usability, navigation or safety claims are supported by this evaluation.