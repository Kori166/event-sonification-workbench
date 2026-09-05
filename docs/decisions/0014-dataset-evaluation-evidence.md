# 0014: Dataset Evaluation Evidence

## Status

Accepted for Stage 3 Milestone 2 on 6 August 2026.

## Context

Technical Evaluation Contract `0.1.0` evaluates a prepared and validated evidence chain.

The project evidence is stored across separate Stage 1 event packages, Stage 2 cue packages and Stage 2 audio packages.

Stage 3 therefore needs to combine these verified packages for evaluation without committing private dataset annotations, full generated packages, evaluator inputs or WAV files to Git.

Enough evidence must still be retained in the repository to make the evaluation traceable and reproducible.

## Decision

The existing Stage 2 evidence chains for MOT17 and KITTI will be used only after they pass integrity checks.

These checks include:

* expected package files
* file formatting
* recorded file hashes
* package identities
* deterministic ordering
* event, cue and suppression counts
* links between Stage 1 and Stage 2 records

The verified packages are then combined into a deterministic evaluator input.

The evaluator input preserves:

* logical source annotation and row
* event and cue links
* sonification preset information
* rendered sample ranges
* WAV identity

Private filesystem paths and WAV data are not included.

## Evaluation Runs

Technical Evaluation Contract `0.1.0` is applied without modification.

Each dataset is evaluated three times in separate output directories.

This provides repeatability evidence without changing the evaluation method after seeing the results.

An evaluation report is retained for each dataset.

Supporting evaluation evidence includes:

* a complete JSON metric summary
* fixed order CSV output
* a concise Markdown summary
* an input hash record
* comparison of the three evaluation runs
* selected record traceability checks

Large or private source packages, evaluator inputs, WAV files and duplicate reports remain outside Git.

Their identities, sizes and SHA 256 values are recorded where required.

## Additional Traceability Checks

Additional checks confirm links between:

* cues and mapping rules
* cues and the schedule
* cues and the retained WAV

These are supporting traceability checks.

They are kept separate from the measures formally defined by Technical Evaluation Contract `0.1.0`.

## Rationale

This approach keeps the repository small enough to manage while preserving the evidence needed to verify the evaluation.

The reports retain the complete technical results, including:

* metric values
* numerators and denominators
* `null` values
* diagnostics
* package identities
* report hashes

A researcher with access to the original datasets can reproduce the excluded processing chains and compare the results with the retained reports.

## Consequences

* One technical evaluation report is retained for each dataset.
* Private datasets and large generated packages remain outside Git.
* Evaluation inputs can be reconstructed from the documented process and retained identities.
* Repeated evaluation provides same environment repeatability evidence.
* Deterministic claims are limited to the selected datasets, fixed preset, fixed renderer and recorded environment.
* MOT17 and KITTI remain two selected case studies rather than representative samples of all annotated video datasets.
* Technical evaluation results do not establish perceptual quality or effectiveness.
* No accessibility, usability, navigation or safety claims are supported by these results.