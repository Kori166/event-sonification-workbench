# Stage 4 Progress Log

This stage-specific log records the recovery of Milestone 1 Phase 1 after the runtime package-layout
mismatch and the premature merge/revert sequence. The main project progress log remains the
chronological project-wide record and should be reconciled with this entry when Phase 1 closes.

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
- Browser/UI work remains blocked until Phase 1 acceptance is complete.

**Current acceptance state**

- PR #32 repository CI: passed on run 94 for the corrective implementation and reconciled records.
- Private retained-chain integration: pending because it requires local retained Stage 2 packages
  and at least one configured dataset media root.
- Phase 1 status: open.

**Required close-out evidence**

1. `python -m pytest tests/test_workbench_session_integration.py -m integration -q` passes locally
   with `STAGE2_EVIDENCE_ROOT` and at least one of `MOT17_ROOT` or `KITTI_TRACKING_ROOT`.
2. The retained session validates twice with the same deterministic `session_id`.
3. Event, cue and audio components report `verified`, media reports `available`, and diagnostics are
   empty and path-free.
4. The final accepted records are reconciled before merge and Phase 2 begins.
