# Stage 4 Milestone 1 Phase 1: Workbench Session Contract and Headless Validation

## Status

Implementation is complete on the Stage 4 Phase 1 branch and is awaiting repository quality-gate evidence before Phase 1 is closed. Browser and UI implementation remain out of scope until the headless contract passes review and CI.

## Purpose

Phase 1 freezes the Workbench Session Contract `0.1.0` and provides a headless Python validation layer for joining already verified Stage 1 event packages, Stage 2 cue/audio packages and optional Stage 3 technical-evaluation evidence into one inspection session.

The workbench layer consumes existing research artefacts. It does not redefine parsing, event normalisation, cue mapping, audio rendering or technical-evaluation semantics, and it does not introduce participant, perceptual, accessibility, usability, navigation or safety evidence.

## Implemented files

- `configs/workbench/workbench-session.schema.v0.1.0.json` defines the strict session schema.
- `docs/decisions/0016-workbench-session-and-inspection-layer.md` records the architectural boundary.
- `docs/data-model/workbench-session.md` documents deterministic identity and runtime binding fields.
- `docs/project-management/stage-4-checklist.md` records Phase 1 to Phase 3 gates.
- `src/event_sonification_workbench/workbench/session.py` implements deterministic session identity and validation.
- `src/event_sonification_workbench/workbench/__init__.py` exposes the Stage 4 session API as an installable package component.
- `tests/test_workbench_session.py` exercises valid loading, package mismatches, hash tampering, optional evaluation and path-isolation behaviour.

## Validation design

The session validator:

1. validates the session document against the frozen schema;
2. derives a content-based `session_id` from package and configuration identities only;
3. reuses the existing Stage 1 to Stage 3 verified-chain path to validate event, cue and audio packages;
4. compares the session's declared run IDs and hashes with the verified package identities;
5. validates optional Stage 3 report identity, schema and input hashes when present;
6. resolves media only through runtime roots such as `MOT17_ROOT` and `KITTI_TRACKING_ROOT`; and
7. returns path-free machine-readable diagnostics.

Runtime dataset roots, output roots, usernames, machine names, browser state and media locations do not contribute to deterministic session identity.

## Review note

`session.py` currently reuses the established verified-chain implementation through `_load_verified_chain` in `technical_evaluation_input.py`. This avoids duplicating Stage 3 integrity logic. The dependency is intentionally recorded because the function is currently private; exposing a public wrapper should be considered before the final release candidate if Stage 4 continues to depend on it.

## Quality gate

The following evidence is required before this phase is marked complete:

- `python -m ruff check .` passes;
- `python -m pytest -m "not integration"` passes without regression;
- the new workbench session tests pass in the same clean CI environment;
- session schema validation succeeds;
- no browser/UI code is present in Phase 1; and
- the final diff contains no private paths, dataset media or generated audio.

No quality result is recorded as passed until the corresponding command has actually completed successfully.

## Next phase

After the Phase 1 quality gate passes and the branch is merged, Phase 2 will implement one synchronised inspection vertical slice: validated session loading, dataset imagery, Stage 1 annotation overlays, unchanged Stage 2 WAV playback, one playback clock, event/cue/suppression timeline markers, record-level traceability and display of already verified Stage 3 metrics.
