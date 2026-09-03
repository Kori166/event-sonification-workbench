# Stage 4 Checklist

## Milestone 1: Build the Inspection Workbench

### Phase 1: Define and Validate Workbench Sessions

- [x] Defined Workbench Session Contract `0.1.0` using a strict JSON Schema.
- [x] Recorded the inspection architecture and evidence boundary in Decision 0016.
- [x] Kept deterministic session identity separate from local runtime paths.
- [x] Generated `session_id` only from deterministic evidence fields.
- [x] Reused the existing Stage 1 to 3 validation logic rather than creating weaker Stage 4 checks.
- [x] Checked that event, cue and audio package identities agree across stages.
- [x] Checked declared file hashes against the retained package files.
- [x] Validated available Stage 3 evaluation reports against their schema and recorded evidence.
- [x] Allowed sessions without evaluation evidence without creating replacement metrics.
- [x] Restricted MOT17 and KITTI media access to their configured dataset roots.
- [x] Kept local package paths, dataset roots and usernames outside the deterministic session identity.
- [x] Returned stable diagnostics without exposing private machine paths.
- [x] Added separate runtime roots for event, cue and audio packages.
- [x] Kept `OUTPUT_ROOT` as a fallback for simpler fixture layouts.
- [x] Confirmed separate and shared package layouts produce the same deterministic session identity.
- [x] Added tests for invalid package roots and path isolation.
- [x] Added private integration coverage using the retained Stage 2 evidence layout.
- [x] Confirmed Ruff and the full test suite excluding private integration tests passed.
- [x] Validated both retained MOT17 and KITTI sessions twice with identical session IDs.
- [x] Confirmed event, cue and audio packages were verified and required media was available.
- [x] Confirmed validation diagnostics remained empty and contained no private paths.

### Runtime Binding Correction

Initial validation assumed that event, cue and audio packages shared one `OUTPUT_ROOT`. The retained evidence instead stored these package types in separate stage directories.

PR #30 introduced separate package roots and passed CI, but it was merged before the required private evidence check. PR #31 therefore reverted it. Issue #29 was reopened and PR #32 reapplied the same correction after the retained evidence layout had been checked.

The correction did not change Workbench Session Contract `0.1.0` or any retained Stage 1 to 3 research evidence.

### Phase 2: Build the Inspection Interface

- [x] Exposed validated retained sessions through a small local inspection service.
- [x] Displayed source imagery using runtime dataset bindings.
- [x] Displayed retained Stage 1 bounding boxes without recalculating annotations.
- [x] Played the verified Stage 2 WAV without modification.
- [x] Used the audio playback time as the single synchronisation clock.
- [x] Displayed events, cues and suppressions on a synchronised timeline.
- [x] Allowed selected cues to be traced back to their event, source annotation and rendered sample range.
- [x] Displayed Stage 3 technical metrics directly from the retained evaluation report.
- [x] Corrected a browser loading overlay problem found during researcher inspection.
- [x] Added a regression test for the loading overlay correction.
- [x] Completed the controlled browser acceptance checks.
- [x] Confirmed final local tests, private integrations, privacy checks and hosted CI passed.

The browser checks were engineering acceptance tests. They were not participant, usability, accessibility or perceptual evaluations.

### Phase 3: Add Both Dataset Cases

- [x] Recorded the Phase 3 scope and architecture in Decision 0018.
- [x] Kept Workbench Session Contract `0.1.0` unchanged.
- [x] Added a retained KITTI Tracking session alongside the existing MOT17 session.
- [x] Limited the catalogue to the two retained evaluation cases.
- [x] Used the same validation, service and browser architecture for both datasets.
- [x] Kept all Stage 1 to 3 contracts, evaluation results and WAV files unchanged.
- [x] Reset dataset specific browser state when switching sessions.
- [x] Added tests covering catalogue behaviour, routing, session switching and frontend reset.
- [x] Passed the existing retained evidence integrations and the new KITTI checks.
- [x] Completed controlled KITTI and cross session browser checks.
- [x] Verified the main release launch process.
- [x] Confirmed configuration failures remain free from private path information.
- [x] Updated the README and supporting project records.
- [x] Passed the privacy, redistribution and hosted CI checks.
- [x] Merged the release candidate through PR #38.

Milestone 1 was complete after both retained datasets could be inspected through the same validated workbench architecture.

## Milestone 2: Refine and Finalise the Workbench

Final researcher inspection identified several presentation and interaction problems that did not change the underlying research evidence. These were corrected before release.

- [x] Recorded the correction scope in Decision 0019.
- [x] Corrected timeline behaviour at the beginning and end of retained sessions.
- [x] Aligned selected cue time, source frame and provenance display.
- [x] Documented and tested the frame timing rules.
- [x] Displayed stable retained Stage 2 outcomes for events on the current frame.
- [x] Made EVENT, CUE and SUPPRESS terminology consistent across the interface.
- [x] Limited direct timeline selection to cue markers.
- [x] Added complete cue controls for the displayed frame.
- [x] Displayed the selected cue's technical mapping parameters.
- [x] Documented the limitation of using bounding box area as an apparent scale input.
- [x] Recorded researcher acceptance problems without treating them as participant findings.
- [x] Improved dense timeline performance through caching.
- [x] Limited source frame processing to frame changes and explicit inspection.
- [x] Added bounded frame preloading.
- [x] Made cue ordering deterministic by time, track and cue ID.
- [x] Treated unresolved evidence as an integrity problem rather than a normal outcome.
- [x] Removed the fixed limit that previously displayed only the first ten cues on a frame.
- [x] Confirmed complete cue controls for frames containing zero, one or many cues.
- [x] Checked the final retained frames for both MOT17 and KITTI.
- [x] Simplified timeline help and removed redundant interface text.
- [x] Corrected the displayed time after cue selection, seeking and frame stepping.
- [x] Made represented video bounding boxes select their exact retained cue.
- [x] Kept suppressed and anomalous boxes as contextual information rather than playable cues.
- [x] Added keyboard interaction for represented video boxes.
- [x] Passed the final 16 browser checks in Firefox and Chrome for both datasets.
- [x] Passed the final privacy and frozen research scope checks.
- [x] Passed final hosted CI and post merge `main` CI.
- [x] Merged Milestone 2 through PR #40.

## Stage 4 Completion

Stage 4 completed the inspection artefact without changing the research outputs generated during Stages 1 to 3.

The final workbench can:
- inspect retained MOT17 and KITTI Tracking sessions
- display source frames and recorded bounding boxes
- play the retained generated WAV
- show synchronised event, cue and suppression records
- trace cues and suppressions back to their source events
- display retained technical evaluation results
- switch between the two retained dataset cases
- verify the evidence chain before displaying a session
