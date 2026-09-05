# mot17 mot17-02-dpm technical evaluation

Report SHA-256: `d847e805d0b2d7ccd50cd315bbcecfc0ad525f40e7c4c2013938f955d20f13e5`.

The contract report is valid. It accounts for 30003 valid events with 26960 represented, 3043 intentionally suppressed, 0 eligible but missed, and 0 explicitly excluded.

| Measure | Numerator | Denominator | Value |
|---|---:|---:|---:|
| accounting_completeness | 30003 | 30003 | 1.0 |
| eligible_event_coverage | 26960 | 26960 | 1.0 |
| source_representation_rate | 26960 | 30003 | 0.8985768089857681 |
| suppression_rate | 3043 | 30003 | 0.10142319101423192 |
| missed_eligible_event_rate | 0 | 26960 | 0.0 |

## Timing Alignment

| Domain | Unit | Count | Min | Max | Mean | Median | P95 |
|---|---|---:|---:|---:|---:|---:|---:|
| scheduling | seconds | 26960 | 0.0 | 3.33333335e-07 | 2.2226755693066802e-07 | 3.33333333e-07 | 3.33333334e-07 |
| scheduling | samples | 26960 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| render_placement | seconds | 26960 | 0.0 | 3.3333333333333335e-07 | 2.222675568743818e-07 | 3.3333333333333335e-07 | 3.3333333333333335e-07 |
| render_placement | samples | 26960 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| end_to_end | seconds | 26960 | 0.0 | 1.66666666667e-15 | 3.292202027694528e-16 | 3.3333333333e-16 | 1.33333333333e-15 |
| end_to_end | samples | 26960 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |

## Traceability, density, overlap and repeatability

All 26960 of 26960 cues were fully traceable under contract 0.1.0. Supplemental mapping-rule, schedule and WAV link checks are reported separately and do not extend the contract.

The 20.086666666666666-second rendered timeline contains 26960 cues (1342.1838698971126 cues/second, 80531.03219382676 cues/minute). Peak concurrency is 203. Overlap duration is 20.086666666666666 seconds and normalised overlap burden is 160.0620643876535.

Three isolated evaluator reports were semantically equal and byte-equal: `identical_in_recorded_environment`.

## Scope of Results

Technical case study evidence for one sequence, preset, renderer and recorded environment. It does not guarantee that the product will be easy to see, simple to use, easy to navigate, or safe for everyday users.
