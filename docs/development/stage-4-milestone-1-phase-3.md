# Stage 4 Milestone 1 Phase 3: Cross-Dataset Completion and Release Preparation

## Status

Implementation in progress under Issue #37 from clean `main` at
`16e20e811d4ed654fe60e36f2769b9884ad871ae`.

## Frozen scope

Decision 0018 freezes Phase 3 as retained-evidence assembly and cross-dataset verification through
Workbench Session Contract `0.1.0`. The same validated-session, immutable inspection-model,
loopback-service and browser-client path will expose only:

- MOT17 session `session-mot17-mot17-02-dpm-3707826663b210c6`; and
- KITTI Tracking session `session-kitti_tracking-0000-9cae092175c68109`.

No Stage 1 parsing/normalisation, Stage 2 scheduling/rendering or Stage 3 evaluation logic is added
to the workbench. No accepted research output will be regenerated or modified.

## Audited retained KITTI evidence

The existing Stage 3 manifest identifies retained KITTI Tracking sequence `0000` evidence with
1,089 valid events, 711 cues, 378 `dont_care_excluded` suppressions and 711 rendered cues. The exact
retained WAV SHA-256 is
`9fe11798dfaca388f10af21c346d49efa3507c1879ae2fff50e2a7d6d7d5e6ce`. The verified Stage 3 report
is `evaluation-kitti_tracking-0000-d997cdc8f6467c1d`, with repository report SHA-256
`b5589590a8c645bd7b5654d0318bf90fdb412f987719c26c2374bf3e487f9ff2`.

The runtime media binding is logical path `training/image_02/0000` below
`KITTI_TRACKING_ROOT`. The retained evidence records 154 zero-based 1242 by 375 PNG frames at 10 fps.
Private dataset/package roots and media remain outside Git.

## Acceptance evidence

### Implementation candidate

- Added the two-entry path-free catalogue
  `configs/workbench/retained-sessions.v0.1.0.json` with MOT17 as the default.
- Added retained KITTI declaration `configs/workbench/kitti-phase-3-session.v0.1.0.json`; its
  deterministic ID reproduces from the existing package/report/configuration hashes.
- Added immutable `InspectionCatalogue` summaries and lookup with stable
  `invalid_session_identifier` failure.
- Added `/api/sessions` and optional `session_id` scoping to the existing frame, image, timeline,
  trace, evaluation and exact-WAV routes. Unscoped routes retain the default MOT17 behaviour.
- Added a minimal browser selector with generation-based request isolation and explicit clearing of
  image/frame, playback, timeline, selected cue/trace, metrics, metadata and notice state.
- Kept one primary release command: `python -m event_sonification_workbench.cli inspect-session`.
  It validated both real retained chains before opening the loopback service. `--session` remains a
  single-declaration diagnostic option, not a browser import mechanism.

Focused automated evidence at the implementation commit:

- Ruff: passed;
- frontend JavaScript syntax: passed;
- catalogue/session/service/frontend focused tests: 19 passed in 4.51s; and
- new retained cross-dataset private integration: 1 passed in 39.03s.

The private integration opened both real sessions through the frozen validator/model, checked 600
MOT17 and 154 KITTI frames, genuine JPEG/PNG media, recorded boxes, events/cues/suppressions, real cue
traces, exact retained WAV hashes, direct verified reports, repeated catalogue lookup in both
directions and path-free scoped service projections.

### Controlled browser acceptance

Codex performed the controlled browser/technical checks against the locally validated service on 14
August 2026. No screenshot or browser artefact was saved or committed. This was not participant,
usability, accessibility, navigation or perceptual testing.

All thirteen KITTI checks passed:

1. the selected session loaded as KITTI Tracking sequence `0000` with the expected session ID;
2. genuine retained KITTI PNG imagery rendered;
3. recorded Stage 1 boxes visibly aligned with vehicles, cyclist, pedestrian and `DontCare` regions
   without workbench recalculation;
4. the exact retained WAV was selected and played;
5. audio `currentTime` advanced and drove the frame/timeline state (approximately 1.216 seconds with
   frame progression observed);
6. paused `+1f` advanced time by 0.1 seconds and frame 14 to 15, while `-1f` restored both;
7. EVENT, CUE and SUPPRESS lanes remained populated and synchronised;
8. a real cue resolved to KITTI event frame 15/track 0, logical annotation
   `training/label_02/0000.txt` row 70, baseline preset/renderer and samples 66,150-71,442;
9. verified KITTI Stage 3 cards displayed 100.00% eligible-event coverage, 65.29% source
   representation, 46.11 cues/second, peak concurrency 24, 34.71% suppression, 100.00% fully
   traceable cues, zero P95 alignment and identical byte reproducibility directly from the report;
10. scoped session/frame/evaluation/timeline/trace responses contained no private-path marker;
11. `frame_out_of_range`, `cue_not_found`, `route_not_found` and
    `invalid_session_identifier` remained stable and path-free;
12. the 900-pixel responsive layout retained image/overlay alignment; and
13. the browser console reported no warnings or errors.

Both `MOT17 -> KITTI -> MOT17` and `KITTI -> MOT17 -> KITTI` sequences passed. Each switch restored
frame/time to zero, cleared the selected trace, selected the correct scoped image/WAV URL and
replaced counts, suppressions, timing, metrics, session identity and nearby cue state. No stale
dataset state was observed.

### Evidence boundary and remaining gates

The browser confirms technical presentation, traceability and cross-session isolation. It does not
show that either dense cue stream is perceptually effective, interpretable, usable or accessible.
R20 remains open and controlled; the accepted WAVs and all Stage 1-3 outputs remain unchanged.

### Final local and private release gates

The release candidate passed every required local gate without an accepted skip:

- Ruff: passed;
- frontend JavaScript syntax: passed;
- final focused suite: 19 passed in 5.87s;
- complete non-integration suite: 271 passed, 6 deselected in 42.51s;
- retained Phase 1 private integration: 1 passed in 72.88s;
- retained Phase 2 MOT17 private integration: 1 passed in 43.22s; and
- new retained Phase 3 cross-dataset integration: 1 passed in 42.59s.

A fresh Python 3.14 virtual environment installed the project in editable form, exposed the primary
command help, and launched the primary release command on an alternate loopback port. Its catalogue
reported exactly two verified sessions and the declared MOT17 default. The temporary environment
was then removed from the workspace.

### Privacy and redistribution audit

The final pre-publication audit passed. The complete Phase 3 diff has no binary addition, raw MOT17
or KITTI media, generated WAV, screenshot, browser data, test artefact, username, machine-specific
absolute path or private root. No value read from the ignored local `.env` occurs in tracked
content. The retained MOT17, KITTI and catalogue declarations contain zero absolute-path markers.
Repository-wide machine-path searches resolve only to deliberate privacy-test patterns and a
synthetic example fixture. The diff touches no Stage 1-3 schema, parser, canonical output, mapping,
renderer, metric definition or canonical report path. `git diff --check` passes.

Hosted CI, PR, merge and post-merge evidence will be added only after those gates actually complete.
