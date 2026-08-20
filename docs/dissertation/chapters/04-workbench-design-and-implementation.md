# 4. Workbench Design and Implementation

## 4.1 Architecture and normalisation

The workbench uses independently verifiable packages rather than one opaque conversion. Figure 1 shows dataset-specific adapters converging on a common event contract, followed by shared mapping, rendering and evaluation. The inspection layer consumes retained products without remapping or rerendering them.

![Figure 1. Implemented architecture and provenance flow. Author-created from versioned contracts and retained session declarations; no experimental values.](../figures/figure-1-architecture-and-provenance.svg)

Schema `0.2.0` defines one event as one valid annotation observation and groups stable identity, zero-based time, object labels, pixel geometry, provenance and source metadata. The MOT17 adapter converts one-based frames and retains its ground-truth evaluation mark as metadata rather than confidence. The KITTI adapter converts corner coordinates and preserves truncation, occlusion, alpha and three-dimensional fields; `DontCare` remains a valid event. Downstream components receive one interface without implying identical native ontologies. Out-of-image boxes are retained with warnings rather than silently clipped.

**Table 2. Common event-schema groups and their reproducibility purpose. Author summary of schema `0.2.0`.**

| Group | Principal fields | Purpose |
|---|---|---|
| Identity and time | event/track identifiers, frame index, timestamp | Stable reference and temporal ordering |
| Semantics | common class, source class, source attributes | Shared processing without erasing native meaning |
| Geometry | image dimensions and bounding-box coordinates | Normalised mapping inputs with retained pixel context |
| Provenance | dataset, sequence, source row and hashes | Resolution from a derived event to its declared source |

Validation is deliberately stricter than adapter convenience. It rejects malformed identifiers, non-finite values, invalid box ordering and inconsistent dimensions, while emitting warnings for geometries that may be legitimate annotations but exceed the image boundary. This distinction keeps structural failures out of the pipeline without silently rewriting source observations. Package manifests record counts, schema/configuration versions, source identities and file hashes, so later stages can verify that they consumed the declared event set rather than a similarly named local file.

## 4.2 Mapping and rendering

Baseline preset `0.1.0` implements a simple auditable parameter mapping. Table 3 summarises the rules and their interpretation boundaries.

**Table 3. Frozen mapping and renderer rules. Author summary of preset and renderer `0.1.0`; exact hashes are retained in session declarations.**

| Rule | Implemented treatment |
|---|---|
| Time and duration | Event timestamp sets cue start; duration is 0.12 s |
| Space and frequency | Horizontal centre sets pan; inverted vertical centre sets 220–1,760 Hz |
| Amplitude | Normalised bounding-box area sets 0.1–0.8; area is not metric depth |
| Eligibility | Each valid event becomes a cue or reason-coded suppression under class/confidence/stride policy |
| Rendering | 44.1 kHz stereo 16-bit PCM; round-half-up, half-open intervals and stable mixing order |
| Class modifier | Retained for traceability but inaudible in renderer `0.1.0` |

Inputs are clamped and mapped values rounded to six decimals. The canonical preset uses every frame and does not treat null confidence as low confidence. Content-derived cue identifiers exclude time-varying state, random values and local paths, so cues and suppressions can be reconstructed from declared inputs.

Suppression is represented as an outcome rather than deletion. Every valid input therefore has exactly one terminal mapping status, allowing the evaluator to distinguish an intentional class-policy decision from an unexplained absence. Keeping the inaudible class modifier in the cue package similarly exposes an implementation boundary: the value is reproducible and inspectable, but no audible class distinction should be claimed for renderer `0.1.0`.

The renderer converts time boundaries to samples, synthesises fixed-envelope sine cues, applies stereo balance and mixes in stable order with conditional peak normalisation. Its log records the event, cue, parameters and sample interval for every placement. This is a reproducible reference renderer, not a perceptually optimised design. It contains no priority, refractory or polyphony control, and bounding-box area is only an imperfect apparent-scale proxy (Dubus and Bresin, 2013).

## 4.3 Inspection layer and outcome

Workbench Session Contract `0.1.0` declares the event, cue, audio and evaluation packages and derives a path-independent session identity. Runtime roots bind local evidence; validation checks the chain before the loopback-only server displays imagery/boxes, unchanged WAV playback, timeline outcomes, provenance and Stage 3 metrics.

The MOT17 and KITTI sessions passed 16 researcher-controlled browser checks for loading, synchronisation, selection, trace inspection and metric display. These were engineering acceptance checks, not usability testing. A workbench screenshot remains excluded because no publication-cleared source frame was retained.

O1/O2 were achieved. O3/O4 were partially achieved: deterministic generation/export and a rigorous technical evaluation were completed, but comparative presets, density controls, ablations and some proposed measures were not.
