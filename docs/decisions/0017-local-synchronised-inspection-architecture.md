# 0017: Local synchronised inspection architecture

## Status

Accepted for Stage 4 Milestone 1 Phase 2 on 7 August 2026.

## Context

Decision 0016 freezes Workbench Session Contract `0.1.0` and requires the browser layer to consume
an already validated Stage 1 to 3 evidence chain. Phase 2 needs one demonstrable MOT17 inspection
slice that joins source imagery, event geometry, cue and suppression records, exact rendered audio,
trace links and the verified Stage 3 report without creating another research pipeline.

The retained MOT17-02-DPM chain records 600 zero-based frames at 30 frames per second. Stage 1 event
timestamps are the deterministic `frame / frame_rate` relationship, Stage 2 cue start times preserve
those timestamps, and render entries record the corresponding 44.1 kHz sample bounds. The verified
WAV is slightly longer than the source-frame sequence because rendered cues have duration.

## Decision

Phase 2 uses a small authoritative Python inspection model, a standard-library localhost HTTP/media
service and package-local plain HTML, CSS and JavaScript. It adds no web framework, Node build,
database, analytics, authentication, upload or write path.

The Python model accepts a successfully validated workbench session and resolves only its already
verified package, report and runtime-media bindings. It loads immutable JSON artefacts once, builds
indexes by frame, timestamp, event ID and cue ID, and exposes bounded deterministic projections. It
does not parse native annotations, schedule cues, render audio or calculate evaluation metrics.

The service binds to loopback by default and exposes read-only routes for session summary, frame
state, bounded timeline windows, cue trace, evaluation projection, source image bytes and the exact
verified WAV. Route parameters cannot select filesystem paths. Static assets are local to the
installed Python package, errors are path-free, and the WAV route supports bounded HTTP byte ranges
without modifying the source file.

In the browser, the HTML audio element is the sole live playback clock. A `requestAnimationFrame`
loop reads `audio.currentTime` and derives the displayed frame and timeline cursor from the recorded
frame rate. Play, pause, seek and frame-step controls all operate by reading or assigning that same
`currentTime`; no independent timer or advancing frame counter is permitted. Source imagery and an
SVG overlay share the recorded image coordinate system.

The timeline requests a bounded window around the current audio time and displays existing event,
cue and suppression records in separate lanes. A cue selection requests a server-side indexed trace
projection linking cue, Stage 1 event, logical source annotation and row, preset/renderer identities,
and render entry/sample bounds. The metrics panel displays fields read directly from the already
verified Stage 3 report and labels the unavailable case without deriving substitutes.

## Rationale

This architecture keeps Python as the single authority for evidence interpretation and makes the
browser a presentation client. Standard-library serving is sufficient for one local read-only slice
and avoids dependency and build-chain expansion. Prebuilt indexes prevent full JSON reparsing or
linear rescans on every playback frame, while windowed routes bound browser work for the unusually
dense real MOT17 schedule.

Making audio time authoritative avoids drift among audio, imagery, overlays and the timeline. The
deterministic Stage 1 timestamp relationship remains the source of display frame timing; browser
animation timing is never treated as research evidence.

## Consequences

- Workbench Session Contract `0.1.0` and all Stage 1 to 3 artefact contracts remain unchanged.
- The interface is local, read-only research infrastructure and creates no participant, usability,
  accessibility, perceptual-effectiveness or safety evidence.
- Runtime package, report and media paths remain process-local state and are never serialized by the
  API or frontend.
- Browser compatibility is deliberately limited to current browsers with HTML audio, Fetch, SVG and
  `requestAnimationFrame` support.
- Phase 2 implements MOT17-02-DPM only. Cross-dataset presentation and release preparation remain
  controlled Phase 3 work.
