# 6. Discussion

## 6.1 RQ1: How can public annotated video datasets be transformed into a common event schema suitable for event-based sonification?

The implementation shows that heterogeneous tracking annotations can be transformed by separating a stable common representation from source-specific metadata. In both adapters, an event denotes one valid annotation observation at one frame, rather than an inferred object-appearance interval. Frame indices are normalised to a zero-based convention, timestamps are derived from the declared frame rate, and bounding boxes use a common pixel-space `x`, `y`, `width`, `height` form. Common and source class labels remain separate, while provenance records retain the dataset, sequence, source row and content hashes.

This separation avoided forcing the datasets into false equivalence. MOT17's evaluation mark is retained as metadata rather than reinterpreted as confidence, and its one-based frames are explicitly converted. KITTI's truncation, occlusion, alpha, three-dimensional dimensions, location and rotation are preserved in source metadata. `DontCare` annotations become valid `dont_care` events and remain auditable even when the mapping preset suppresses them. The schema therefore provides the shared temporal, geometric and provenance fields needed by the mapper without discarding meaningful differences in the source ontologies.

The result is evidence for a practical transformation method rather than a claim of universal dataset interoperability. Only two tracking formats were implemented, and both provide frame-level bounding boxes. Other modalities, sparse annotations, uncertain temporal extents or substantially different ontologies could require schema extensions and new validation rules.

## 6.2 RQ2: How can normalised visual events be mapped into deterministic and traceable audio cues?

The baseline mapping uses explicit, inspectable functions. Event time determines cue start; normalised horizontal centre determines pan; vertical centre determines frequency with the axis inverted; and normalised box area determines amplitude. Cue duration is fixed. Values are clamped to the declared ranges and rounded to six decimal places, while class modifiers are retained as trace parameters but are not applied by the baseline renderer. Eligibility is also explicit: `DontCare` and configured excluded classes are suppressed, available native confidence below the configured threshold may be suppressed, and a frame-stride rule can reduce temporal density.

Determinism depends on more than using fixed equations. Event and cue identifiers are content-derived, packages record configuration identities and hashes, and suppression records state a machine-readable reason. Rendering uses round-half-up sample conversion, half-open sample intervals, a fixed 44.1 kHz stereo PCM format and an ordered mixing policy. The complete cue and suppression trace rates in both cases, together with repeatable packages and audio, show that the implementation made each output accountable within the tested environment.

However, deterministic does not mean perceptually effective. The canonical preset is a baseline, not an optimised sonification design. In particular, direct area-to-amplitude mapping treats bounding-box area as an approximate apparent-scale signal. That signal varies with pose, stride, occlusion, truncation and perspective. KITTI contains metadata that could support richer depth-sensitive mappings, but those alternatives were not evaluated here.

## 6.3 RQ3: How can event-based sonification outputs be evaluated using technical metrics for coverage, alignment, traceability and reproducibility?

The evaluation demonstrates the value of predefining event outcomes and denominators. Each valid event must be represented, intentionally suppressed, missed or excluded. Multiple cues may represent one event, so cue count is not substituted for event coverage; intentional suppressions are not treated as misses. Under these definitions, both cases achieved complete event accounting and eligible coverage even though their source representation rates differed substantially.

Temporal evaluation in samples, seconds and across scheduling, placement and end-to-end domains also prevented a misleading single-number result. Exact integer-sample agreement coexisted with very small floating-point second differences for MOT17. Traceability was tested by resolving and comparing identifiers and hashes across the chain. Reproducibility was divided into semantic, byte, audio and configuration checks and bounded to the recorded environment. Together, these measures offer an auditable technical evaluation pattern for this class of pipeline.

Coverage and correctness metrics are not sufficient on their own. Density and overlap exposed a major difference that the 100% eligible-coverage result would hide: MOT17 produced roughly 29 times as many cues per second as KITTI and a much larger overlap burden. This is technically important because a policy can be complete, aligned and reproducible while producing a highly crowded sound field. The present work can measure that condition, but cannot determine its perceptual consequences.

## 6.4 Cross-dataset implications

The shared pipeline behaved consistently across two datasets with different frame rates, image dimensions, annotation conventions and class vocabularies. The different result profiles arose from declared data and policy differences rather than dataset-specific renderer code. In particular, the KITTI source representation rate reflects the retained and suppressed `DontCare` class, while MOT17's high density reflects its much larger number of eligible observations in a short sequence.

This comparison supports the architectural choice to keep adapters dataset-specific while making schema validation, mapping, rendering and evaluation common. It also shows why future comparisons should report the composition of event outcomes alongside aggregate rates. Otherwise, intentional policy choices can be mistaken for technical failure, and dense successful mappings can appear unconditionally preferable to sparser ones.

## 6.5 Threats to validity and limitations

Internal validity is strengthened by the frozen contract, synthetic oracle, negative tests, content-derived identities and independent audit. Nevertheless, the evaluation uses one baseline preset and one renderer. It does not include mapping ablations, alternative density controls, priority rules, refractory periods or polyphony limits. The causal effect of individual mapping choices therefore remains untested.

Construct validity is limited by the scope of the metrics. Accounting, alignment and traceability measure properties of the transformation pipeline, not whether listeners perceive the intended event attributes. Informal researcher inspection indicated that dense overlaps were difficult to distinguish, but this observation is not participant evidence. No claims are made about usability, accessibility, navigational benefit or safety.

External validity is limited to two selected public tracking sequences. The cases exercise meaningful differences, but they do not represent all visual datasets or deployment conditions. Reproducibility is additionally bounded to Windows/AMD64/Python 3.14.3; the evidence does not support a cross-platform byte-identity claim. Raw datasets and large generated audio packages were not committed, so reproduction also depends on independently obtaining the source data and configuring the declared runtime roots.

Finally, the baseline treats each annotation observation independently. It does not perform temporal smoothing or reason about object trajectories as higher-level events. This preserves a clear audit trail, but contributes to cue density and leaves open whether track-level aggregation would better serve a perceptual task.

