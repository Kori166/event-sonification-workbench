# Workbench Session Contract 0.1.0

## Purpose

A workbench session records the deterministic identity of one compatible inspection chain spanning
Stage 1 event data, Stage 2 cue and audio outputs and optional Stage 3 evaluation evidence. It does
not contain raw dataset media or local absolute paths. Local paths are supplied separately when the
session is opened.

The normative schema is
`configs/workbench/workbench-session.schema.v0.1.0.json`.

## Identity boundary

Two categories of information are deliberately separated.

**Deterministic content identity** includes the dataset and sequence, package run IDs, package and
file SHA-256 values, preset and renderer identities and optional evaluation identity. These values
contribute to `session_id`.

**Runtime bindings** include `OUTPUT_ROOT`, `MOT17_ROOT`, `KITTI_TRACKING_ROOT` and an optional
repository root used to resolve a logical evaluation-report path. These values locate files on the
current machine. They do not contribute to `session_id` and are never returned in diagnostics.

## Top-level fields

| Field | Type | Meaning | Session identity |
|---|---|---|---|
| `session_version` | string | Contract version. Fixed at `0.1.0`. | Yes |
| `session_id` | string | Content-derived `session-<dataset>-<sequence>-<16 hex>` identity. | Derived |
| `dataset` | string | `mot17` or `kitti_tracking`. | Yes |
| `sequence` | string | Normalised logical sequence identifier used by the packages. | Yes |
| `event_package` | object | Stage 1 package identity and exact file hashes. | Yes |
| `cue_package` | object | Stage 2 cue-package identity, input link and exact file hashes. | Yes |
| `audio_package` | object | Stage 2 audio identity, input link and exact file hashes. | Yes |
| `evaluation` | object | Optional Stage 3 evaluation evidence. | Yes when available |
| `configuration` | object | Preset and renderer identities used by the chain. | Yes |
| `media` | object | Runtime dataset-media binding declaration. | No |

## Event package

`event_package` identifies the verified Stage 1 package.

| Field | Meaning |
|---|---|
| `run_id` | Content-derived Stage 1 run ID. |
| `package_sha256` | SHA-256 identity derived from the complete package file-hash set. |
| `format_version` | Stage 1 package format, fixed at `0.1.0`. |
| `schema_version` | Common event schema, fixed at `0.2.0`. |
| `events_sha256` | Exact SHA-256 of `events.json`. |
| `events_csv_sha256` | Exact SHA-256 of `events.csv`. |
| `run_metadata_sha256` | Exact SHA-256 of `run_metadata.json`. |
| `provenance_log_sha256` | Exact SHA-256 of `provenance_log.json`. |

The Stage 1 loader remains authoritative for canonical serialisation, metadata consistency,
validation status, deterministic ordering and the content-derived run ID.

## Cue package

`cue_package` identifies the verified Stage 2 scheduling package.

| Field | Meaning |
|---|---|
| `run_id` | Content-derived cue run ID. |
| `package_sha256` | SHA-256 identity derived from all five cue-package file hashes. |
| `format_version` | Cue-package format, fixed at `0.1.0`. |
| `input_event_run_id` | Stage 1 run ID that the session expects the cue package to consume. |
| `input_event_package_sha256` | Expected Stage 1 package identity. |
| `cue_schedule_sha256` | Exact SHA-256 of `cue_schedule.json`. |
| `cue_schedule_csv_sha256` | Exact SHA-256 of `cue_schedule.csv`. |
| `cue_log_sha256` | Exact SHA-256 of `cue_log.json`. |
| `suppression_log_sha256` | Exact SHA-256 of `suppression_log.json`. |
| `sonification_metadata_sha256` | Exact SHA-256 of `sonification_metadata.json`. |

The validator checks the declared input event identity against the independently verified Stage 1
package and the input reference recorded by Stage 2 metadata.

## Audio package

`audio_package` identifies the deterministic WAV-rendering package.

| Field | Meaning |
|---|---|
| `run_id` | Content-derived audio run ID. |
| `package_sha256` | SHA-256 identity derived from all three audio-package file hashes. |
| `renderer_version` | Renderer version, fixed at `0.1.0`. |
| `input_cue_run_id` | Expected cue-package run ID. |
| `input_cue_package_sha256` | Expected cue-package identity. |
| `cue_schedule_sha256` | Expected schedule hash carried into rendering. |
| `wav_sha256` | Exact SHA-256 of `sonification.wav`. |
| `render_log_sha256` | Exact SHA-256 of `render_log.json`. |
| `renderer_metadata_sha256` | Exact SHA-256 of `renderer_metadata.json`. |

The existing Stage 3 evidence-chain verifier is reused to check the audio package, WAV metadata,
render bounds and cross-stage event-to-cue-to-render links.

## Evaluation block

Evaluation evidence is optional.

An unevaluated session contains only:

```json
{"available": false}
```

This permits inspection of events, cues, suppressions and audio without implying that Stage 3
metrics exist for that chain.

When `available` is `true`, the block additionally records the evaluation run ID, contract version,
logical repository-relative report path, physical report SHA-256, referenced Stage 1 and Stage 2 run
IDs, package identities and the principal input file hashes used by the Stage 3 report.

The loader verifies the report against the versioned Stage 3 report schema and checks its dataset,
sequence, evaluation run ID, contract version, input hashes and non-recursive output hash. Stage 3
metrics are not recalculated by the session loader.

## Configuration block

`configuration` records:

- `preset_name`;
- `preset_version`;
- `preset_sha256`;
- `renderer_version`; and
- `renderer_sha256`.

These values must match the identities already present in the verified cue and audio packages.

## Media block

`media` declares how source imagery is located at runtime.

| Field | Meaning |
|---|---|
| `binding` | Fixed at `runtime`. |
| `root_environment` | `MOT17_ROOT` or `KITTI_TRACKING_ROOT`. |
| `relative_path` | Safe POSIX-style path beneath that root leading to the sequence media directory. |

The root value itself is never written into the session. For MOT17, the required environment name
must be `MOT17_ROOT`; for KITTI Tracking it must be `KITTI_TRACKING_ROOT`. The Phase 1 loader checks
that the resolved directory remains beneath the configured root and contains at least one regular
file. Media-byte hashing is outside contract `0.1.0`.

## Session ID

`session_id` has the form:

```text
session-<dataset>-<sequence>-<16 hexadecimal characters>
```

The suffix is the first 16 hexadecimal characters of SHA-256 over canonical JSON containing only
identity-bearing session fields. The `media` block, local roots, current playback position, browser
state, timestamps, machine names, usernames and random values are excluded.

A session file whose stored `session_id` differs from the generated value is invalid.

## Validation result

`validate_workbench_session` returns a path-free structure:

```json
{
  "valid": true,
  "session_id": "session-mot17-mot17-02-dpm-0123456789abcdef",
  "components": {
    "event_package": "verified",
    "cue_package": "verified",
    "audio_package": "verified",
    "evaluation": "verified",
    "media": "available"
  },
  "diagnostics": []
}
```

Failures use stable codes such as `cue_event_package_mismatch`,
`audio_cue_package_mismatch`, `hash_mismatch_cue_schedule`, `hash_mismatch_wav` and
`media_runtime_root_unavailable`. Diagnostics identify the component and field where useful but do
not echo private path values.
