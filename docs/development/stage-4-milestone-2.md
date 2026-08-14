# Stage 4 Milestone 2: Inspection Corrections and Final Release Refinement

## Status

Implementation candidate under Issue #39 from clean `main`
`799c5ef95d42040d05c2b7d7a757ec765b6d382c`.

## Diagnosis

The retained backend evidence is complete: direct trace lookup succeeded for the first, second,
penultimate and final cues in both MOT17 and KITTI. The observed `0.000s` pedestrian cue also
resolved to its retained event, logical annotation, configuration and render samples.

The confirmed boundary failure is a frontend cache/DOM interaction. At sequence start the old cache
required `time > start + 0.25`; at sequence end it required `time < end - 0.25`. A clamped boundary
can never satisfy that guard while the cursor remains near the edge. The animation loop therefore
repeatedly requested the same window and every response used `replaceChildren()`, replacing cue
buttons during interaction. The trace route itself is not defective.

Related audit findings were also confirmed:

- cue selection displayed trace evidence without pausing, seeking or loading its source frame;
- the `1e-9` frame epsilon could move a timestamp immediately below a boundary into the next frame;
- overlay outcomes were inferred from the transient one-second timeline rather than stable retained
  cue/suppression links; and
- every canvas click selected the nearest cue, even outside the CUE lane.

## Frozen correction boundary

Decision 0019 limits Milestone 2 to read-only inspection corrections: stable boundary windows,
recorded event-outcome projection, explicit cue/source-frame inspection, visible frame structure,
cue-only hit testing and clearer evidence/mapping wording. Workbench Session Contract `0.1.0`, all
Stage 1-3 research semantics/results, baseline configuration and retained audio remain frozen.

## Acceptance evidence

Automated, private, browser, privacy/scope, CI, PR, merge and post-merge evidence will be recorded
only after each gate actually passes.
