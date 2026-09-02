# Workbench Session Contract 0.1.0

## Purpose

A workbench session identifies one retained inspection chain spanning Stage 1 events, Stage 2 cue/suppression and audio outputs, and optional Stage 3 technical evaluation evidence.

The session is a read-only inspection contract. It does not contain raw dataset media, regenerate research outputs or store machine-specific absolute paths.

The normative schema is:

```text
configs/workbench/workbench-session.schema.v0.1.0.json
```

## Identity And Runtime Bindings

The contract separates deterministic content identity from local runtime locations.

Deterministic identity includes:

- dataset and sequence;
- Stage 1 event-package identity and hashes;
- Stage 2 cue-package identity and hashes;
- Stage 2 audio-package identity and hashes;
- preset and renderer identity;
- optional Stage 3 evaluation identity.

These values contribute to the content-derived `session_id`.

Runtime bindings locate the retained packages and dataset media on the current machine. They do not contribute to `session_id` and are not exposed as provenance values. Supported bindings include:

- `EVENT_PACKAGE_ROOT`;
- `CUE_PACKAGE_ROOT`;
- `AUDIO_PACKAGE_ROOT`;
- `OUTPUT_ROOT` as a shared fallback;
- `MOT17_ROOT`;
- `KITTI_TRACKING_ROOT`;
- `REPOSITORY_ROOT` for repository-held evaluation evidence.

Package-specific roots take precedence over `OUTPUT_ROOT` when supplied.

## Top-Level Structure

| Field | Purpose |
|---|---|
| `session_version` | Identifies the session contract version. |
| `session_id` | Content-derived retained-session identifier. |
| `dataset` | Identifies `mot17` or `kitti_tracking`. |
| `sequence` | Identifies the retained sequence. |
| `event_package` | Declares the Stage 1 package identity. |
| `cue_package` | Declares the Stage 2 cue/suppression package identity. |
| `audio_package` | Declares the Stage 2 rendered-audio package identity. |
| `evaluation` | Declares optional Stage 3 technical evaluation evidence. |
| `configuration` | Declares preset and renderer identity. |
| `media` | Declares runtime media requirements without storing local paths. |

## Stage 1 Event Package

The event-package block records the retained Stage 1 run identifier, package identity, schema version and exact hashes for:

- `events.json`;
- `events.csv`;
- `run_metadata.json`;
- `provenance_log.json`.

The Stage 1 loader remains responsible for validating canonical serialisation, event ordering, package metadata, source provenance and the content-derived run identifier.

## Stage 2 Cue And Suppression Package

The cue-package block records:

- cue run identifier and package identity;
- the Stage 1 input package identity it expects;
- cue schedule hashes;
- cue-log hash;
- suppression-log hash;
- sonification-metadata hash.

The session validator checks that the declared Stage 1 identity matches the input identity recorded by Stage 2.

This preserves the explicit event-outcome relationship:

```text
valid event
→ cue
or
→ suppression
```

## Stage 2 Audio Package

The audio-package block records:

- audio run identifier and package identity;
- input cue-package identity;
- cue-schedule hash;
- WAV hash;
- render-log hash;
- renderer-metadata hash.

The validation path checks the audio package against the retained cue package and verifies cue-to-render relationships and sample bounds.

Suppressions have no audio-package record of their own because no waveform is generated for those event outcomes.

## Evaluation Evidence

Stage 3 evaluation evidence is optional at the contract level.

An unevaluated session can declare:

```json
{"available": false}
```

A retained evaluated session instead records the logical evaluation-report reference and identity required by the workbench. The browser displays the retained report; it does not recalculate metrics.

## Configuration Identity

The session records the sonification preset and audio renderer used by the retained chain, including their versions and hashes. This allows the workbench to display the exact configuration associated with a cue or suppression rather than relying on current default settings.

## Media Boundary

Source media is bound at runtime and is not embedded in the session contract. This keeps the committed session declaration portable and avoids storing dataset copies or machine paths in Git.

The retained catalogue is defined by:

```text
configs/workbench/retained-sessions.v0.1.0.json
```

The completed workbench exposes the retained MOT17-02-DPM and KITTI Tracking 0000 cases through the same inspection interface.

## Validation Boundary

A session must be validated before it is served. Validation checks include:

- session schema and supported versions;
- package and file hashes;
- cross-stage input identities;
- dataset and sequence consistency;
- preset and renderer identity;
- cue and suppression provenance;
- rendered cue sample ranges;
- optional evaluation-report identity;
- required source-media availability.

A broken link prevents the retained chain from being treated as valid inspection evidence. Validation does not regenerate or repair any research output.

## Inspection Behaviour

Once opened, the workbench provides read-only access to retained evidence including:

- source frames and bounding boxes;
- retained WAV playback;
- synchronised event, cue and suppression timeline records;
- selectable cues and suppressions;
- source annotation provenance;
- mapping/configuration identity;
- rendered sample ranges for cues;
- retained suppression reasons;
- retained technical evaluation metrics.

The workbench therefore acts as an inspection layer over previously generated evidence rather than as another processing stage.

## Reproducibility Boundary

The session contract makes the inspected evidence chain explicit and portable by recording logical identities and hashes separately from runtime storage paths. It supports verification that the same retained packages are being inspected, but does not by itself establish cross-platform byte identity or perceptual validity.
