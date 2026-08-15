# 0019: Boundary cue inspection and evidence semantics

## Status

Accepted for Stage 4 Milestone 2 on 14 August 2026.

## Context

Researcher inspection of the Milestone 1 release candidate found unreliable cue selection near the
start and end of retained sequences, confusing one-frame differences between playback and selected
provenance, invisible frame intervals, ambiguous EVENT/CUE/SUPPRESS interaction and incomplete
baseline-mapping explanation.

Audit proved that first, second, penultimate and final cue traces resolve completely for both MOT17
and KITTI. The retained provenance is sound. The boundary defect is browser-side: a clamped window
can never enter the old fixed inner-cache margin, so the animation loop refetches the same window and
each response destroys and rebuilds its cue controls. The browser also derived outcome styling from
the current one-second window and selected the nearest cue for a click in any canvas lane.

## Decision

Workbench Session Contract `0.1.0` remains unchanged. The immutable inspection model projects each
frame event's already-recorded Stage 2 outcome as represented, suppressed or unresolved. A
represented projection may identify its retained cue; a suppressed projection may identify its
retained suppression code. This is indexed evidence-link lookup, not result calculation.

Frame-time presentation uses the half-open relationship:

```text
frame = floor(audio.currentTime * frame_rate)
frame n covers n / fps <= t < (n + 1) / fps
```

When a cue is selected, the browser pauses, seeks to the retained cue start and explicitly loads the
cue's recorded source-event frame. This explicit frame avoids a rounded cue timestamp being treated
as evidence for a neighbouring frame. Independent play, seek or step returns the viewer to the
ordinary playback-frame relationship.

Timeline caching treats clamped start/end windows as stable, records the pending window key and
allows a newer request to supersede an older response. Frame divisions and a current-frame interval
derive only from frame rate and window bounds; the exact audio cursor remains visually separate.
Only bounded hits on the CUE lane select a cue. EVENT and SUPPRESS lanes remain contextual.

The interface describes EVENT as a Stage 1 normalised event and CUE/SUPPRESS as its possible Stage 2
outcomes. It exposes retained cue parameters and a static key for the frozen baseline mapping. The
renderer policy is stated accurately: `class_modifier` is retained for traceability but is not
applied to the waveform.

### Follow-up refinement after first browser acceptance

The first researcher-controlled acceptance attempt on 15 August 2026 did not pass. Display-rate
redrawing of every dense timeline marker caused avoidable playback work, cue controls were ordered
by distance from the playback clock, and the normal legend/mapping language was too complex.

The static timeline layer is therefore cached and rebuilt only when its evidence window or size
changes; the display-rate path composites that layer with the current frame interval and cursor.
Frame projection/image work occurs only on source-frame transitions or explicit inspection actions.
Images are prepared off-screen, with preloading bounded to the following two frames. Cue controls use stable
`(start_time_seconds, track_id, cue_id)` order and selection changes only their highlight when the
window is already present.

`unresolved` remains a backend integrity state but is not a normal displayed Stage 2 outcome. The
validated-session legend shows only cue generation and intentional suppression; any unresolved
projection raises a neutral, path-free integrity warning. The visible mapping key uses plain
Time/Left-right/Pitch/Loudness wording while retaining the technical-baseline, no-depth and no-
perceptual-validation limitations.

## Consequences

- No Stage 1 schema/parser/event package, Stage 2 preset/scheduler/renderer/WAV or Stage 3
  contract/report changes.
- Boundary interaction becomes stable without widening the bounded timeline or adding an inspector.
- Bounding-box area remains the frozen amplitude input. It is documented as an imperfect
  apparent-scale proxy because pedestrian pose can change width independently of meaningful
  apparent-distance change.
- Bounding-box height and smoothed height change remain possible future mapping experiments, never
  ground-truth depth claims.
- R20 remains open: informal researcher inspection found dense overlapping cues difficult to
  distinguish, but no participant or perceptual evaluation has been conducted.
