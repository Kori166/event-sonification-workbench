# 0015: Verified Evaluation Results For Reporting

## Status

Accepted for Stage 3 Milestone 3 on 6 August 2026.

## Context

Stage 3 Milestone 2 produced two verified technical evaluation reports using the fixed Evaluation Contract `0.1.0`.

The dissertation needs clear tables and findings based on those reports.

Copying values manually or rounding them without recording the source could weaken traceability between the dissertation and the original evaluation evidence.

## Decision

The two canonical evaluation reports remain the main numerical source.

Before any reporting material is created, their expected hashes and schemas must be checked.

Report material will be generated deterministically from those verified reports.

This includes:

* CSV tables
* Markdown tables
* report values
* presentation material

Generated reporting files must not include timestamps, private paths, random identifiers or environment dependent metadata.

Each reported value must retain a clear link to its source.

The reporting evidence records:

* the source location in the canonical report
* the original value
* the displayed value
* any calculation used
* any interpretation limit

Direct values and recalculated values are checked separately.

Formatting, reported claims, source preservation and repeated output are also verified.

## Reporting Rules

Source representation and eligible event coverage remain separate because they use different denominators.

Timing is reported in both audio samples and seconds.

Exact sample placement does not mean that every decimal difference expressed in seconds must also be exactly zero.

Comparisons between MOT17 and KITTI are limited to descriptive technical differences for:

* the selected dataset cases
* the fixed baseline preset
* the fixed renderer
* the recorded execution environment

The results are not treated as evidence that one dataset or mapping is better for listeners.

## Rationale

This approach keeps a direct and auditable link between the dissertation results and the canonical Stage 3 evidence.

It also prevents presentation rounding or manual editing from changing the meaning of the original results.

The reporting process therefore prepares the verified findings for presentation without changing the evaluation method or source evidence.

## Consequences

* Dissertation tables and reported findings can be traced back to the canonical evaluation reports.
* Displayed rounding does not replace the original exact values.
* Small non zero values cannot silently become zero.
* `null` values remain distinct from numerical zero.
* The reporting process does not change Evaluation Contract `0.1.0`.
* The canonical evaluation reports remain unchanged.
* Reporting does not create new participant or perceptual evidence.
* No accessibility, usability, navigation, mobility or safety claims are added.

The generated file hash record excludes only its own hash because a file cannot include a final hash of itself without creating a recursive value.