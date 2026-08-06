# 0013: Versioned Technical-Evaluation Contract

## Status

Accepted and verified against the manually calculated Stage 3 Milestone 1 oracle on 6 August 2026.
Applied unchanged to the selected real MOT17-02-DPM and KITTI Tracking 0000 evidence chains during
Milestone 2 on the same date.

## Context

Stage 2 provides complete event-to-cue/suppression accounting and deterministic render evidence,
but it does not define evaluation denominators, time references, interval boundaries or levels of
reproducibility. Calculating real-dataset results before fixing those choices would make the method
vulnerable to result-driven redefinition.

## Decision

- Freeze contract `0.1.0` in a schema-validated machine-readable policy and a human-readable method.
- Treat a valid event without a cue, suppression or explicit exclusion as an eligible miss; never
  count intentional suppression as a miss.
- Permit multiple distinct cues for one event as one represented outcome; reject cue-plus-
  suppression, orphan references and duplicate outcome records.
- Report every rate with numerator and denominator and use null for every zero denominator.
- Separate scheduling, render-placement and end-to-end timing in seconds and renderer-rounded
  sample positions; use nearest-rank p95.
- Prefer the rendered zero-based timeline, integer sample intervals and half-open boundaries.
- Validate traceability by resolving and comparing linked records and hashes, not by identifier
  presence.
- Separate semantic, byte, audio and configuration repeat evidence and leave untested levels null.
- Use canonical JSON and content-derived identities; limit repeat claims to tested environments.

## Consequences

- A missed event can produce a complete but warning-bearing evaluation report; structural broken
  links and contradictory outcomes make it invalid.
- Render quantisation may produce non-zero seconds difference alongside zero sample-placement
  error, and the report preserves both rather than hiding the distinction.
- Trailing silence contributes to density and overlap denominators when present in renderer
  metadata, because it is part of the evaluated output timeline.
- Stage 3 Milestone 2 may apply this frozen method to selected real packages but must not change
  formulas to improve results without a new contract version and decision review.
- These technical measures do not support perceptual, participant, accessibility or safety claims.

## Real-data application record

Milestone 2 did not change this decision, contract, report schema, denominator, threshold or
boundary rule in response to observed values. Each selected dataset produced three semantically and
byte-identical reports in the recorded environment. Supplemental mapping-rule, schedule and WAV
link audits are kept outside contract `0.1.0` and governed by Decision 0014.
