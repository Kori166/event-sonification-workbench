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

### Final cue-discoverability diagnosis

The next researcher-controlled attempt confirmed the performance correction, including ten-second
playback in Firefox and Chrome for both datasets, but did not pass the release gate. The remaining
cue defect is not missing retained evidence. `renderWindowCues()` sorted every cue in the one-second
window and then applied `.slice(0, 10)`. Dense earlier cues therefore displaced later controls,
including final-frame and cyclist/bicycle-related cues that remained visible as canvas markers.

A marker already inside the cached evidence window called `selectCue()` without reloading that
window. That avoided the previous DOM churn but preserved the same broad, truncated control group;
it did not establish a frame-local cue context. Frame is already retained on every cue projection,
so the smallest complete correction is a read-only frame cue projection rather than a wider
timeline or any Stage 2 recomputation.

### Final interaction diagnosis

The subsequent researcher-controlled pass confirmed nearly all 28 checks, including complete
first/final/dense frame groups, cyclist discoverability, marker context, frame presentation,
provenance, deterministic controls, session isolation and ten-second Firefox/Chrome playback.

One transport defect remained. `selectCue()` explicitly assigned the retained cue time to both
`audio.currentTime` and `state.lastPlaybackTime`, but updated only the range input. The animation
loop updates the numeric time only when those two values differ, so its next iteration correctly
skipped the presentation block and left the text stale. This is a frontend presentation defect;
retained time/frame evidence remains correct.

The same inspection also established a bounded interaction requirement: represented Stage 1 video
boxes should select their already-linked retained Stage 2 cue. Frame projections already expose the
exact relationship as `stage_2_outcome.cue_id`; no timestamp, class, track or canvas-position
inference is needed. Suppressed boxes have no cue and remain contextual evidence.

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
- Each frame response now includes every retained Stage 2 cue whose recorded source frame matches
  that frame. The control group is scoped to the displayed frame, has an explicit frame/count label
  and supports zero, one or many cues without fixed-count truncation.
- Clicking a CUE marker continues to pause and load its retained source frame; that frame load now
  establishes the complete sibling-cue group. Selecting a sibling on the same frame updates only
  its active highlight, selected marker and provenance, without rebuilding or reordering the group.
- The one-second canvas, cached static layer, cue-only hit testing, frame divisions, highlighted
  interval and thin white exact playback cursor are unchanged.
- A single transport-presentation helper updates the range value and formatted numeric time for
  explicit cue selection, seek/frame-step actions, session reset and animation-driven playback.
  Explicit cue selection invokes it immediately before asynchronous frame/trace work.
- Represented video overlay groups read their exact retained `stage_2_outcome.cue_id` and invoke the
  same `selectCue()` path as timeline markers and frame buttons. They expose restrained hover,
  focus and selected states plus Enter/Space operation. Suppressed/anomaly boxes receive no cue
  control, cue identity or selection handler.
- Normal overlay semantics now show only `Cue generated` and `Intentionally suppressed`.
  Backend `unresolved` detection remains, but the frontend presents it as a neutral, path-free
  evidence-integrity anomaly and emits a stable diagnostic rather than a research category.
- EVENT/CUE/SUPPRESS detail is available through a collapsed native `details` help control, while
  the lane names remain visible. The redundant overlay-legend lead-in was removed. Cue-mapping
  wording and detailed `class_modifier` treatment remain accurate.

Previous follow-up local results on Windows / Python 3.14.3:

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

Final frame-scoped follow-up results on Windows / Python 3.14.3:

- Ruff: passed;
- frontend JavaScript syntax: passed;
- focused workbench suite: 27 passed in 9.07s;
- complete non-integration suite: 279 passed, 6 deselected in 43.64s;
- Phase 1 retained-chain private integration: 1 passed in 69.34s;
- Phase 2 MOT17 inspection private integration: 1 passed in 31.22s; and
- Phase 3 cross-dataset private integration: 1 passed in 28.84s.

The final private gate compares every frame's complete cue projection with the represented outcome
IDs on that frame. For both datasets it directly checks the first, densest and final cue groups,
traces every cue in those selected groups and re-verifies exact declared WAV hashes. The retained
MOT17 final group is frame 599; the retained KITTI final group is frame 153. KITTI's real frame-0
van/cyclist/pedestrian group is complete, stable and independently traceable.

Final interaction-correction results on Windows / Python 3.14.3:

- Ruff: passed;
- frontend JavaScript syntax: passed;
- focused workbench suite: 28 passed in 7.48s;
- complete non-integration suite: 280 passed, 6 deselected in 38.14s;
- Phase 1 retained-chain private integration: 1 passed in 61.61s;
- Phase 2 MOT17 inspection private integration: 1 passed in 29.50s; and
- Phase 3 cross-dataset private integration: 1 passed in 30.80s.

The retained integrations again verify genuine media, complete outcome/cue/trace projections and
the exact declared WAV hashes. No retained package was regenerated.

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
- The performance follow-up preflight confirmed repeated MOT17 selection preserved its then-visible
  ordered controls and changed only the selected highlight. Separate continuous runs progressed
  MOT17 to frame 316 at 10.565s and KITTI to frame 106 at 10.658s with no integrity warning.
- The final frame-scoped preflight exposed all 35 MOT17 frame-0 cues and all 37 frame-599 cues. The
  KITTI frame-0 group contained van, cyclist and pedestrian controls, and frame 153 exposed all nine
  cues. Repeated/sibling selection retained order; a CUE marker changed frame 1 to its deterministic
  frame-0 group while EVENT, SUPPRESS and empty-lane clicks did not. Help was initially collapsed,
  expanded through its native control and retained the full explanation. Ten-second runs reached
  MOT17 frame 322 and KITTI frame 109, and the in-app technical console contained no warnings or
  errors. This is diagnostic engineering evidence only; it is not the Firefox/Chrome researcher
  gate and does not satisfy items 27-28.
- The final interaction preflight selected a MOT17 `0.033333s` CUE marker and immediately observed
  `00:00.033`, frame 001 and matching active frame-button/video cue IDs. Click, Enter and Space on
  represented video controls selected their exact projected cue; two same-frame siblings retained
  control order and Space did not start playback. Suppressed boxes exposed no role, tab stop or cue
  ID. Video, timeline and frame-button routes converged on one cue ID/frame; the real KITTI cyclist
  box selected its matching cue and complete trace. Ten-second runs reached KITTI frame 108 and
  MOT17 frame 322, with no in-app console warnings or errors. This remains Codex technical
  preflight, not the final Firefox/Chrome researcher gate.

### First researcher-controlled browser acceptance attempt

The first attempt against `02130795678b991e07570b64052d6d1442aeb889` failed its release gate. It
identified Firefox playback lag, more severe Chrome freezing/stutter, cue controls reordering after
selection, confusing normal presentation of `unresolved`, and a confusing Frozen Baseline Mapping
section. These are engineering/presentation findings only, not usability or perceptual evidence.

### Second researcher-controlled browser acceptance attempt

The next attempt against `8426461ec386d4e2b5fb90ebb100a6188085ef07` also did not pass the release
gate. It confirmed first and repeated cues, rounded frame-1 alignment, KITTI frame 000, frame
divisions/current interval, cue-only canvas interaction, deterministic ordering, mapping wording,
both switch directions and ten-second Firefox/Chrome playback on both datasets.

The remaining observations were that MOT17 controls reached only approximately frame 573 instead of
the final cue frame 599; KITTI controls reached only approximately frame 145 instead of frame 153;
some visible cyclist/bicycle-related cues had no inspection button; and selecting a CUE marker did
not replace the broad window group with the expected frame-local controls. The researcher also
requested collapsed lane help and removal of the overlay-legend lead-in. Explicit confirmation of
the thin white playback cursor and final Firefox/Chrome console results remained pending. These are
iterative technical inspection findings, not usability or perceptual evidence.

### Third researcher-controlled browser acceptance attempt

The latest pass against `6c73a1754eed2d2a40e9d6480afc982ccf81e357` confirmed the large majority
of the 28-check procedure: first/final cues, complete frame groups, dense multi-class and cyclist
cue discoverability, marker context, deterministic selection, frame divisions/current interval,
the distinct thin white cursor, collapsed help, simplified legend/mapping, complete provenance,
both session-switch directions and ten-second Firefox/Chrome playback on both retained datasets.

It found one remaining defect: cue selection moved the slider, cursor, source frame and provenance
but left the numeric transport-time text at its previous value. It also supplied one bounded
technical requirement: a represented cue shown as a green video bounding box should be directly
selectable through the same retained cue-selection path. This is researcher-controlled technical
inspection, not participant feedback or usability/accessibility/perceptual evaluation.

### Final focused researcher-controlled browser acceptance

The researcher completed the final focused gate against implementation candidate
`39cf6953b72c30a03e920f672a81259b44399c12` on 18 August 2026. All 16 checks passed:

1. MOT17 first-cue slider, numeric time, white cursor, source frame and provenance aligned.
2. The MOT17 `0.033333s` CUE marker displayed approximately `00:00.033` and remained on frame 1.
3. A clearly later MOT17 cue updated numeric time immediately.
4. Equivalent KITTI cue selection aligned transport, frame and provenance.
5. A represented MOT17 video box selected its exact retained cue and matching inspection state.
6. A different same-frame represented box selected the correct sibling without reordering buttons.
7. A represented KITTI video box selected its exact retained cue and provenance.
8. A cyclist/bicycle-related represented KITTI box was selectable.
9. Intentionally suppressed boxes did not behave as generated cue controls.
10. Video box, CUE marker and frame button routes resolved the same cue ID and source frame.
11. MOT17 frame 599 retained its final cue group and trace.
12. KITTI frame 153 retained its final cue group and trace.
13. Firefox playback remained smooth.
14. Chrome playback remained smooth.
15. The Firefox console contained no workbench errors or warnings.
16. The Chrome console contained no workbench errors or warnings.

This is researcher-controlled technical browser acceptance, not participant feedback or usability,
accessibility or perceptual evaluation. The implementation candidate had already passed exact-head
hosted CI run 32131916988. A documentation-only acceptance commit still requires exact-head CI
before PR #40 can merge, followed by post-merge `main` CI and close-out recording.
