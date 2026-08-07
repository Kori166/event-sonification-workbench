# Stage 4 Checklist

## Status

Stage 4 is active. Milestone 1 Phase 1 froze the workbench inspection contract and established the
headless validation layer before browser implementation begins. PR #28 merged after clean CI but
before the retained Stage 2 evidence layout was exercised. Post-merge review identified a bounded
runtime-binding mismatch: the validator assumed all package run directories shared one
`OUTPUT_ROOT`, whereas retained Stage 2 evidence stores event, cue and audio packages beneath
separate stage directories.

PR #30 implemented the correction and passed clean CI, but it was merged before the private retained-
chain acceptance gate was run. PR #31 then reverted PR #30 in full. Issue #29 has been reopened and
PR #32 reapplies the same bounded runtime correction from the reverted `main` state. Workbench
Session Contract `0.1.0` remains unchanged. Phase 1 remains open until PR #32 passes clean CI and the
retained local real-data acceptance run succeeds with actual dataset media.

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
- [ ] Pass `python -m ruff check .` on final corrective PR #32 CI.
- [ ] Pass the non-integration test suite without regressions on final corrective PR #32 CI.
- [ ] Run the retained Stage 4 integration test locally with `STAGE2_EVIDENCE_ROOT` and at least one
      configured dataset root.
- [ ] Confirm one retained real MOT17 or KITTI session validates twice with the same `session_id`,
      verified package components, available media and no path-bearing diagnostics.
- [ ] Reconcile Phase 1 records with the accepted PR #30 -> PR #31 -> PR #32 history before merge.

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
it does not substitute for fresh PR #32 CI or the private retained-chain acceptance action.

PR #32 is intentionally kept as a draft until both remaining evidence sources exist: clean CI on the
final corrective head and a local retained-chain integration pass using private Stage 2 packages and
dataset media.

### Phase 2: synchronised inspection vertical slice

- [ ] Expose one validated session through a small local inspection API.
- [ ] Display source sequence imagery using runtime media binding.
- [ ] Overlay Stage 1 event geometry without recalculating annotations.
- [ ] Play the verified Stage 2 WAV unchanged.
- [ ] Use one playback clock for media, annotation state and timeline position.
- [ ] Display Stage 1 events, Stage 2 cues and Stage 2 suppressions on the synchronised timeline.
- [ ] Resolve at least one selected cue through cue, source event, source annotation and render log.
- [ ] Display available Stage 3 metrics directly from the verified report.

### Phase 3: cross-dataset completion and release preparation

- [ ] Exercise the same session contract with MOT17 and KITTI Tracking.
- [ ] Add bounded presentation features required for the artefact demonstration.
- [ ] Verify installation and local launch from a clean environment.
- [ ] Reconcile README, project plan, progress log, risk register and release documentation.
- [ ] Build and verify a versioned release candidate without committing private datasets or generated
      private media.

## Scope boundary

Stage 4 assembles and presents existing research outputs. It does not redefine parsing, event
normalisation, cue mapping, rendering or the Stage 3 technical-evaluation contract. No participant,
accessibility, usability, navigation, perceptual-effectiveness or safety conclusion is introduced by
this stage.
