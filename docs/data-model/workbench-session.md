# Workbench Session Contract 0.1.0

## Purpose

A workbench session identifies one retained chain of evidence that can be inspected in the workbench.

The chain can include:

* Stage 1 events
* Stage 2 cues and suppressions
* Stage 2 rendered audio
* optional Stage 3 technical evaluation results

The session is read only. It does not contain raw dataset media, regenerate research outputs or store absolute paths from the local machine.

The formal session schema is:

```text
configs/workbench/workbench-session.schema.v0.1.0.json
```

## Session Identity And Runtime Locations

The contract keeps deterministic session identity separate from the local locations used to open files.

The deterministic identity includes:

* dataset and sequence
* Stage 1 event package identity and hashes
* Stage 2 cue package identity and hashes
* Stage 2 audio package identity and hashes
* sonification preset identity
* renderer identity
* optional Stage 3 evaluation identity

These values are used to create the content based `session_id`. Runtime settings tell the workbench where the retained packages and dataset media are stored on the current machine. These locations are not included in the `session_id` and are not recorded as provenance.

Supported runtime settings are:

* `EVENT_PACKAGE_ROOT`
* `CUE_PACKAGE_ROOT`
* `AUDIO_PACKAGE_ROOT`
* `OUTPUT_ROOT` as a shared fallback
* `MOT17_ROOT`
* `KITTI_TRACKING_ROOT`
* `REPOSITORY_ROOT` for evaluation evidence stored in the repository

When a package specific root is supplied, it takes priority over `OUTPUT_ROOT`.

## Session Structure

| Field | Purpose |
|---|---|
| `session_version` | Identifies the version of the session contract. |
| `session_id` | Identifies the retained evidence chain using its content. |
| `dataset` | Identifies `mot17` or `kitti_tracking`. |
| `sequence` | Identifies the retained dataset sequence. |
| `event_package` | Identifies the Stage 1 event package. |
| `cue_package` | Identifies the Stage 2 cue and suppression package. |
| `audio_package` | Identifies the Stage 2 rendered audio package. |
| `evaluation` | Identifies optional Stage 3 evaluation evidence. |
| `configuration` | Identifies the sonification preset and renderer. |
| `media` | Describes the source media required at runtime without storing local paths. |

## Stage 1 Event Package

The event package section records the retained Stage 1 run and the exact identities of:

* `events.json`
* `events.csv`
* `run_metadata.json`
* `provenance_log.json`

It also records the event schema version and package identity.

The Stage 1 loader remains responsible for checking:

* canonical serialisation
* event ordering
* package metadata
* source provenance
* the content based run identifier

The workbench does not repeat these processing rules.

## Stage 2 Cue And Suppression Package

The cue package section records:

* the cue run identifier
* the cue package identity
* the expected Stage 1 input package
* cue schedule hashes
* cue log hash
* suppression log hash
* sonification metadata hash

The session validator checks that the Stage 1 package declared by the session matches the Stage 1 input recorded by Stage 2.

This preserves the event outcome relationship:

```text
valid event
→ cue

or

valid event
→ suppression
```

Each valid event should therefore have a traceable recorded outcome.

## Stage 2 Audio Package

The audio package section records:

* the audio run identifier
* the audio package identity
* the input cue package
* cue schedule hash
* WAV hash
* render log hash
* renderer metadata hash

Validation checks that the audio package belongs to the retained cue package. It also checks the recorded relationship between cues and rendered sample ranges. Suppressions do not have audio records because they intentionally produce no waveform.

## Evaluation Evidence

Stage 3 evaluation evidence is optional within the session contract.

A session without evaluation evidence can declare:

```json
{
  "available": false
}
```

An evaluated session instead records the logical location and identity of the retained evaluation report. The workbench displays these saved results. It does not recalculate the evaluation metrics.

## Configuration Identity

The session records the exact sonification preset and audio renderer associated with the retained outputs. This includes their versions and hashes. The workbench can therefore show the configuration that actually produced a cue or suppression rather than relying on the current default settings.

## Source Media

Source images and other dataset media are provided at runtime. They are not stored inside the session declaration. This keeps the session portable and avoids committing dataset copies or local machine paths to Git.

The retained session catalogue is stored at:

```text
configs/workbench/retained-sessions.v0.1.0.json
```

The final workbench contains retained sessions for:

* MOT17 sequence `MOT17-02-DPM`
* KITTI Tracking sequence `0000`

Both are opened through the same inspection interface.

## Session Validation

A session must pass validation before the workbench treats it as valid retained evidence.

Validation checks include:

* session structure and supported versions
* package and file hashes
* links between Stage 1 and Stage 2 packages
* dataset and sequence consistency
* preset and renderer identity
* cue provenance
* suppression provenance
* rendered sample ranges
* optional evaluation report identity
* availability of required source media

A broken link causes the session to fail validation. The validator does not regenerate, alter or repair research outputs.

## Workbench Inspection

Once a valid session is opened, the workbench provides read only inspection of retained evidence.

This includes:

* source frames
* bounding boxes
* retained WAV playback
* event timeline records
* cue timeline records
* suppression timeline records
* selectable cues and suppressions
* source annotation provenance
* sonification configuration
* rendered sample ranges
* suppression reasons
* retained technical evaluation results

During playback, the retained audio time acts as the main synchronisation clock. The displayed source frame, timeline position and related evidence are derived from this audio time. Independent timers are not used to advance these elements separately. The workbench therefore presents previously generated evidence rather than creating another processing stage.

## Reproducibility Limits

The session contract makes the retained evidence chain explicit by recording logical identities and hashes separately from local storage locations. This supports checking that the same retained packages are being inspected across repeated use of the workbench. It does not demonstrate cross platform byte identity. It also does not provide evidence of perceptual validity, usability or human benefit.