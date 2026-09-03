# 0017: Local Synchronised Workbench

## Status

Accepted for Stage 4 Milestone 1 Phase 2 on 7 August 2026.

## Context

Decision 0016 defines Workbench Session Contract `0.1.0`.

The browser must inspect an already validated Stage 1 to 3 evidence chain rather than create a new processing pipeline.

Phase 2 therefore needed one working MOT17 example that could display:

* source images
* event bounding boxes
* cues and suppressions
* retained audio
* provenance links
* verified Stage 3 results

The retained `MOT17-02-DPM` case contains 600 zero based frames at 30 frames per second.

Stage 1 timestamps are calculated from:

`frame / frame_rate`

Stage 2 cue start times preserve these timestamps.

The renderer records the matching sample positions at 44.1 kHz.

The WAV is slightly longer than the video frame sequence because each cue has its own duration.

## Decision

Phase 2 will use:

* a small Python inspection model
* a local HTTP service
* plain HTML, CSS and JavaScript

No web framework, Node build process, database, analytics, authentication, upload feature or write function is required.

## Inspection Model

The Python inspection model opens a successfully validated workbench session.

It reads only the retained packages, evaluation report and media already linked to that session.

The model loads the JSON evidence once and creates indexes for:

* frame
* timestamp
* event ID
* cue ID

These indexes allow the browser to request small parts of the retained evidence efficiently.

The model does not:

* parse original dataset annotations
* generate events
* schedule cues
* render audio
* calculate evaluation metrics

It only presents evidence that already exists.

## Local Service

The service runs on the local machine by default.

It provides read only access to:

* session information
* frame information
* bounded timeline windows
* cue traceability
* evaluation results
* source images
* the verified WAV

Requests cannot be used to select arbitrary filesystem paths.

Errors do not expose private paths.

The WAV can be delivered in partial byte ranges for browser playback without modifying the original file.

## Audio And Frame Synchronisation

The browser audio player is the single live timing source.

The interface reads:

`audio.currentTime`

and uses it to calculate:

* the displayed video frame
* the timeline cursor

Play, pause, seek and frame step controls all use the same audio time.

No separate timer or independent frame counter is used.

The source image and SVG bounding box overlay use the same recorded image coordinate system.

## Timeline And Cue Inspection

The timeline loads a limited time window around the current audio position.

It displays retained:

* events
* cues
* suppressions

in separate lanes.

Selecting a cue loads its retained trace information, including:

* cue ID
* source event
* source annotation and row
* mapping preset
* renderer information
* rendered sample range

The metrics panel reads values directly from the verified Stage 3 evaluation report.

If no evaluation evidence exists, the interface reports it as unavailable rather than calculating replacement values.

## Rationale

This design keeps Python responsible for interpreting the retained evidence while the browser only presents it.

Using a small local service avoids adding unnecessary frameworks and build dependencies.

Prebuilt indexes also avoid repeatedly reading or searching large JSON files during playback.

This is particularly important for the dense MOT17 cue schedule.

Using audio time as the single clock prevents separate audio, frame, overlay and timeline timers from drifting apart.

Browser animation timing is used only to update the display and is not treated as research evidence.

## Consequences

* Workbench Session Contract `0.1.0` remains unchanged.
* Stage 1 to 3 contracts and outputs remain unchanged.
* The workbench is read only.
* Runtime package, report and media paths remain local and are not exposed through the interface.
* The browser requires standard support for HTML audio, Fetch, SVG and `requestAnimationFrame`.
* Phase 2 supports `MOT17-02-DPM`.
* KITTI support remains part of Phase 3.
* The interface provides technical inspection only.

The workbench does not provide evidence about usability, accessibility, perceptual effectiveness or safety.