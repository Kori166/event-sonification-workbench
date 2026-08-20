# 8. Conclusion and Future Work

This project produced an auditable workbench that separates dataset interpretation, common events, deterministic cue/suppression generation, rendering and technical evaluation.

For RQ1, dataset-specific adapters transformed MOT17-02-DPM and KITTI Tracking 0000 into schema `0.2.0` while preserving native labels, metadata and provenance. This does not establish universal interoperability. For RQ2, fixed eligibility, mapping, identity, rounding and renderer contracts produced deterministic, fully traceable cues and suppressions for one baseline, not an optimal or perceptually validated mapping. For RQ3, predeclared outcomes/denominators, sample/seconds alignment, resolved provenance, load metrics and tiered repetition provided an auditable technical evaluation.

Both cases achieved complete accounting, 100% eligible coverage, complete cue/suppression traceability and zero maximum integer-sample error; repeated outputs matched in the recorded environment. O1/O2 were achieved and O3/O4 partially achieved because comparative presets, density controls, ablations and some proposed measures were not completed. The main limitation is that technical correctness coexisted with extreme MOT17 density, without participant evidence about distinguishability.

The dissertation's contribution is therefore methodological as much as technical: it demonstrates how an event-sonification claim can be bounded by explicit source interpretation, terminal outcomes, reproducible artefacts and metrics whose denominators remain visible. That evidence chain supports scrutiny of what the software did while preventing correctness results from being promoted into untested human-centred claims.

Future work should compare track aggregation, priority, refractory and polyphony controls against the frozen baseline; test height, smoothing and KITTI three-dimensional data as alternatives to area; and evaluate discrimination, workload and accessibility with appropriate participants/ethics approval. Additional formats and cross-platform reproduction should then test the boundaries of the common schema and deterministic implementation.
