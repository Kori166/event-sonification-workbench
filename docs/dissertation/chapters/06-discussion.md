# 6. Discussion

## 6.1 RQ1: How can public annotated video datasets be transformed into a common event schema suitable for event-based sonification?

The cases show that heterogeneous tracking annotations can be transformed by separating a stable common core from source-specific interpretation. Frame indices, timestamps and box geometry are normalised; common/source labels remain separate; and provenance retains dataset, sequence, source row, configuration and hashes. This respects the datasets’ different purposes rather than treating their rows as interchangeable (Dendorfer *et al.*, 2021; Geiger *et al.*, 2013). Thus the MOT17 evaluation mark remains metadata, while KITTI’s `DontCare` and three-dimensional fields remain auditable.

This extends dataset-documentation principles from dataset-level origin and transformation (Gebru *et al.*, 2021; Pushkarna, Zaldivar and Kjartansson, 2022) into individual events and packages. **RQ1 is answered:** for the selected formats, dataset-specific adapters can produce a versioned common event schema while retaining native semantics and provenance. The result covers two frame-level rectangular formats, not universal interoperability.

## 6.2 RQ2: How can normalised visual events be mapped into deterministic and traceable audio cues?

Determinism followed from fixing eligibility, equations, ranges, rounding, identities and renderer policy, not merely from using simple functions. Each event has a cue or coded suppression; content-derived identifiers and hashes bind inputs/configuration; and stable sample conversion/mixing connects cues to rendered intervals. This treats mapping as an explicit design object, consistent with parameter-mapping research (Grond and Berger, 2011).

However, determinism is not perceptual effectiveness. Mapping practice is diverse and often weakly evaluated (Dubus and Bresin, 2013). In particular, bounding-box area is an imperfect apparent-scale input affected by pose, truncation, occlusion and perspective, not metric depth (R21). **RQ2 is answered:** versioned mapping and rendering contracts can create deterministic, traceable cues and suppressions for one baseline, without establishing listener comprehensibility or superiority.

## 6.3 RQ3: How can event-based sonification outputs be evaluated using technical metrics for coverage, alignment, traceability and reproducibility?

Predeclared outcomes and denominators prevented cue count from being mistaken for event coverage and suppressions from being treated as misses. Multi-domain timing preserved the distinction between exact sample placement and small seconds-domain floating-point differences. Trace tests resolved identifiers/hashes, while tiered reproduction separated semantic, byte, audio and configuration claims. This operationalises reproducibility as testable procedure rather than aspiration (Sandve *et al.*, 2013; Pineau *et al.*, 2021).

The load results also show why correctness metrics are insufficient: the accounting results in Table 4 coexist with substantially different density and overlap profiles. Participant studies demonstrate why those technical loads cannot predict human performance (Hu *et al.*, 2020; Neugebauer *et al.*, 2020; Ji *et al.*, 2021). **RQ3 is answered:** a frozen outcome model, coverage denominators, sample/seconds alignment, resolved traces, load measures and tiered repeatability provide an auditable technical evaluation when supported by an oracle, fault tests and independent reporting audit.

## 6.4 Contribution and threats to validity

The common pipeline handled different rates, dimensions, formats and classes without dataset-specific rendering. KITTI’s lower source representation reflects retained/suppressed `DontCare`; MOT17’s dense output reflects many eligible observations. The contribution complements reusable sonification systems (Walker and Cothran, 2003; Peng and Choi, 2021; Trayford *et al.*, 2025) by joining tracking annotations to common events, provenance and predeclared evaluation; no comparative superiority was tested.

The cases are contrasting probes, not a benchmark comparison: native annotations, durations, policies and scenes differ, so dataset identity alone cannot explain the density gap. MOT17 stresses dense eligible observations; KITTI tests richer metadata and an explicit non-sonified class. Complete accounting in both supports the architecture claim, while their load profiles expose where later policies require evaluation.

**Construct validity.** Accounting, alignment, traceability and reproduction measure pipeline properties, not intelligibility. Density/overlap measure load, and source representation depends on class policy.

**Internal validity.** Pipeline and evaluator share conventions, so a common error could inflate agreement. The independent oracle, injected faults, negative tests, frozen contract and reporting audit mitigate but cannot eliminate this risk. One mapping prevents attribution of load to individual design choices.

**External validity.** One sequence from each of two tracking datasets, one renderer and no participant population limit generalisation. Other modalities may require schema extensions.

**Conclusion validity.** Complete coverage does not imply good sound design; zero sample error does not imply perceptual simultaneity. Informal researcher difficulty with dense overlaps (R20) is not participant evidence, and no comparative condition supports improvement claims.

**Reproducibility validity.** Repeated packages, audio and reports support determinism only in the recorded environment. CI on Ubuntu tests non-private code but not the retained data/audio chain; cross-platform byte identity remains untested.

Finally, each observation is mapped independently. Track aggregation, priority, refractory periods or polyphony limits may reduce density, but require new technical comparisons and participant work for human-centred conclusions.
