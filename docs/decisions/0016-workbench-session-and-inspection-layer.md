# 0016: Workbench session and inspection layer

## Status

Accepted for Stage 4 Milestone 1 Phase 1 on 7 August 2026.

## Context

Stages 1 to 3 already define and verify deterministic event packages, cue and suppression packages,
audio packages, provenance links and technical-evaluation reports. Stage 4 requires a local
inspection interface that can present those artefacts together with dataset media. Reimplementing
parsing, cue mapping, audio rendering or evaluation logic in the interface would create a second
research pipeline and weaken traceability to the verified evidence.

The Stage 4 interface is therefore research infrastructure for inspection and demonstration. It is
not participant evidence and does not establish accessibility, usability, navigation, perceptual
effectiveness or safety.

## Decision

Workbench Session Contract `0.1.0` is frozen before browser code is introduced.

A session identifies one compatible Stage 1 event package, Stage 2 cue package, Stage 2 audio
package and, optionally, one Stage 3 technical-evaluation report. The headless Python session loader
must validate the session schema, reuse the established Stage 1 to 3 package-validation path, verify
cross-stage identities and hashes, and resolve dataset media only after the deterministic evidence
chain has been accepted.

The browser layer will receive only an already validated session representation. It will be
read-only with respect to Stage 1 to 3 packages and will not recalculate research metrics or
regenerate sonification outputs.

The deterministic session identity is content-derived from the dataset, sequence, package run IDs,
package and file hashes, configuration identities and optional evaluation identity. Runtime storage
locations are excluded from that identity. Dataset and output roots are supplied separately through
runtime bindings such as `MOT17_ROOT`, `KITTI_TRACKING_ROOT` and `OUTPUT_ROOT`.

## Rationale

This boundary preserves the existing reproducibility and provenance model. A package can move to a
different machine or directory without changing the identity of the evidence it contains. The
interface can also change independently without changing the Stage 1 to 3 research contracts.

Reusing the existing package validators prevents Stage 4 from defining a weaker interpretation of
package validity. A session is accepted only when its underlying evidence chain is already valid and
the session's declared identities match the verified files.

## Consequences

- Mismatched, missing or tampered package chains are rejected before UI rendering.
- Absolute local paths, machine names and usernames must not enter `session_id` or exported
  diagnostics.
- Raw MOT17 and KITTI Tracking media remain runtime dependencies outside Git.
- An unavailable Stage 3 report does not prevent package inspection; the session records
  `evaluation.available = false` and no substitute metric is calculated.
- Display-only waveform, spectrogram or timeline visualisations do not become technical-evaluation
  evidence merely because they appear beside verified metrics.
- Stage 4 may add presentation and media-serving components, but Stage 1 to 3 contracts remain
  unchanged unless a separate explicit decision supersedes them.
