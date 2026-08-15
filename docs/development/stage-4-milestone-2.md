# Stage 4 Milestone 2: Inspection Corrections and Final Release Refinement

## Status

Follow-up correction candidate on draft PR #40 under Issue #39. The first candidate was
`02130795678b991e07570b64052d6d1442aeb889`, based on clean `main`
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

### Follow-up playback and presentation diagnosis

The first researcher-controlled acceptance attempt did not pass. The researcher observed visible
Firefox playback lag, more severe Chrome freezing/stutter, cue controls reordering after selection,
confusing `unresolved` legend terminology and an overly technical, duplicative Frozen Baseline
Mapping section.

Execution-frequency profiling of the candidate separated the browser work as follows:

- every display refresh read `audio.currentTime`, updated transport text, invoked the guarded frame
  and timeline loaders, and fully repainted the timeline canvas;
- every audio-time change changed the cursor/seek state;
- every source-frame transition fetched one bounded frame projection and source image, then rebuilt
  the SVG overlay; and
- every accepted timeline-window response rebuilt the evidence markers and cue-control DOM.

The confirmed avoidable playback cost was the full display-rate repaint of every retained timeline
marker. A dense MOT17 one-second window contains thousands of EVENT/CUE/SUPPRESS markers, so the
same static marker set was redrawn on every animation refresh even though only the cursor and current
frame interval had changed. `loadFrame()` was also called on every refresh merely to reach its
same-frame guard. Separately, cue controls were sorted by distance from `audio.currentTime`; cue
selection seeks that clock and therefore changed the ordering origin.

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
- The dense static timeline layer is now rebuilt only on a window change or resize. The animation
  loop only updates transport state, checks for an actual source-frame transition and composites the
  cached layer with the current interval, selection and cursor. Paused, unchanged time does no work.
- Frame projection/image requests now start only on frame transitions or explicit cue/session
  actions. Images are prepared off-screen before the visible source changes; at most the following
  two frames are preloaded through the existing read-only route. Preloads are session-scoped and
  cannot replace visible state.
- Only one ordinary timeline request may be in flight. Existing generation/request IDs still reject
  stale frame, timeline and trace responses, and clamped window coverage remains stable.
- Cue controls use `(start_time_seconds, track_id, cue_id)` order. Selecting an already visible cue
  changes highlight/provenance only; it neither refetches the window nor reconstructs the buttons.
- Normal overlay semantics now show only `Cue generated` and `Intentionally suppressed`.
  Backend `unresolved` detection remains, but the frontend presents it as a neutral, path-free
  evidence-integrity anomaly and emits a stable diagnostic rather than a research category.
- EVENT/CUE/SUPPRESS and cue-mapping explanations now use plain technical wording. Detailed
  `class_modifier` treatment remains in Configuration provenance.

Follow-up local results on Windows / Python 3.14.3:

- Ruff: passed;
- frontend JavaScript syntax: passed;
- focused workbench suite: 26 passed in 6.83s;
- complete non-integration suite: 278 passed, 6 deselected in 34.16s;
- Phase 1 retained-chain private integration: 1 passed in 54.72s;
- Phase 2 MOT17 inspection private integration: 1 passed in 29.71s; and
- Phase 3 cross-dataset private integration: 1 passed in 31.75s.

The expanded private cross-dataset gate follows the first, second, penultimate and final retained
cues for both datasets, confirms every displayed event resolves to cue generation or intentional
suppression, and verifies cue/event frame identity, class modifier availability, render linkage,
genuine media and exact WAV hashes.

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
- The follow-up preflight confirmed repeated MOT17 cue selection kept the same ten ordered controls
  and only changed the selected highlight. Separate continuous runs progressed MOT17 to frame 316 at
  10.565s and KITTI to frame 106 at 10.658s with no integrity warning. Preparing images before the
  visible swap eliminated new aborted-image transfers in the local service log. This is diagnostic
  engineering evidence only; it is not the Firefox/Chrome researcher gate.

### First researcher-controlled browser acceptance attempt

The first attempt against `02130795678b991e07570b64052d6d1442aeb889` failed its release gate. It
identified Firefox playback lag, more severe Chrome freezing/stutter, cue controls reordering after
selection, confusing normal presentation of `unresolved`, and a confusing Frozen Baseline Mapping
section. These are engineering/presentation findings only, not usability or perceptual evidence.

### Revised researcher-controlled browser acceptance procedure

This gate is pending researcher observation. Launch the primary command, open
`http://127.0.0.1:8765/`, keep browser zoom at 100%, and open Developer Tools Console. Record each
item as pass/fail with a short observation; do not treat the result as usability or perceptual
testing.

1. On MOT17, select `0.000s · pedestrian · t10`; confirm its trace opens.
2. Select that cue repeatedly at least five times; confirm the control and trace remain stable.
3. Seek to the end and select a `19.967s` window cue; confirm its trace opens at source frame 599.
4. Seek to approximately 0.034s and select `0.033s · pedestrian · t10`; confirm cue source frame 001,
   playback time 0.033333s and provenance source frame 1 agree.
5. On KITTI, select `0.000s · van · t0` repeatedly; confirm trace/frame 000 stability.
6. Seek to the end and select `15.300s · car · t9`; confirm its trace opens at source frame 153.
7. Confirm subtle vertical frame divisions and usable frame-number labels appear in both datasets.
8. Confirm the current frame interval is visibly highlighted.
9. Confirm the thin white playback cursor remains distinct from the frame-interval highlight.
10. Confirm EVENT/CUE/SUPPRESS wording explains Stage 1 events and Stage 2 outcomes clearly.
11. Confirm the overlay legend contains only the expected normal outcomes: `Cue generated` and
    `Intentionally suppressed`.
12. Click EVENT, SUPPRESS and empty canvas areas; confirm none selects a cue. Click directly on a CUE
    marker and confirm it does.
13. Confirm `Cues in this evidence window` remain in deterministic chronological order before and
    after selecting several controls, including equal-time controls ordered by track and cue ID.
14. Confirm the simple Time/Left-right/Pitch/Loudness explanation is understandable and accurate,
    states that the technical baseline is not perceptually validated, and makes no depth claim.
15. Confirm a selected cue exposes start, frequency, pan, amplitude, duration, class/track/frame,
    logical annotation, configuration and render samples; class modifier remains configuration-only
    and is described as recorded for traceability but not applied to waveform.
16. Perform MOT17 → KITTI → MOT17; confirm frame/time/trace/selection and dataset content reset.
17. Perform KITTI → MOT17 → KITTI and confirm the same isolation.
18. In Firefox at 100% zoom, play MOT17 continuously for 10 seconds; confirm no visible freezing,
    source images progress, audio remains continuous and the timeline cursor moves.
19. In Firefox at 100% zoom, play KITTI continuously for 10 seconds and confirm the same behaviour.
20. In Chrome at 100% zoom, play MOT17 continuously for 10 seconds and confirm the same behaviour.
21. In Chrome at 100% zoom, play KITTI continuously for 10 seconds and confirm the same behaviour.
22. Confirm both browser consoles contain no errors or warnings attributable to the workbench.

These checks are technical browser acceptance, not usability or perceptual evaluation. Fresh hosted
CI is required on the exact revised head before this candidate is returned for the retest. PR #40
must remain draft and unmerged until the researcher supplies the new observations.
