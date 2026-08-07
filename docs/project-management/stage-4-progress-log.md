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
