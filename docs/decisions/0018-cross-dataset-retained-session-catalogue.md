# 0018: Cross-dataset retained-session catalogue

## Status

Accepted for Stage 4 Milestone 1 Phase 3 on 14 August 2026.

## Context

Phase 2 proves one retained MOT17-02-DPM inspection slice through Workbench Session Contract
`0.1.0`, an immutable indexed inspection model, a loopback read service and a plain browser client.
Phase 3 must demonstrate the same architecture with retained KITTI Tracking sequence `0000` without
changing Stage 1-3 contracts or creating another parser, scheduler, renderer or evaluator.

The retained KITTI chain already contains a valid schema `0.2.0` event package, cue and suppression
package, exact WAV/render package, verified Stage 3 report and 154 locally bound source images. Its
runtime differences are already represented by the frozen session contract: dataset identity,
logical media binding, native zero-based PNG filenames, 10 fps timing and dataset-specific
provenance values. No contract defect is present.

## Decision

Phase 3 retains Workbench Session Contract `0.1.0` unchanged and adds one path-free KITTI session
declaration beside the existing MOT17 declaration. A small committed catalogue lists only those two
logical declaration paths and identifies the default session. Catalogue paths must be safe relative
repository paths; the service provides no filesystem discovery, upload or editable path input.

Each declaration is independently opened by the existing validator and represented by the existing
immutable `InspectionModel`. A bounded `InspectionCatalogue` provides deterministic summaries and
lookup by declared `session_id`. Lookup failures use the stable path-free code
`invalid_session_identifier`.

The loopback service remains stateless with respect to session selection. `/api/sessions` exposes
the bounded catalogue, while existing read routes accept an optional `session_id` query. Omitting
the query preserves the declared default MOT17 behaviour. Image and audio bytes, frames, timelines,
traces and evaluation projections always come from the explicitly resolved immutable model.

The browser adds a minimal retained-session selector. Every request is scoped by `session_id`.
Changing selection pauses and detaches audio, increments a request generation, clears image/frame,
overlay, timeline, cue/trace, evaluation, metadata, notice and playback state, then loads the new
verified session. Responses from an earlier generation are ignored so no stale dataset state can
replace the selected session.

The primary release launch remains:

```powershell
python -m event_sonification_workbench.cli inspect-session
```

It loads the committed catalogue, validates both retained declarations against process-local
bindings, and serves only on loopback. `--session` remains available as a bounded single-declaration
diagnostic path.

## Rationale

Explicit immutable models plus query-scoped lookup avoid mutable server session state and make
cross-session isolation testable. Reusing the same validator, model, routes and frontend projection
keeps dataset-specific research semantics in the retained common events and provenance where they
belong. A two-entry catalogue is sufficient for release assessment and does not create a dataset
management feature.

## Consequences

- Workbench Session Contract `0.1.0` and all Stage 1-3 contracts/results remain unchanged.
- Only the declared MOT17 and KITTI sessions can be selected; no arbitrary filesystem browsing or
  generic import is introduced.
- Runtime dataset/package/report paths remain process-local and path-free API errors are preserved.
- The accepted WAVs, mappings, suppression policies, render logs and Stage 3 metrics are consumed
  unchanged.
- Browser acceptance is technical presentation evidence only. R20 remains open and controlled; the
  interface establishes no usability, accessibility, navigation, perceptual or safety benefit.

