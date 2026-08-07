# Stage 4 Milestone 1 Phase 1: Workbench Session Contract and Headless Validation

## Status

The committed Phase 1 implementation and repository CI quality gates pass. One retained real
MOT17 or KITTI package chain still needs to be validated with its actual local dataset media from a
clean checkout before Phase 1 is closed and browser implementation is treated as unblocked.

## Purpose

Phase 1 freezes the Workbench Session Contract `0.1.0` and provides a headless Python validation
layer for joining already verified Stage 1 event packages, Stage 2 cue/audio packages and optional
Stage 3 technical-evaluation evidence into one inspection session.

The workbench layer consumes existing research artefacts. It does not redefine parsing, event
normalisation, cue mapping, audio rendering or technical-evaluation semantics, and it does not
introduce participant, perceptual, accessibility, usability, navigation or safety evidence.

## Implemented files

- `configs/workbench/workbench-session.schema.v0.1.0.json` defines the strict session schema.
- `docs/decisions/0016-workbench-session-and-inspection-layer.md` records the architectural boundary.
- `docs/data-model/workbench-session.md` documents deterministic identity and runtime binding fields.
- `docs/project-management/stage-4-checklist.md` records Phase 1 to Phase 3 gates.
- `src/event_sonification_workbench/workbench/session.py` implements deterministic session identity
  and validation.
- `src/event_sonification_workbench/workbench/__init__.py` exposes the Stage 4 session API as an
  installable package component.
- `tests/test_workbench_session.py` exercises valid loading, package mismatches, hash tampering,
  optional evaluation and path-isolation behaviour.

## Validation design

The session validator:

1. validates the session document against the frozen schema;
2. derives a content-based `session_id` from package and configuration identities only;
3. reuses the existing Stage 1 to Stage 3 verified-chain path to validate event, cue and audio
   packages;
4. compares the session's declared run IDs and hashes with the verified package identities;
5. validates optional Stage 3 report identity, schema and input hashes when present;
6. resolves media only through runtime roots such as `MOT17_ROOT` and `KITTI_TRACKING_ROOT`; and
7. returns path-free machine-readable diagnostics.

Runtime dataset roots, output roots, usernames, machine names, browser state and media locations do
not contribute to deterministic session identity.

## Review note

`session.py` currently reuses the established verified-chain implementation through
`_load_verified_chain` in `technical_evaluation_input.py`. This avoids duplicating Stage 3 integrity
logic. The dependency is intentionally recorded because the function is currently private;
exposing a public wrapper should be considered before the final release candidate if Stage 4
continues to depend on it.

## Pull-request quality evidence

PR #28 initially failed only at Ruff. CI run 71 reported three `TRY004` findings in
`workbench/session.py`; the invalid-type branches were corrected to raise `TypeError`, and the
associated exception handling was updated. Automated tests were skipped in that failed run and are
not counted as evidence.

CI run 72 then passed on Ubuntu 24.04 with Python 3.11.15:

- editable installation of `.[dev]`: passed;
- `ruff check .`: passed with no findings;
- `python -m pytest -m "not integration"`: 258 passed, 3 deselected;
- `tests/test_workbench_session.py`: 6 passed within the full non-integration suite.

The successful CI checkout also confirms that the new `workbench` package is included by the
editable installation. No private dataset roots, retained Stage 2 package chains or local media are
available in CI, so this evidence does not satisfy the final retained real-chain acceptance action.

## Remaining Phase 1 acceptance action

From a clean local checkout with the retained evidence and one configured dataset root:

- construct a `workbench-session.json` for either the recorded MOT17-02-DPM or KITTI Tracking 0000
  Stage 1/2 chain;
- validate the session against the frozen contract;
- confirm the package identities and declared hashes resolve exactly;
- resolve the actual local sequence media beneath the configured runtime root;
- repeat validation and confirm the same `session_id` is produced; and
- confirm returned diagnostics and any exported session representation remain free of absolute
  local paths, usernames and machine-specific state.

No browser/UI code should be introduced before this action is recorded as passed.

## Next phase

After the remaining Phase 1 acceptance action passes and PR #28 is merged, Phase 2 will implement
one synchronised inspection vertical slice: validated session loading, dataset imagery, Stage 1
annotation overlays, unchanged Stage 2 WAV playback, one playback clock, event/cue/suppression
timeline markers, record-level traceability and display of already verified Stage 3 metrics.
