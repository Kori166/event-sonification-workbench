# Stage 4 Checklist

## Status

Stage 4 is active. Milestone 1 Phase 1 has frozen the workbench inspection contract and established
the headless validation layer before browser implementation begins. PR #28 CI passed after one
Ruff-only correction; retained real-chain validation from a clean local checkout remains the final
Phase 1 acceptance action before the browser vertical slice is treated as unblocked.

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
- [x] Keep `OUTPUT_ROOT`, dataset roots, usernames and machine-specific paths outside `session_id`.
- [x] Return stable path-free diagnostic codes for rejected sessions.
- [x] Add automated tests for valid loading, package mismatches, hash tampering, absent evaluation
      evidence and privacy/path isolation.
- [x] Pass `python -m ruff check .` in pull-request CI.
- [x] Pass the non-integration test suite without regressions in pull-request CI.
- [ ] Validate one retained real MOT17 or KITTI package chain and its actual dataset media from a
      clean local checkout using the frozen session contract.

### Phase 1 acceptance gate

Phase 1 is complete only when a clean checkout can validate one compatible retained package chain,
reject deliberately inconsistent or tampered session definitions, resolve local dataset media
without exposing its absolute path, reproduce the same session ID from identical evidence, and pass
the existing automated quality gates. Browser or UI code is not part of this phase.

PR #28 CI run 72 passed on Ubuntu 24.04 / Python 3.11.15 with Ruff clean and 258 non-integration
tests passed, 3 integration tests deselected. The six Stage 4 session tests passed within that suite.
This CI evidence covers committed fixtures and clean installation; it does not replace the retained
private-chain/media acceptance action above.

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
