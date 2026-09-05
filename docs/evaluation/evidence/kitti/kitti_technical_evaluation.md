# kitti_tracking 0000 technical evaluation

Report SHA-256: `b5589590a8c645bd7b5654d0318bf90fdb412f987719c26c2374bf3e487f9ff2`.

The contract report is **valid**. It accounts for 1089 valid events: 711 represented, 378 intentionally suppressed, 0 eligible but missed, and 0 explicitly excluded.

| Measure | Numerator | Denominator | Value |
|---|---:|---:|---:|
| accounting_completeness | 1089 | 1089 | 1.0 |
| eligible_event_coverage | 711 | 711 | 1.0 |
| source_representation_rate | 711 | 1089 | 0.6528925619834711 |
| suppression_rate | 378 | 1089 | 0.34710743801652894 |
| missed_eligible_event_rate | 0 | 711 | 0.0 |

## Timing alignment

| Domain | Unit | Count | Min | Max | Mean | Median | P95 |
|---|---|---:|---:|---:|---:|---:|---:|
| scheduling | seconds | 711 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| scheduling | samples | 711 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| render_placement | seconds | 711 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| render_placement | samples | 711 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| end_to_end | seconds | 711 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| end_to_end | samples | 711 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |

## Traceability, density, overlap and repeatability

All 711 of 711 cues were fully traceable under contract 0.1.0. Supplemental mapping-rule, schedule and WAV link checks are reported separately and do not extend the contract.

The 15.42-second rendered timeline contains 711 cues (46.10894941634241 cues/second; 2766.536964980545 cues/minute). Peak concurrency is 24; overlap duration is 15.42 seconds and normalised overlap burden is 4.533073929961089.

Three isolated evaluator reports were semantically equal and byte-equal: `identical_in_recorded_environment`.

## Interpretation boundary

Technical case-study evidence for one sequence, preset, renderer and recorded environment; no perceptual, accessibility, usability, navigation or safety claim.
