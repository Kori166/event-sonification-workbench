# 0018: Retained Dataset Session Catalogue

## Status

Accepted for Stage 4 Milestone 1 Phase 3 on 14 August 2026.

## Context

Phase 2 showed that the workbench could inspect the retained `MOT17-02-DPM` session using Workbench Session Contract `0.1.0`.

Phase 3 needed to show that the same workbench architecture could also inspect KITTI Tracking sequence `0000`.

The aim was to support both retained datasets without changing the Stage 1 to 3 contracts or creating separate parsing, sonification, rendering or evaluation systems.

The retained KITTI evidence already contained:

* common event schema `0.2.0` records
* cue and suppression records
* the retained WAV and render evidence
* the verified Stage 3 evaluation report
* 154 locally stored source images

The existing session contract already supported the important KITTI differences, including dataset identity, source media, zero based PNG filenames, 10 fps timing and dataset specific provenance.

No change to the session contract was required.

## Decision

Workbench Session Contract `0.1.0` remains unchanged.

A retained KITTI session declaration is added alongside the existing MOT17 session.

A small catalogue lists only these two retained sessions and identifies the default session.

The catalogue does not search the filesystem or allow users to enter arbitrary paths.

Each session is opened through the existing validator and represented using the same read only inspection model.

Sessions are selected using their declared `session_id`.

Invalid session IDs return the stable error code:

`invalid_session_identifier`

## Session Service

The service remains stateless when switching between datasets.

`/api/sessions` provides the list of available retained sessions.

Existing read routes can also receive a `session_id`.

If no session ID is provided, MOT17 remains the default.

Frames, audio, timelines, cues, provenance and evaluation results always come from the selected validated session.

## Browser Session Switching

The browser includes a simple session selector.

Every request is linked to the selected `session_id`.

When the dataset is changed, the workbench:

* pauses and disconnects the current audio
* clears the previous frame and image
* clears overlays
* clears timeline information
* clears cue and provenance information
* clears evaluation and metadata information
* resets playback state
* loads the newly selected validated session

Older requests are ignored after a session change so information from the previous dataset cannot replace the newly selected session.

## Starting The Workbench

The main release command remains:

```powershell
python -m event_sonification_workbench.cli inspect-session