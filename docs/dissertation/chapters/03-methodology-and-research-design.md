# 3. Methodology and Research Design

## 3.1 Research approach

The study used an iterative design-and-evaluation method to construct and examine a computational research artefact. The pipeline transforms annotations into normalised events, maps eligible events to cues, renders audio and exposes evidence for inspection. Reproducible-computing principles informed version recording, retained intermediates and avoidance of manual result manipulation (Sandve *et al.*, 2013; Pineau *et al.*, 2021). Each claim had to resolve to a contract, generated artefact, automated check or recorded decision.

Development proceeded through common-schema/adaptor construction, mapping/rendering, frozen technical evaluation and integration into a local read-only workbench. An **event** is one valid annotation observation at one frame; a **cue** is a scheduled audio representation; and a **suppression** is an explicit reason-coded decision that a valid event produces no cue. **Technical evaluation** concerns the computational transformation, not listener performance.

This order separated research questions that would otherwise be coupled. Schema/adaptor validation established the input meaning before audio was produced; mapping and rendering were then evaluated against that stable representation; and the inspection interface was built over retained evidence rather than becoming a second processing implementation. Decisions, risks and verification records distinguished implemented behaviour from proposal intent throughout development.

## 3.2 Case selection and construction

MOT17-02-DPM and KITTI Tracking 0000 were purposively selected to exercise different conventions rather than support population inference (Dendorfer *et al.*, 2021; Geiger *et al.*, 2013). Table 1 summarises the relevant boundary.

MOT17 provides a dense pedestrian-focused case at 30 frames per second, whereas KITTI supplies a lower-rate road-scene case with broader classes and richer metadata. Their contrast tests whether shared downstream processing can coexist with source-specific parsing, but it does not make the sequences statistically comparable or representative of their complete datasets.

**Table 1. Native case differences and adapter treatment. Author summary of dataset documentation and implemented contracts.**

| Concern | MOT17-02-DPM | KITTI 0000 | Common treatment |
|---|---|---|---|
| Frame/time | One-based; 30 fps | Zero-based; 10 fps | Zero-based frame and derived timestamp |
| Geometry | `x`, `y`, width, height | left, top, right, bottom | Pixel `x`, `y`, width, height |
| Semantics | Tracking classes/evaluation mark | Road classes, `DontCare`, 3D fields | Common/source labels separated; native metadata retained |
| Confidence | Evaluation mark is not probability | Optional score | Confidence populated only where source meaning supports it |
| Provenance | Source row/configuration | Source row/configuration | Deterministic identity, logical origin and hashes |

Each adapter applies explicit index/geometry conversions and emits schema `0.2.0` event packages. The mapper consumes validated events under preset `0.1.0`, producing a cue or suppression account. Renderer `0.1.0` emits PCM audio and sample-level logs. Stable identifiers and hashes connect stages. Session Contract `0.1.0` binds retained event, cue, audio and evaluation artefacts for inspection without reimplementing processing.

Full datasets, generated packages and WAV files remained outside version control. Logical inputs, expected hashes and environment-variable roots connect independently obtained local data to results without embedding private machine paths.

## 3.3 Evaluation design

Technical Evaluation Contract `0.1.0` was frozen before the real cases. It defines event outcomes and coverage denominators, sample/seconds timing domains, resolved traceability, density/overlap and levels of reproducibility. Freezing definitions reduced scope for post-hoc favourable metrics.

A manually calculated synthetic oracle first exercised five events, five cues, one suppression, overlapping/touching intervals and sample conversion. Negative cases introduced eligible misses, orphan cues, contradictory outcomes, broken links and a one-sample displacement, mitigating the risk that pipeline and evaluator shared the same error. The unchanged contract was then applied to both public-data chains. Repeated builds tested determinism; an independent audit compared canonical reports with tables, figures, captions and hashes.

Accounting completeness requires one recognised outcome per valid event. Eligible coverage excludes intentional suppressions, while source representation includes them. Alignment compares expected and actual boundaries; traceability resolves identifiers and hashes; density/overlap describe load; and reproducibility distinguishes semantic, byte, audio and configuration identity.

These distinctions were methodological controls rather than reporting conveniences. They prevent intentional policy exclusions being labelled misses, floating-point seconds obscuring exact sample placement, plausible identifiers being accepted without resolving their links, and same-environment equality being generalised to untested platforms.

## 3.4 Research quality and scope

Versioned contracts, deterministic identities, automated tests, byte comparisons, the independent oracle, injected faults and the reporting audit support reliability and internal validity. Construct validity is bounded: the metrics measure transformation properties, not intelligibility. External validity is limited by two selected sequences, rectangular annotations, one mapping/renderer and one recorded execution environment. Shared conventions may still influence pipeline and evaluator despite independent checks. Conclusions are therefore descriptive technical claims. No participant, accessibility or task-performance experiment was conducted, and cross-platform byte identity was not tested.
