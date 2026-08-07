# Stage 4 Milestone 1 Phase 1: Workbench Session Contract and Headless Validation

## Status

Phase 1 remains open. PR #28 merged the frozen Workbench Session Contract and initial headless
validator after clean CI, but before the retained Stage 2 evidence directory layout was exercised.
A post-merge review identified a bounded runtime-binding mismatch. Issue #29 and PR #30 correct that
mismatch without changing the session contract or any Stage 1 to 3 research evidence.

Corrective PR #30 now passes the repository quality gate. Browser and UI implementation remain
blocked only until one retained real MOT17 or KITTI session validates locally with its actual dataset
media through the new private integration test.

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

Issue #29 and PR #30 introduce package-specific runtime roots:

- `EVENT_PACKAGE_ROOT` for Stage 1 event-package run directories;
- `CUE_PACKAGE_ROOT` for Stage 2 cue-package run directories; and
- `AUDIO_PACKAGE_ROOT` for Stage 2 audio-package run directories.

If a package-specific root is omitted, `OUTPUT_ROOT` remains the fallback for that package type. An
explicit but invalid package-specific root is rejected rather than silently replaced by the common
fallback. Resolved package directories must remain beneath their declared runtime roots and cannot
be symlinks.

These runtime bindings do not enter `workbench-session.json`, do not affect `generate_session_id`,
and are not echoed in diagnostics.

## Corrective tests

The committed non-integration tests now cover:

- the original common `OUTPUT_ROOT` layout;
- physically separate event, cue and audio package roots;
- identical `session_id` results under common and separate package storage;
- path-free rejection of invalid explicit package roots;
- existing dataset/package mismatch, declared hash tampering, optional evaluation and media-root
  privacy cases.

A new private integration test, `tests/test_workbench_session_integration.py`, constructs retained
sessions directly from the committed Stage 3 real-data experiment manifest. It resolves package
roots beneath the existing `STAGE2_EVIDENCE_ROOT/<dataset>/run-a/{events,cues,audio}` convention and
uses whichever of `MOT17_ROOT` or `KITTI_TRACKING_ROOT` is configured. For each available dataset it
requires two identical validations, verified event/cue/audio components, available media, no
diagnostics and no private-path marker in the returned result.

## Corrective PR quality evidence

PR #30 CI run 82 completed successfully on Ubuntu 24.04 with Python 3.11.15:

- editable installation of `.[dev]`: passed;
- `ruff check .`: passed with no findings;
- `python -m pytest -m "not integration"`: 261 passed, 4 deselected;
- `tests/test_workbench_session.py`: 9 passed within the non-integration suite.

The four deselected integration tests include the new Stage 4 retained-chain test. CI does not have
private Stage 2 packages or dataset media, so that deselection is expected and is not counted as
retained-chain evidence.

## Decision boundary

Decision 0016 remains valid. Its implementation note now makes the separate package-root behaviour
explicit. No session schema field or identity-bearing value was changed, so a contract version bump
would incorrectly treat storage location as research content.

The current validator still reuses the established verified-chain implementation through
`_load_verified_chain` in `technical_evaluation_input.py`. This avoids duplicating Stage 3 integrity
logic. Exposing a public wrapper remains a possible release-hardening change if Stage 4 continues to
depend on that private function.

## Remaining acceptance actions

Before Phase 1 is closed:

1. run `python -m pytest tests/test_workbench_session_integration.py -m integration -q` from a clean
   local checkout with `STAGE2_EVIDENCE_ROOT` and at least one of `MOT17_ROOT` or
   `KITTI_TRACKING_ROOT` configured;
2. confirm at least one retained real session validates twice with the same deterministic
   `session_id`;
3. confirm event, cue and audio components report `verified`, media reports `available`, and
   diagnostics are empty; and
4. confirm the returned result and final corrective diff remain free of private absolute paths,
   usernames, datasets, WAV files and other excluded full-data derivatives.

Only after those actions are recorded as passed should Phase 1 be marked complete and Phase 2 begin.
