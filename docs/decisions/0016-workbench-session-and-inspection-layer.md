# 0016: Workbench Session And Inspection Layer

## Status

Accepted for Stage 4 Milestone 1 Phase 1 on 7 August 2026.

A clarification was added later the same day to support separate event, cue and audio package locations.

This did not change Workbench Session Contract `0.1.0` or the way session identity is calculated.

The corrected implementation was verified against both retained MOT17 and KITTI sessions before final acceptance.

## Context

Stages 1 to 3 already produce and verify:

* event packages
* cue and suppression packages
* rendered audio packages
* provenance links
* technical evaluation reports

Stage 4 needs to bring this evidence together in one inspection interface.

The interface must not repeat parsing, cue generation, rendering or evaluation logic because that would create a second research pipeline and weaken traceability to the verified outputs.

The workbench is therefore a read only inspection tool for research evidence.

It does not provide participant evidence and does not establish usability, accessibility, navigation, perceptual effectiveness or safety.

## Decision

Workbench Session Contract `0.1.0` is fixed before browser development begins.

A workbench session links:

* one Stage 1 event package
* one Stage 2 cue package
* one Stage 2 audio package
* optionally, one Stage 3 technical evaluation report

The Python session loader must validate the complete evidence chain before it is passed to the browser.

This includes:

* checking the session structure
* reusing existing Stage 1 to 3 package validation
* checking identities and hashes across stages
* resolving source media only after the evidence chain has passed validation

The browser receives only an already validated session.

It cannot modify Stage 1 to 3 packages, regenerate audio or recalculate evaluation results.

## Session Identity

Each session receives a deterministic `session_id`.

The identity is based on retained evidence such as:

* dataset and sequence
* package run IDs
* package hashes
* file hashes
* configuration identities
* evaluation identity where available

Local storage locations are not part of the session identity.

This means the same retained evidence can be moved to another directory or machine without changing its identity.

## Runtime File Locations

Event, cue and audio packages may be stored in separate locations.

The following runtime settings can be used:

* `EVENT_PACKAGE_ROOT`
* `CUE_PACKAGE_ROOT`
* `AUDIO_PACKAGE_ROOT`

If all packages are stored beneath one common directory, `OUTPUT_ROOT` can still be used as a fallback.

Dataset media continue to use:

* `MOT17_ROOT`
* `KITTI_TRACKING_ROOT`

These runtime paths are not included in `session_id` and are not returned in diagnostics.

## Rationale

This design keeps the workbench separate from the research processing pipeline.

Stage 4 displays evidence that has already been created and verified rather than creating a second interpretation of it.

Reusing the existing package validators also means Stage 4 cannot silently accept evidence that earlier stages would reject.

Keeping storage paths outside the session identity improves portability. The retained evidence can move between machines or directories without becoming a different research session.

The separate package location support was required because the retained Stage 2 event, cue and audio packages are stored in different directories.

This is treated as a runtime storage detail rather than part of the research evidence.

## Consequences

* Missing, mismatched or altered evidence is rejected before the interface loads.
* Local paths, usernames and machine names do not become part of the session identity.
* Runtime storage locations can change without changing Workbench Session Contract `0.1.0`.
* MOT17 and KITTI source media remain outside Git.
* A missing Stage 3 report does not prevent inspection of valid Stage 1 and Stage 2 evidence.
* When no evaluation report is available, the session records `evaluation.available = false`.
* No replacement evaluation values are calculated.
* Display only timelines, waveforms or similar visualisations are not treated as evaluation evidence.
* Stage 4 can add presentation and media serving features without changing Stage 1 to 3 contracts or results.
``