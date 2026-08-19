# 4. Workbench Design and Implementation

## 4.1 Architecture

The workbench is organised as a sequence of independently verifiable packages:

`native annotations → event package → cue package → audio package → evaluation report → workbench session`

This structure makes intermediate decisions visible. An adapter is responsible for source interpretation; the mapper operates on a common schema; the renderer operates on cues; and the evaluator reconciles evidence across package boundaries. The user interface consumes the validated products of these stages and does not silently remap or rerender them.

**Drafting note:** reserve Figure 1 for an architecture and provenance-flow diagram based on the sequence above. It should show the two dataset adapters converging on the common event schema, followed by mapping, rendering, evaluation and the read-only workbench. No repository-native architecture figure was audited in Phase A, so the diagram should be produced and checked during final assembly.

## 4.2 Normalisation layer

**Context.** MOT17 and KITTI express frames, boxes, classes and auxiliary properties differently. A mapper coupled directly to either native format would duplicate transformation logic and obscure what had been retained or changed.

**Decision and rationale.** Schema version 0.2.0 defines one event as one valid annotation observation. It records a deterministic event identifier, dataset and sequence identity, source row, zero-based frame index, derived timestamp, pixel-space bounding box, common and source class labels, native confidence where available, and provenance hashes. Derived centre and area values are explicit. Source-specific information remains in metadata rather than being discarded.

The MOT17 adapter converts one-based frames to zero-based frames and derives time at 30 frames per second. Its ground-truth evaluation mark remains metadata and does not become a confidence probability; native confidence is therefore null for the canonical ground-truth case. The KITTI adapter uses its native zero-based frames and 10 frames-per-second rate, converts left/top/right/bottom coordinates to `x`, `y`, `width`, `height`, and preserves fields such as truncation, occlusion, alpha and three-dimensional location. `DontCare` rows are retained as normalised events.

**Consequence.** Downstream components receive the same temporal and geometric interface while the evidence chain still exposes native meanings. This permits common evaluation without claiming that the underlying ontologies are identical. Boxes outside the image are retained with validation warnings rather than silently clipped, preserving source fidelity.

## 4.3 Mapping layer

**Context.** The mapping needed to be simple enough to audit while demonstrating spatial and temporal sonification. It also needed to account explicitly for events that did not generate audio.

**Decision and rationale.** Baseline preset version 0.1.0 maps event timestamp to cue start, horizontal box centre to stereo pan, vertically inverted box centre to frequency, and normalised box area to amplitude. Duration is fixed at 0.12 seconds. Frequency spans 220–1,760 Hz, amplitude 0.1–0.8 and pan -1–1. Inputs are clamped to their declared ranges and output parameters are rounded to six decimal places.

Eligibility is evaluated in a fixed order. `DontCare` events, events outside the inclusion policy, configured excluded classes, events with available native confidence below 0.5, and events rejected by frame stride can be suppressed. The canonical preset uses every frame and does not treat null confidence as low confidence. Every suppression is recorded with a code and reason. Cue identifiers are derived from the source event, preset identity and mapper identity, without timestamps, paths or random values.

**Consequence.** A cue or suppression can be reconstructed from declared inputs, and policy exclusions cannot disappear from coverage accounting. The simplicity of the baseline also creates limitations: area is only an approximate apparent-scale signal, and no priority, refractory or polyphony rule reduces dense simultaneous output.

## 4.4 Rendering layer

**Context.** Scheduling in decimal seconds is insufficient for exact audio verification because the final artefact is indexed in samples.

**Decision and rationale.** Renderer version 0.1.0 converts boundaries using round-half-up arithmetic and treats intervals as half open. It produces stereo, 44.1 kHz, 16-bit little-endian PCM WAV audio. Each cue is a zero-phase sine tone with a 0.005-second linear attack and 0.01-second linear release. Pan uses linear balance. Cues are mixed in a stable order defined by start sample and cue identifier, followed by conditional normalisation to a target peak of 0.95. Class modifiers remain traceable cue parameters but are deliberately not applied by this renderer policy.

**Consequence.** The render log records the source event, cue, sample bounds and parameters for every placed cue, supporting exact timing and provenance checks. The fixed synthesis policy is reproducible and inspectable, but it is a reference renderer rather than a perceptually optimised sound design.

## 4.5 Session integration and inspection interface

**Context.** Pipeline artefacts alone make it difficult to inspect a source box, its cue, its waveform position and its evaluation status together. Reimplementing processing in a web interface would risk divergence from the tested command-line chain.

**Decision and rationale.** Workbench Session Contract version 0.1.0 declares the prebuilt event, cue, audio and evaluation packages and derives a deterministic, path-independent session identity. Runtime roots are supplied through environment variables. Before a session is served, the complete artefact chain is validated. The server is loopback-only and the interface is read-only.

The interface displays source imagery and boxes, plays the unchanged rendered WAV, synchronises event, cue and suppression records on a timeline, exposes configuration and sample-range traces, and presents the Stage 3 metrics. Two canonical sessions cover the MOT17 and KITTI cases. Browser-based technical acceptance recorded 16 passing checks for loading, synchronisation, trace inspection and metric display.

**Consequence.** The workbench provides one inspection surface for the same evidence used by the evaluator, without creating an alternative processing path. The browser checks demonstrate technical integration, not user acceptance or usability.

## 4.6 Implementation outcome

Objectives O1 and O2 were achieved: the project supplies a common, provenance-preserving event representation and deterministic dataset adapters. O3 was partially achieved because deterministic mapping, rendering and export are implemented, but only one baseline preset was evaluated and planned density-control alternatives were not completed. O4 was partially achieved because coverage, alignment, traceability, density, overlap and reproducibility were evaluated rigorously, while some originally proposed ablations and measures were not implemented. These boundaries are carried into the Discussion rather than presented as completed features.

