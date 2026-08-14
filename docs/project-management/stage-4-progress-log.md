# Stage 4 Progress Log

This stage-specific log records Milestone 1 contract recovery and the bounded Phase 2 inspection
candidate. The main project progress log remains the chronological project-wide record.

## 2026-08-07 - Milestone 1 Phase 1 runtime-binding recovery

**Work completed**

- Confirmed PR #28 had merged the Workbench Session Contract `0.1.0` and initial headless validator
  before the retained Stage 2 evidence layout was exercised.
- Confirmed the initial validator assumed event, cue and audio run directories were all direct
  children of one `OUTPUT_ROOT`.
- Recorded Issue #29 for compatibility with the retained
  `STAGE2_EVIDENCE_ROOT/<dataset>/run-a/{events,cues,audio}` layout.
- PR #30 implemented separate `EVENT_PACKAGE_ROOT`, `CUE_PACKAGE_ROOT` and `AUDIO_PACKAGE_ROOT`
  bindings with `OUTPUT_ROOT` fallback and added the retained-chain integration test.
- PR #30 passed clean CI on its final head but was merged before the private retained-chain
  acceptance test was run.
- PR #31 reverted PR #30 in full, restoring `main` to the post-PR-#28 state.
- Reopened Issue #29 and created fresh branch `stage-4/phase-1-runtime-bindings-final` from the
  reverted `main` state.
- Reapplied the PR #30 implementation and tests without changing Workbench Session Contract `0.1.0`
  or any Stage 1 to 3 research contract or evidence.
- Opened draft PR #32 so the final correction cannot be treated as accepted before both clean CI and
  private retained-chain validation are available.
- Reconciled Decision 0016, the Stage 4 checklist, Phase 1 development record and risk register with
  the actual PR #30 -> PR #31 -> PR #32 history.
- PR #32 CI run 94 passed on Ubuntu 24.04 / Python 3.11.15. Editable installation succeeded, Ruff
  reported no findings and the non-integration suite completed with 261 passed and 4 integration
  tests deselected. All nine Stage 4 non-integration session tests passed.

**Decisions maintained**

- Runtime package locations are environmental bindings and do not contribute to deterministic
  `session_id`.
- Package-specific roots take precedence when supplied; `OUTPUT_ROOT` remains a common-root
  fallback.
- The existing Stage 1 to 3 verified-chain logic remains authoritative for package validity.
- Browser/UI work remained outside Phase 1; Phase 2 begins with the synchronised inspection slice.

**Final acceptance state**

- The true sequence was PR #28 initial implementation -> retained runtime-layout mismatch identified
  -> PR #30 correction merged prematurely -> PR #31 full revert -> Issue #29 reopened -> PR #32
  final correction -> clean CI -> private retained-chain acceptance -> Phase 1 close-out.
- PR #32 repository CI run 97 passed on Ubuntu 24.04 / Python 3.11.15: editable installation and
  Ruff passed, and the non-integration suite reported 261 passed and 4 deselected.
- `python -m pytest tests/test_workbench_session_integration.py -m integration -q` exercised both
  retained MOT17 and KITTI Tracking `run-a` chains and reported `1 passed in 81.89s`.
- Both retained sessions validated twice identically with stable deterministic IDs. Event, cue and
  audio components were verified, media was available, evaluation was intentionally not available,
  and diagnostics were empty and path-free.
- The final scope/privacy audit found no private roots or paths, dataset media, retained packages,
  generated WAV files or Phase 2 browser/UI implementation in the branch diff.
- Phase 1 status: complete, pending only green close-out-commit CI and merge of PR #32.
- Next: Phase 2 builds one synchronised inspection vertical slice over an already validated session.

## 2026-08-07 - Milestone 1 Phase 2 implementation candidate

**Work completed**

- Opened Issue #35 and branch `stage-4/phase-2-synchronised-inspection` from clean main at
  `85c2d6abf249ebb3ebffb50b150aee8c0c099c41`.
- Recorded Decision 0017: an indexed Python inspection model, standard-library loopback HTTP/media
  service and package-local HTML/CSS/JavaScript with no production dependency addition.
- Added a validated-session opener that preserves Phase 1 path-free diagnostics while making local
  verified bindings available only inside the process.
- Added bounded session/frame/timeline/trace/evaluation/image/audio routes, safe identifier-only
  resolution, deterministic JSON and exact WAV range service.
- Added a dense dark technical frontend with source imagery, SVG event geometry, custom playback and
  frame stepping, three timeline lanes, cue trace inspection and verified Stage 3 metric cards.
- Made browser audio `currentTime` the only live playback clock; image frame and timeline cursor are
  derived from it through the recorded 30 fps relationship.
- Added the path-free real MOT17 declaration
  `session-mot17-mot17-02-dpm-3707826663b210c6` with the verified Stage 3 report available.
- Added four normal-CI inspection tests and one private real MOT17 integration test.

**Validation evidence**

- Ruff passed.
- Frontend JavaScript syntax validation passed.
- Non-integration suite: 265 passed, 5 deselected in 39.31s.
- Existing Phase 1 retained-chain integration: 1 passed in 82.15s.
- New Phase 2 real MOT17 integration: 1 passed in 45.34s.
- Draft PR #36 CI run `31204926127`: editable install and Ruff passed; 265 non-integration tests
  passed and 5 integrations were deselected on Ubuntu 24.04 / Python 3.11.15.
- The real loopback service launched and returned verified session, frame, synchronized timeline,
  trace and evaluation projections without a private runtime path.

**Acceptance boundary**

- The configured in-app browser tab could be opened, but the required browser-control interface was
  not exposed to this Codex task. Visual box alignment, live playback synchronization, control
  interactions, trace rendering, metric rendering and UI path absence could therefore not be
  evidenced under the mandatory browser workflow.
- Service/API probes are not substituted for browser evidence. Phase 2 remains incomplete, its eight
  checklist items remain unchecked, R20 remains open and controlled, and the branch must not merge.
- Next: restore browser-control capability and run and record the complete real-session browser pass
  before considering merge. Candidate privacy and hosted-CI gates pass; Phase 3 has not started.

## 2026-08-14 - Milestone 1 Phase 2 controlled browser acceptance

**Researcher-observed acceptance**

- The researcher manually completed all twelve controlled browser checks against retained real
  session `session-mot17-mot17-02-dpm-3707826663b210c6`; Codex did not perform the visual checks.
- The session, genuine source imagery, unchanged Stage 2 WAV, one-clock synchronisation, paused frame
  stepping, three timeline lanes, cue trace, Stage 3 metric projection, responsive image/overlay
  alignment, path-free privacy responses and stable failure behaviour all passed.
- The image endpoint returned HTTP 200 and JPEG bytes while a CSS presentation defect kept the
  loading overlay visible. The existing JavaScript correctly set `hidden`; adding
  `.viewer-loading[hidden] { display: none; }` restored the expected presentation. A deterministic
  static-asset test now covers that contract.
- Console scans of session, frame, evaluation, timeline and real-cue trace JSON found no private
  runtime path, username or OneDrive root. No screenshot containing MOT17 imagery was committed.
- Extreme 20-50% zoom produced cosmetic background-gradient artefacts only. Informal inspection also
  found the dense overlapping cue stream difficult to interpret; neither observation changes the
  accepted evidence or constitutes participant/perceptual evaluation.
- All eight Phase 2 checklist items are supported. R20 remains open and controlled because browser
  acceptance establishes engineering presentation/synchronisation only, not usability,
  accessibility or perceptual effectiveness.
- Final local close-out gates passed: Ruff clean; frontend JavaScript syntax valid; 266 passed and 5
  deselected in the non-integration suite; Phase 1 private integration 1 passed in 83.56s; Phase 2
  private integration 1 passed in 34.93s.
- Final-head hosted CI run 105 passed with installation, Ruff and 266 non-integration tests / 5
  deselected on Ubuntu 24.04 / Python 3.11.15.
- PR #36 merged as `f9a3101f4eaef65b55d2efbdc1d8b0beaad489ec`; Issue #35 auto-closed as
  completed with all 17 acceptance criteria checked.
- Stage 4 Milestone 1 Phase 2 is complete. Stage 4 remains active; Phase 3 cross-dataset completion
  and release preparation is next and has not started.

## 2026-08-14 - Milestone 1 Phase 3 cross-dataset candidate

- Opened Issue #37 and branch `stage-4/phase-3-cross-dataset-release` from clean main
  `16e20e811d4ed654fe60e36f2769b9884ad871ae`.
- Decision 0018 retains Workbench Session Contract `0.1.0` and freezes a two-entry path-free
  catalogue over immutable validated inspection models.
- Added retained KITTI session `session-kitti_tracking-0000-9cae092175c68109`, scoped service/media
  lookup and a minimal browser selector with generation-based state isolation.
- Final local checks passed: Ruff, frontend syntax, 19 focused tests and 271 non-integration tests
  with 6 integration tests deselected. Phase 1 (`1 passed in 72.88s`), Phase 2 MOT17
  (`1 passed in 43.22s`) and Phase 3 cross-dataset (`1 passed in 42.59s`) private gates passed.
- A clean Python 3.14 environment installed and launched the primary release command; the catalogue
  reported exactly the two verified retained sessions and the declared MOT17 default.
- The Phase 3 privacy/redistribution audit passed: no private path/value, raw media, generated WAV,
  screenshot, browser/test artefact or Stage 1-3 canonical change occurs in the release diff.
- Codex completed 13/13 controlled KITTI browser checks and both switching sequences. Genuine KITTI
  imagery and recorded boxes aligned; playback, one-clock timing, frame stepping, lanes, real trace,
  direct report metrics, privacy, stable failures and responsive alignment passed. No screenshot or
  browser artefact was saved or committed.
- R20 remains open: this is browser/technical acceptance, not perceptual, participant, usability or
  accessibility evidence.
- Final-head CI run 31817924213 passed on
  `7b27481241b9a97c0b67a4b402d49ac50df57d1e`, then reviewed PR #38 merged as release-candidate
  `3c23a6b518fd33b1542145da06ab1939c7d676dc` and Issue #37 closed.
- Post-merge `main` CI run 31818140887 passed with clean install, Ruff and 271 tests / 6 deselected
  on Ubuntu 24.04 / Python 3.11.15. Phase 3 and Stage 4 Milestone 1 are complete; Stage 4 remains
  active.
