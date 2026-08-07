# Stage 4 Checklist

## Status

Stage 4 is active. Milestone 1 Phase 1 freezes the workbench inspection contract and establishes the
headless validation layer before browser implementation begins.

## Milestone 1: versioned artefact release candidate

### Phase 1: workbench contract and headless validation

- [ ] Freeze Workbench Session Contract `0.1.0` under a strict JSON Schema.
- [ ] Record the inspection-layer architecture and evidence boundary in Decision 0016.
- [ ] Document deterministic session fields separately from runtime environmental bindings.
- [ ] Generate `session_id` deterministically from canonical identity fields only.
- [ ] Reuse existing Stage 1 to 3 package loaders and evidence-chain verification rather than
      implementing weaker Stage 4 validation rules.
- [ ] Reject mismatched Stage 1 event and Stage 2 cue-package identities.
- [ ] Reject mismatched Stage 2 cue and audio-package identities.
- [ ] Reject declared file hashes that differ from verified package files.
- [ ] Validate an available Stage 3 report against its schema, identity and recorded input hashes.
- [ ] Permit `evaluation.available = false` without calculating substitute metrics.
- [ ] Resolve MOT17 media only beneath `MOT17_ROOT` and KITTI Tracking media only beneath
      `KITTI_TRACKING_ROOT`.
- [ ] Keep `OUTPUT_ROOT`, dataset roots, usernames and machine-specific paths outside `session_id`.
- [ ] Return stable path-free diagnostic codes for rejected sessions.
- [ ] Add automated tests for valid loading, package mismatches, hash tampering, absent evaluation
      evidence and privacy/path isolation.
- [ ] Pass `python -m ruff check .`.
- [ ] Pass the non-integration test suite without regressions.

### Phase 1 acceptance gate

Phase 1 is complete only when a clean checkout can validate one compatible retained package chain,
reject deliberately inconsistent or tampered session definitions, resolve local dataset media
without exposing its absolute path, reproduce the same session ID from identical evidence, and pass
the existing automated quality gates. Browser or UI code is not part of this phase.

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
