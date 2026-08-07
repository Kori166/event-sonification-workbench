# Stage 4 Milestone 1 Phase 1: Workbench Session Contract and Headless Validation

## Status

Phase 1 is complete. PR #28 merged the frozen Workbench Session Contract and initial headless
validator after clean CI, but before the retained Stage 2 evidence directory layout was exercised.
A post-merge review identified a bounded runtime-binding mismatch.

Issue #29 and PR #30 implemented the correction and PR #30 passed clean CI. PR #30 was then merged
before the private retained-chain acceptance gate was run. PR #31 reverted PR #30 in full, returning
`main` to the post-PR-#28 implementation. Issue #29 was reopened and PR #32 now reapplies the same
bounded runtime correction from that reverted state. PR #32 passed the repository CI gate, and both
retained real MOT17 and KITTI sessions validated locally with their actual dataset media. Browser
and UI implementation remain Phase 2 work and were not started during this close-out.

## Purpose

Phase 1 freezes Workbench Session Contract `0.1.0` and provides a headless Python validation layer
for joining already verified Stage 1 event packages, Stage 2 cue/audio packages and optional Stage 3
technical-evaluation evidence into one inspection session.

The workbench layer consumes existing research artefacts. It does not redefine parsing, event
normalisation, cue mapping, audio rendering or technical-evaluation semantics, and it does not
introduce participant, perceptual, accessibility, usability, navigation or safety evidence.

## Original PR #28 evidence

PR #28 initially failed only at Ruff. CI run 71 reported three `TRY004` findings in
`workbench/session.py`; the invalid-type branches were corrected to raise `TypeError`, and the
associated exception handling was updated. Automated tests were skipped in that failed run and are
not counted as evidence.

CI run 72 then passed on Ubuntu 24.04 with Python 3.11.15:

- editable installation of `.[dev]`: passed;
- `ruff check .`: passed with no findings;
- `python -m pytest -m "not integration"`: 258 passed, 3 deselected;
- the six original Stage 4 session tests passed within the full non-integration suite.

PR #28 merged at `de5d2646bdd3bc5811dae94a786cfabf872d1e26`. The merge records accepted contract and fixture
implementation, not completion of the private retained-chain acceptance gate.

## Post-merge mismatch found

The initial `validate_workbench_session` implementation resolved all three package run directories
as direct children of a single `OUTPUT_ROOT`:

```text
OUTPUT_ROOT/<event-run-id>
OUTPUT_ROOT/<cue-run-id>
OUTPUT_ROOT/<audio-run-id>
```

The retained Stage 2 evidence used by Stage 3 instead follows a separated layout:

```text
STAGE2_EVIDENCE_ROOT/<dataset>/run-a/events/<event-run-id>
STAGE2_EVIDENCE_ROOT/<dataset>/run-a/cues/<cue-run-id>
STAGE2_EVIDENCE_ROOT/<dataset>/run-a/audio/<audio-run-id>
```

This is a runtime storage mismatch rather than a defect in Workbench Session Contract `0.1.0`.
Package identities, hashes, run IDs and deterministic `session_id` remain independent of physical
storage location.

## Corrective implementation

Issue #29 defines package-specific runtime roots:

- `EVENT_PACKAGE_ROOT` for Stage 1 event-package run directories;
- `CUE_PACKAGE_ROOT` for Stage 2 cue-package run directories; and
- `AUDIO_PACKAGE_ROOT` for Stage 2 audio-package run directories.

If a package-specific root is omitted, `OUTPUT_ROOT` remains the fallback for that package type. An
explicit but invalid package-specific root is rejected rather than silently replaced by the common
fallback. Resolved package directories must remain beneath their declared runtime roots and cannot
be symlinks.

These runtime bindings do not enter `workbench-session.json`, do not affect `generate_session_id`,
and are not echoed in diagnostics.

PR #30 introduced this implementation. PR #31 reverted it only because the private acceptance gate
had not yet been exercised. PR #32 reapplies the same implementation; the frozen session contract,
Stage 1 to 3 package contracts and research evidence remain unchanged throughout that history.

## Corrective tests

The non-integration tests cover:

- the original common `OUTPUT_ROOT` layout;
- physically separate event, cue and audio package roots;
- identical `session_id` results under common and separate package storage;
- path-free rejection of invalid explicit package roots;
- existing dataset/package mismatch, declared hash tampering, optional evaluation and media-root
  privacy cases.

The private integration test, `tests/test_workbench_session_integration.py`, constructs retained
sessions directly from the committed Stage 3 real-data experiment manifest. It resolves package
roots beneath the existing `STAGE2_EVIDENCE_ROOT/<dataset>/run-a/{events,cues,audio}` convention and
uses whichever of `MOT17_ROOT` or `KITTI_TRACKING_ROOT` is configured. For each available dataset it
requires two identical validations, verified event/cue/audio components, available media, no
diagnostics and no private-path marker in the returned result.

## PR #30 quality evidence and revert

Final PR #30 head `bf8e242e233338ec53d7a74ddce09de74005220d` passed CI run 84 on Ubuntu 24.04 with Python
3.11.15:

- editable installation of `.[dev]`: passed;
- `ruff check .`: passed with no findings;
- `python -m pytest -m "not integration"`: 261 passed, 4 deselected;
- all 9 non-integration workbench-session tests passed.

The fourth deselected integration test was the new private retained-chain acceptance test. PR #30 was
therefore not sufficient evidence for Phase 1 completion. It was merged prematurely and then fully
reverted by PR #31. That sequence did not invalidate the implementation or its CI result; it restored
`main` until the missing private acceptance evidence could be obtained.

## Final corrective PR #32

PR #32 was opened as a draft from the post-PR-#31 `main`. It reapplies the PR #30 runtime-root
implementation and tests, then reconciles the decision, checklist, development and risk history.

PR #32 CI run 97 passed on Ubuntu 24.04 / Python 3.11.15:

- editable installation of `.[dev]`: passed;
- `ruff check .`: passed with no findings;
- `python -m pytest -m "not integration"`: 261 passed, 4 deselected;
- all 9 non-integration workbench-session tests passed.

The four deselected integration tests include the Stage 4 private retained-chain check. Hosted CI has
no access to the ignored Stage 2 package evidence or private dataset media, so this is expected and is
not treated as private acceptance evidence.

The final acceptance conditions were:

1. `python -m pytest tests/test_workbench_session_integration.py -m integration -q` passes locally
   with `STAGE2_EVIDENCE_ROOT` and at least one of `MOT17_ROOT` or `KITTI_TRACKING_ROOT` configured;
2. at least one retained real session validates twice with the same deterministic `session_id`;
3. event, cue and audio components report `verified`, media reports `available`, and diagnostics are
   empty; and
4. the returned result and final corrective diff remain free of private absolute paths, usernames,
   datasets, WAV files and other excluded full-data derivatives.

## Decision boundary

Decision 0016 remains valid. Its implementation note makes the separate package-root behaviour
explicit. No session schema field or identity-bearing value changed, so a contract version bump
would incorrectly treat storage location as research content.

The current validator still reuses the established verified-chain implementation through
`_load_verified_chain` in `technical_evaluation_input.py`. This avoids duplicating Stage 3 integrity
logic. Exposing a public wrapper remains a possible release-hardening change if Stage 4 continues to
depend on that private function.

## Final retained-chain acceptance

On 7 August 2026, the retained Stage 2 evidence was placed under a dedicated private test-evidence
root outside the repository. Both retained `run-a` chains were exercised with their corresponding
local dataset media roots.

- Command: `python -m pytest tests/test_workbench_session_integration.py -m integration -q`
- Result: `1 passed in 81.89s`.
- MOT17 session: `session-mot17-mot17-02-dpm-08569247db5a6003`.
- KITTI Tracking session: `session-kitti_tracking-0000-47c503c0c30db25a`.
- Each session validated twice with identical returned results and the same deterministic
  `session_id`.
- Both returned `event_package`, `cue_package` and `audio_package` as `verified`, `media` as
  `available`, `evaluation` as `not_available`, and `diagnostics` as an empty list.
- The returned results contained no absolute path, username, OneDrive marker or machine-specific
  location.
- `python -m ruff check .` passed locally with no findings.
- A local Windows non-integration run reported 258 passed, 3 failed and 4 deselected because the
  checkout's synthetic source fixture bytes did not match its recorded LF hash. This is not used as
  clean-checkout evidence; PR #32 CI run 97 remains the accepted pre-close-out result with 261 passed
  and 4 deselected on Ubuntu 24.04 / Python 3.11.15.
- An optional `python -m pytest -m integration` attempt exceeded the 304-second command limit and
  produced no final pytest count; it is not reported as pass evidence.
- The final diff audit found no private roots, username, machine name, absolute private path, raw
  dataset media, retained package, WAV file or browser/UI implementation.

Workbench Session Contract `0.1.0` did not change. Phase 1 is complete subject only to green CI on
the close-out commit and merge of PR #32. Phase 2 handover is to build one synchronised inspection
vertical slice over an already validated workbench session.
