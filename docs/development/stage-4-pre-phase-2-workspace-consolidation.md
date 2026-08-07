# Stage 4 pre-Phase-2 workspace consolidation

## Status

Completed on 7 August 2026 before Stage 4 Milestone 1 Phase 2. This was a filesystem and readiness
audit only; it introduced no inspection API, server, player, timeline or browser implementation.

## Inventory and classification

The complete legacy workspace, including hidden and ignored content, was inventoried before any
deletion:

- 25,928 files and 2,946 directories;
- 1,013,273,794 bytes;
- SHA-256 calculated for all 25,928 files with zero read/hash errors;
- repository material, private data, retained evidence, generated outputs, working documents,
  disposable development artefacts and ambiguous items classified separately.

The legacy Git checkout had unrelated pre-rebuild history and could not be merged safely into the
current repository. Its source, notebooks, tests and Git object database were retained as a private
historical archive rather than copied into current `main`. No unique legacy file was judged suitable
for restoration into the current source tree.

## Migration result

- 5,575 retained files totalling 553,560,437 bytes remain in canonical private evidence, generated-
  output and archive locations after cache cleanup.
- Eight standalone Stage 1 package files totalling 82,057,577 bytes were removed only after every
  filename, size and SHA-256 value matched the corresponding canonical retained package.
- 20,345 reproducible dependency, environment, bytecode, package-metadata and tool-cache files
  totalling 377,655,780 bytes were removed after the complete private inventory was written.
- No unresolved file remains in the legacy workspace. The legacy root contains zero items; final
  removal of that empty directory was deferred because the active desktop task held it open.
- A detailed local-only JSON migration manifest records per-file source, destination, size,
  timestamp, hash, category and decision. It remains outside Git.

The retained Stage 2 evidence was not regenerated or modified. All 48 manifest-declared package
files across MOT17 and KITTI Tracking `run-a` and `run-b` matched the committed SHA-256 values. The
verified evidence total remains 48 files and 295,700,402 bytes.

## Runtime and quality verification

The ignored local runtime configuration resolves:

- `MOT17_ROOT`;
- `KITTI_TRACKING_ROOT`; and
- `STAGE2_EVIDENCE_ROOT`.

Actual values remain private and are not recorded here. `.env.example` remains path-free.

Post-migration checks:

- `python -m ruff check .`: passed;
- `python -m pytest -m "not integration"`: 261 passed, 4 deselected;
- `python -m pytest tests/test_workbench_session_integration.py -m integration -q`: 1 passed;
- both retained sessions executed rather than skipped and continued to verify deterministic repeat
  results, event/cue/audio packages, media availability and empty path-free diagnostics.

## Phase 2 dependency map

| Phase 2 input | Canonical location class | Runtime or repository binding | Validation source |
|---|---|---|---|
| MOT17 sequence imagery | Private `Data` hierarchy | `MOT17_ROOT` | Workbench media binding |
| KITTI Tracking sequence imagery | Private `Data` hierarchy | `KITTI_TRACKING_ROOT` | Workbench media binding |
| Stage 1 event packages and provenance | Retained Stage 2 evidence hierarchy | `EVENT_PACKAGE_ROOT` derived from `STAGE2_EVIDENCE_ROOT` | Verified-chain session validation |
| Stage 2 cue schedules, cue logs and suppression logs | Retained Stage 2 evidence hierarchy | `CUE_PACKAGE_ROOT` derived from `STAGE2_EVIDENCE_ROOT` | Verified-chain session validation |
| Stage 2 WAV, render log and renderer metadata | Retained Stage 2 evidence hierarchy | `AUDIO_PACKAGE_ROOT` derived from `STAGE2_EVIDENCE_ROOT` | Verified-chain session validation |
| Preset, renderer and schema identities | Repository `configs` hierarchy | Logical repository paths | Schema and recorded SHA-256 validation |
| Stage 3 technical-evaluation reports | Repository evaluation-evidence hierarchy | Logical repository paths | Evaluation schema/hash validation |

## Boundary and conclusion

The repository privacy audit found no dataset media, native annotations, retained package chain,
generated WAV, private environment value or large local output in the proposed change. Workbench
Session Contract `0.1.0` and all Stage 1-3 contracts, metrics and research results remain unchanged.

The local filesystem and verified evidence dependencies are ready for the Phase 2 synchronised
inspection vertical slice over an already validated workbench session.
