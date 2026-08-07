# 0016: Workbench session and inspection layer

## Status

Accepted for Stage 4 Milestone 1 Phase 1 on 7 August 2026.

Implementation clarification added on 7 August 2026 after PR #28 merged: runtime package storage may
use separate event, cue and audio roots. This does not change Workbench Session Contract `0.1.0` or
the deterministic identity boundary.

Implementation history: PR #30 applied this clarification but was merged before the private retained-
chain acceptance gate was run. PR #31 reverted PR #30 in full. The correction was then reapplied on
a fresh branch under reopened Issue #29 so that clean CI and private retained-chain acceptance could
both be evidenced before the final merge. This history changes neither the decision nor the frozen
session contract.

Final implementation note, 7 August 2026: PR #32's separate runtime-root clarification passed the
retained-chain acceptance test for both MOT17 and KITTI Tracking. Workbench Session Contract `0.1.0`
remained unchanged, and runtime storage locations continue to be non-identity state.

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
locations are excluded from that identity. Dataset and package roots are supplied separately through
runtime bindings.

Package resolution may use `EVENT_PACKAGE_ROOT`, `CUE_PACKAGE_ROOT` and `AUDIO_PACKAGE_ROOT` when
the three package types are stored separately. `OUTPUT_ROOT` remains a common-root fallback when a
single directory contains all run directories. Dataset media continues to use `MOT17_ROOT` or
`KITTI_TRACKING_ROOT`. None of these runtime values contributes to `session_id` or appears in
returned diagnostics.

## Rationale

This boundary preserves the existing reproducibility and provenance model. A package can move to a
different machine or directory without changing the identity of the evidence it contains. The
interface can also change independently without changing the Stage 1 to 3 research contracts.

Reusing the existing package validators prevents Stage 4 from defining a weaker interpretation of
package validity. A session is accepted only when its underlying evidence chain is already valid and
the session's declared identities match the verified files.

The separate package-root clarification is required because retained Stage 2 evidence stores event,
cue and audio packages beneath distinct stage directories. Treating that storage layout as runtime
state avoids encoding a historical local directory convention into the frozen session contract.

## Consequences

- Mismatched, missing or tampered package chains are rejected before UI rendering.
- Absolute local paths, machine names and usernames must not enter `session_id` or exported
  diagnostics.
- Runtime package layout can change without changing Workbench Session Contract `0.1.0`.
- Raw MOT17 and KITTI Tracking media remain runtime dependencies outside Git.
- An unavailable Stage 3 report does not prevent package inspection; the session records
  `evaluation.available = false` and no substitute metric is calculated.
- Display-only waveform, spectrogram or timeline visualisations do not become technical-evaluation
  evidence merely because they appear beside verified metrics.
- Stage 4 may add presentation and media-serving components, but Stage 1 to 3 contracts remain
  unchanged unless a separate explicit decision supersedes them.
