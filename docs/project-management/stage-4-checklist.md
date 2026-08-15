# Stage 4 Checklist

## Status

Stage 4 is active. Milestone 1 Phase 1 froze the workbench inspection contract and established the
headless validation layer before browser implementation begins. PR #28 merged after clean CI but
before the retained Stage 2 evidence layout was exercised. Post-merge review identified a bounded
runtime-binding mismatch: the validator assumed all package run directories shared one
`OUTPUT_ROOT`, whereas retained Stage 2 evidence stores event, cue and audio packages beneath
separate stage directories.

PR #30 implemented the correction and passed clean CI, but it was merged before the private retained-
chain acceptance gate was run. PR #31 then reverted PR #30 in full. Issue #29 was reopened and PR
#32 reapplied the same bounded runtime correction from the reverted `main` state. Workbench Session
Contract `0.1.0` remains unchanged. PR #32 passed its repository CI gate, and the retained local
real-data acceptance run then passed for both MOT17 and KITTI Tracking. Milestone 1 Phase 1 is
complete. The Phase 2 implementation and researcher-performed controlled browser acceptance now
support all eight acceptance items. Final local/private gates, the privacy/scope audit and hosted CI
run 105 passed; PR #36 merged and Issue #35 closed. Stage 4 Milestone 1 Phase 2 is complete; Phase 3
is next and has not begun.

## Milestone 1: versioned artefact release candidate

### Phase 1: workbench contract and headless validation

- [x] Freeze Workbench Session Contract `0.1.0` under a strict JSON Schema.
- [x] Record the inspection-layer architecture and evidence boundary in Decision 0016.
- [x] Document deterministic session fields separately from runtime environmental bindings.
- [x] Generate `session_id` deterministically from canonical identity fields only.
- [x] Reuse existing Stage 1 to 3 package loaders and evidence-chain verification rather than
      implementing weaker Stage 4 validation rules.
- [x] Reject mismatched Stage 1 event and Stage 2 cue-package identities.
- [x] Reject mismatched Stage 2 cue and audio-package identities.
- [x] Reject declared file hashes that differ from verified package files.
- [x] Validate an available Stage 3 report against its schema, identity and recorded input hashes.
- [x] Permit `evaluation.available = false` without calculating substitute metrics.
- [x] Resolve MOT17 media only beneath `MOT17_ROOT` and KITTI Tracking media only beneath
      `KITTI_TRACKING_ROOT`.
- [x] Keep package roots, dataset roots, usernames and machine-specific paths outside `session_id`.
- [x] Return stable path-free diagnostic codes for rejected sessions.
- [x] Support separate `EVENT_PACKAGE_ROOT`, `CUE_PACKAGE_ROOT` and `AUDIO_PACKAGE_ROOT` runtime
      bindings for retained evidence layouts.
- [x] Retain `OUTPUT_ROOT` as a common-root fallback for compact fixture/output layouts.
- [x] Add automated tests proving separate and common-root package layouts preserve the same
      deterministic session identity.
- [x] Add path-isolation coverage for invalid explicit package roots.
- [x] Add a private integration test aligned with the retained `STAGE2_EVIDENCE_ROOT` layout.
- [x] Pass `python -m ruff check .` on final corrective PR #32 CI.
- [x] Pass the non-integration test suite without regressions on final corrective PR #32 CI.
- [x] Run the retained Stage 4 integration test locally with `STAGE2_EVIDENCE_ROOT` and at least one
      configured dataset root.
- [x] Confirm one retained real MOT17 or KITTI session validates twice with the same `session_id`,
      verified package components, available media and no path-bearing diagnostics.
- [x] Reconcile Phase 1 records with the accepted PR #30 -> PR #31 -> PR #32 history before merge.

### Phase 1 acceptance gate

Phase 1 is complete only when a clean checkout can validate one compatible retained package chain,
reject deliberately inconsistent or tampered session definitions, resolve local dataset media
without exposing its absolute path, reproduce the same session ID from identical evidence, and pass
the existing automated quality gates. Browser or UI code is not part of this phase.

PR #28 CI run 72 passed on Ubuntu 24.04 / Python 3.11.15 with Ruff clean and 258 non-integration
tests passed, 3 integration tests deselected. That evidence remains valid for the original contract
and fixture validation, but it did not exercise the retained Stage 2 package-directory layout.

PR #30 later passed clean CI with Ruff and 261 non-integration tests, including all nine Stage 4
non-integration session tests, but that PR was reverted by PR #31 because the private retained-chain
gate had not yet been run. Its CI evidence demonstrates the correction was test-clean at that head;
it does not substitute for the private retained-chain acceptance action.

PR #32 CI run 97 passed on Ubuntu 24.04 / Python 3.11.15. Editable installation succeeded, Ruff
reported no findings and `python -m pytest -m "not integration"` completed with 261 passed and 4
integration tests deselected. All nine Stage 4 non-integration session tests passed. The additional
deselected Stage 4 integration test is deliberately private and was exercised locally on 7 August
2026 with both retained datasets: `1 passed in 81.89s`. Both sessions validated twice identically,
all event/cue/audio components were verified, media was available and diagnostics were empty and
path-free. Phase 1 is complete; PR #32 still requires green CI on the close-out records before merge.

### Phase 2: synchronised inspection vertical slice

- [x] Expose one validated session through a small local inspection API.
- [x] Display source sequence imagery using runtime media binding.
- [x] Overlay Stage 1 event geometry without recalculating annotations.
- [x] Play the verified Stage 2 WAV unchanged.
- [x] Use one playback clock for media, annotation state and timeline position.
- [x] Display Stage 1 events, Stage 2 cues and Stage 2 suppressions on the synchronised timeline.
- [x] Resolve at least one selected cue through cue, source event, source annotation and render log.
- [x] Display available Stage 3 metrics directly from the verified report.

### Phase 2 acceptance state

Issue #35 and Decision 0017 define the slice. The researcher manually completed all twelve browser
checks against `session-mot17-mot17-02-dpm-3707826663b210c6`. Source imagery rendered after the
targeted `.viewer-loading[hidden] { display: none; }` correction; geometry, unchanged WAV playback,
the single audio clock, frame stepping, timeline, trace, metrics, responsive alignment, privacy and
path-free failures passed. A CSS asset contract test covers the loading-overlay regression. These
checks are engineering/browser acceptance, not participant, perceptual, usability or accessibility
evidence. Final-head CI run 105 passed with 266 tests and 5 deselected, and PR #36 merged as
`f9a3101f4eaef65b55d2efbdc1d8b0beaad489ec`.

Final local close-out gates on Windows / Python 3.14.3 passed: Ruff clean, frontend JavaScript syntax
valid, 266 non-integration tests passed with 5 integrations deselected, the Phase 1 retained-chain
integration passed once in 83.56s and the Phase 2 real-session integration passed once in 34.93s.

**Stage 4 Milestone 1 Phases 1-2 complete; Phase 3 close-out recorded below.**

### Phase 3: cross-dataset completion and release preparation

- [x] Freeze the Phase 3 architecture and scope in Decision 0018.
- [x] Retain Workbench Session Contract `0.1.0` unchanged.
- [x] Declare one path-free retained real KITTI Tracking session.
- [x] Expose only the retained MOT17 and KITTI sessions through bounded catalogue/lookup behaviour.
- [x] Use the same validated-session, inspection-model, loopback-service and browser-client path for
      both dataset families.
- [x] Preserve Stage 1-3 contracts, canonical results and exact retained WAV bytes unchanged.
- [x] Reset all dataset-dependent browser state when session selection changes.
- [x] Add focused catalogue, routing, frontend-reset and cross-dataset automated tests.
- [x] Pass existing Phase 1 and Phase 2 private integrations plus a new KITTI/cross-dataset gate.
- [x] Complete controlled KITTI and cross-session browser acceptance.
- [x] Verify the primary release launch and path-free configuration failures.
- [x] Reconcile README, launch/evidence documentation, project plan, progress log and risk register.
- [x] Pass the Phase 3 privacy/redistribution audit and final-head hosted CI.
- [x] Merge the focused PR, close Issue #37 and pass post-merge `main` CI.
- [x] Record release-candidate merge `3c23a6b518fd33b1542145da06ab1939c7d676dc` and mark Stage 4
      Milestone 1 complete.

**Stage 4 Milestone 1 complete; Stage 4 remains active.**

### Milestone 2: inspection corrections and final release refinement

- [x] Audit clean `main` and record starting SHA `799c5ef95d42040d05c2b7d7a757ec765b6d382c`.
- [x] Characterise the boundary provenance defect and verify retained backend traces.
- [x] Freeze the correction architecture and research boundary in Decision 0019.
- [x] Stabilise clamped start/end timeline windows and boundary cue controls.
- [x] Align selected cue time, source frame and provenance without changing timestamps.
- [x] Document/test half-open frame timing and display frame structure distinctly from the cursor.
- [x] Project stable retained Stage 2 outcomes for source-frame events.
- [x] Reconcile overlay and EVENT/CUE/SUPPRESS terminology.
- [x] Make only cue markers selectable and label evidence-window cues explicitly.
- [x] Expose selected-cue technical parameters and the technical baseline mapping accurately.
- [x] Record the bounding-box-area limitation and retain R20 without redesigning audio.
- [x] Record the failed first researcher acceptance without treating it as perceptual evidence.
- [x] Profile playback work and cache dense static timeline drawing outside the display-rate path.
- [x] Restrict source-frame work to frame transitions/explicit inspection and bound preloading.
- [x] Make cue controls deterministic by time, track and cue ID without selection reordering.
- [x] Present unresolved evidence as an integrity anomaly, not a normal Stage 2 category.
- [x] Pass focused, complete-suite and all retained private integration gates.
- [ ] Pass revised 22-check Firefox/Chrome, two-dataset browser acceptance.
- [x] Pass the Milestone 2 privacy and frozen-research-scope audit.
- [ ] Pass final-head hosted CI.
- [ ] Merge the focused PR and pass post-merge `main` CI.
- [ ] Record the exact Milestone 2 close-out SHA and mark Milestone 2 complete.

## Scope boundary

Stage 4 assembles and presents existing research outputs. It does not redefine parsing, event
normalisation, cue mapping, rendering or the Stage 3 technical-evaluation contract. No participant,
accessibility, usability, navigation, perceptual-effectiveness or safety conclusion is introduced by
this stage.
