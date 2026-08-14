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

### Implementation and automated gates

- Clamped start/end windows now remain cached at their sequence edge. A pending-window key prevents
  duplicate in-flight requests, while monotonically increasing request IDs reject older responses.
- Cue selection now has its own request generation, pauses playback, seeks to the retained cue start,
  loads the trace's recorded event frame and visibly labels that frame as the cue source frame.
- Exact playback derivation uses `floor(time * fps)` with half-open intervals. Tests cover immediately
  below, exactly at and immediately above a boundary.
- Frame projections now resolve Stage 2 outcome from immutable cue/suppression indexes rather than
  the current timeline window.
- The canvas draws frame boundaries, a current-frame interval, the exact white playback cursor and
  selected-cue emphasis. Hit testing accepts only a bounded CUE-lane marker.
- Overlay/evidence terminology, nearby-cue labelling, selected parameters and the frozen mapping key
  now describe the retained evidence consistently.

Final local results on Windows / Python 3.14.3:

- Ruff: passed;
- frontend JavaScript syntax: passed;
- focused workbench suite: 22 passed in 9.56s;
- complete non-integration suite: 274 passed, 6 deselected in 39.72s;
- Phase 1 retained-chain private integration: 1 passed in 64.32s;
- Phase 2 MOT17 inspection private integration: 1 passed in 34.55s; and
- Phase 3 cross-dataset private integration: 1 passed in 37.15s.

The expanded private cross-dataset gate follows the first, second, penultimate and final retained
cues for both datasets and confirms cue/event frame identity, class modifier availability, render
linkage, stable frame outcomes, genuine media and exact WAV hashes.

### Privacy and scope audit

The complete Milestone 2 diff contains no binary, media, WAV, screenshot, browser storage, temporary
output, username, machine path, private root or local environment value. The only path-pattern hits
are deliberate privacy-test regular expressions. No workbench contract/declaration, Stage 1 schema
or parser, Stage 2 preset/scheduler/renderer, Stage 3 contract/report or canonical evidence path is
changed. `git diff --check` passes.

### Codex browser preflight

Codex exercised both retained datasets in the local browser as a technical preflight, without
claiming the researcher-only visual/semantic acceptance below. No screenshot was saved or committed.

- MOT17: the observed `0.000s · pedestrian · t10` opened repeatedly; a final-time cue opened at
  19.966667s/frame 599; and the rounded 0.033333s cue explicitly remained on recorded frame 1.
- KITTI: the first cue opened repeatedly at frame 0 and a final-time cue opened at 15.3s/frame 153.
- Both switch directions repeated twice and restored playback-frame label, frame 000, time zero,
  empty trace selection and no active nearby cue.
- Trace views exposed class, track, source frame, start, frequency, pan, amplitude, duration, class
  modifier, annotation, configuration and render samples.

### Researcher-controlled browser acceptance procedure

This gate is pending researcher observation. Launch the primary command, open
`http://127.0.0.1:8765/`, keep browser zoom at 100%, and open Developer Tools Console. Record each
item as pass/fail with a short observation; do not treat the result as usability or perceptual
testing.

1. On MOT17, select `0.000s · pedestrian · t10`; confirm its trace opens.
2. Select that cue repeatedly at least five times; confirm the control and trace remain stable.
3. Seek to the end and select a `19.967s` nearby cue; confirm its trace opens at source frame 599.
4. Seek to approximately 0.034s and select `0.033s · pedestrian · t10`; confirm cue source frame 001,
   playback time 0.033333s and provenance source frame 1 agree.
5. On KITTI, select `0.000s · van · t0` repeatedly; confirm trace/frame 000 stability.
6. Seek to the end and select `15.300s · car · t9`; confirm its trace opens at source frame 153.
7. Confirm subtle vertical frame divisions and usable frame-number labels appear in both datasets.
8. Confirm the current frame interval is visibly highlighted.
9. Confirm the thin white playback cursor remains distinct from the frame-interval highlight.
10. Confirm EVENT/CUE/SUPPRESS wording explains Stage 1 events and Stage 2 outcomes clearly.
11. Confirm the overlay legend uses the same event/outcome relationship.
12. Click EVENT, SUPPRESS and empty canvas areas; confirm none selects a cue. Click directly on a CUE
    marker and confirm it does. Nearby controls must be labelled `Nearby cues`.
13. Confirm a selected cue exposes frequency, pan, amplitude, duration, class/track/frame and retained
    provenance; confirm the mapping key matches the frozen baseline and class modifier is trace-only.
14. Perform MOT17 → KITTI → MOT17; confirm frame/time/trace/selection and dataset content reset.
15. Perform KITTI → MOT17 → KITTI and confirm the same isolation.
16. Confirm the browser console contains no errors or warnings attributable to the workbench.

Hosted CI, PR, merge and post-merge evidence remain pending after researcher acceptance.
