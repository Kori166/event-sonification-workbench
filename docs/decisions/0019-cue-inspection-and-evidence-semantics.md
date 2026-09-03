# 0019: Stable Cue Inspection And Clearer Workbench Evidence

## Status

Accepted for Stage 4 Milestone 2 on 14 August 2026.

## Context

Researcher inspection found several problems near the start and end of retained sequences.

Cue selection could be unreliable, playback and provenance could appear one frame apart, frame intervals were difficult to see, and the meaning of EVENT, CUE and SUPPRESS was unclear.

The baseline mapping explanation was also too technical.

Checks confirmed that the first, second, second last and final cue traces were complete for both MOT17 and KITTI. The retained evidence itself was correct.

The problem was in the browser interface.

The timeline repeatedly requested and rebuilt the same evidence window near sequence boundaries. Cue controls were also recreated unnecessarily, and clicking anywhere on the canvas could select the nearest cue rather than only selecting cues from the CUE lane.

## Decision

Workbench Session Contract `0.1.0` remains unchanged.

The workbench will continue to display existing Stage 1 to 3 evidence without recalculating results.

Each event shown for a frame is linked to its recorded Stage 2 outcome:

* represented by a cue
* intentionally suppressed
* unresolved where an integrity problem exists

A represented event may link to its retained cue.

A suppressed event may link to its retained suppression reason.

These are lookups of existing evidence rather than new calculations.

## Frame And Time Handling

The displayed video frame follows:

```text
frame = floor(audio.currentTime * frame_rate)

frame n covers n / fps <= t < (n + 1) / fps