# 0014: Real-data technical-evaluation evidence boundary

## Status

Accepted for Stage 3 Milestone 2 on 6 August 2026.

## Context

Contract `0.1.0` accepts a prepared validated record chain, while the retained real evidence exists as separate Stage 1 event, Stage 2 cue and Stage 2 audio packages. The milestone also needs enough committed evidence for audit and reproduction without committing private annotations, full event/cue packages, evaluator inputs or WAV files.

## Decision

- Reuse the two independently generated Stage 2 chains only after checking exact membership, canonical serialisation, every documented physical hash, content-derived package identity, ordering, accounting and cross-stage link.
- Assemble the verified package contracts into a deterministic evaluator input. Preserve logical source file/row references, cue-to-event links, preset evidence, render ranges and WAV identity; do not embed WAV bytes or private paths.
- Apply frozen contract `0.1.0` unchanged three times per dataset in isolated directories.
- Commit one canonical report per dataset because the two reports are reasonably sized, plus a lossless JSON metric summary, fixed-order CSV, bounded Markdown, input hash manifest, three-run comparison and deterministic selected-record audit.
- Exclude private/generated source chains, evaluator inputs and repeat report copies while recording their logical location, size and SHA-256 in the close-out.
- Treat cue-to-mapping-rule, cue-to-schedule and cue-to-WAV checks as supplemental resolved-link audits. They must be labelled separately and must not be presented as new contract `0.1.0` fields.
- Limit deterministic claims to the recorded environment and the selected sequence, preset and renderer.

## Consequences

- The repository retains complete metric values, numerators, denominators, nulls, diagnostics, identities and canonical report hashes without retaining private or redundant large artefacts.
- A user with the private datasets can reproduce the excluded chains and verify every committed report through the versioned protocol, experiment manifest, environment manifest and commands.
- The selected MOT17 and KITTI sequences remain bounded case studies rather than representative populations.
- Technical coverage, timing, traceability, density, overlap and repeat evidence do not establish perceptual effectiveness, accessibility, usability, navigation benefit or safety.
