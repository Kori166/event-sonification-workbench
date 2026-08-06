# Stage 3 cross-dataset technical summary

This is a descriptive comparison of two bounded case studies: MOT17-02-DPM and KITTI Tracking sequence 0000. Both used the frozen technical-evaluation contract 0.1.0, common event schema 0.2.0, baseline preset 0.1.0 and baseline renderer 0.1.0. The sequences are not equivalent experimental populations, and no inferential test or better/worse ranking is supported.

## Accounting, coverage and density

| Measure | MOT17-02-DPM | KITTI 0000 |
|---|---:|---:|
| Valid source events | 30,003 | 1,089 |
| Represented events | 26,960 | 711 |
| Intentionally suppressed events | 3,043 | 378 |
| Eligible but missed events | 0 | 0 |
| Explicitly excluded events | 0 | 0 |
| Accounting completeness | 30,003 / 30,003 = 1.0 | 1,089 / 1,089 = 1.0 |
| Eligible-event coverage | 26,960 / 26,960 = 1.0 | 711 / 711 = 1.0 |
| Source-representation rate | 26,960 / 30,003 = 0.8985768089857681 | 711 / 1,089 = 0.6528925619834711 |
| Suppression rate | 3,043 / 30,003 = 0.10142319101423192 | 378 / 1,089 = 0.34710743801652894 |
| Missed-eligible rate | 0 / 26,960 = 0.0 | 0 / 711 = 0.0 |
| Evaluated duration (seconds) | 20.086666666666666 | 15.42 |
| Cue count | 26,960 | 711 |
| Cues per second | 1342.1838698971126 | 46.10894941634241 |
| Cues per minute | 80531.03219382676 | 2766.536964980545 |
| Maximum starts in a half-open one-second window | 1,500 | 116 |

MOT17 suppressions were `class_excluded` records from the fixed preset. KITTI suppressions were `dont_care_excluded` records, preserving and then explicitly filtering native `DontCare` annotations. Intentionally suppressed events are therefore not missed events.

## Timing alignment

All sample-domain scheduling, render-placement and end-to-end errors were zero for both sequences. KITTI's second-domain values were also zero. MOT17 retained very small second-domain decimal differences while still placing every cue at the contract-defined decimal-round-half-up sample:

| MOT17 second-domain statistic | Count | Minimum | Maximum | Mean | Median | P95 |
|---|---:|---:|---:|---:|---:|---:|
| Scheduling | 26,960 | 0.0 | 3.33333335e-07 | 2.2226755693066802e-07 | 3.33333333e-07 | 3.33333334e-07 |
| Render placement | 26,960 | 0.0 | 3.3333333333333335e-07 | 2.222675568743818e-07 | 3.3333333333333335e-07 | 3.3333333333333335e-07 |
| End to end | 26,960 | 0.0 | 1.66666666667e-15 | 3.292202027694528e-16 | 3.3333333333e-16 | 1.33333333333e-15 |

The frozen contract uses absolute differences, nearest-rank p95, the midpoint median for even counts and decimal round-half-up sample placement. No threshold or denominator was changed after seeing these results.

## Traceability

| Link | MOT17-02-DPM | KITTI 0000 |
|---|---:|---:|
| Cue to event | 26,960 / 26,960 = 1.0 | 711 / 711 = 1.0 |
| Cue to source annotation | 26,960 / 26,960 = 1.0 | 711 / 711 = 1.0 |
| Cue to rendered sample | 26,960 / 26,960 = 1.0 | 711 / 711 = 1.0 |
| Fully traceable cue | 26,960 / 26,960 = 1.0 | 711 / 711 = 1.0 |
| Traceable suppression | 3,043 / 3,043 = 1.0 | 378 / 378 = 1.0 |
| Broken links | 0 | 0 |
| Supplemental cue-to-mapping-rule audit | 26,960 / 26,960 = 1.0 | 711 / 711 = 1.0 |
| Supplemental cue-to-schedule audit | 26,960 / 26,960 = 1.0 | 711 / 711 = 1.0 |
| Supplemental cue-to-WAV audit | 26,960 / 26,960 = 1.0 | 711 / 711 = 1.0 |

The final three rows are resolved-link audits over the prepared package evidence; they are clearly separated because they are not additional fields in contract 0.1.0. The deterministic record selections and agreeing identifiers, source rows, hashes and sample ranges are recorded in the traceability audit.

## Overlap burden

Both calculations use rendered integer sample intervals with half-open boundaries `[start, end)` and end-before-start ordering at equal boundaries.

| Measure | MOT17-02-DPM | KITTI 0000 |
|---|---:|---:|
| Peak concurrency | 203 | 24 |
| Overlap duration (seconds) | 20.086666666666666 | 15.42 |
| Overlap proportion | 20.086666666666666 / 20.086666666666666 = 1.0 | 15.42 / 15.42 = 1.0 |
| Excess concurrent cue-seconds | 3215.1133333333332 | 69.9 |
| Normalised overlap burden | 3215.1133333333332 / 20.086666666666666 = 160.0620643876535 | 69.9 / 15.42 = 4.533073929961089 |

These values describe the fixed baseline output. They do not establish whether either density or overlap pattern is understandable, useful or accessible to a listener.

## Reproducibility and bounded interpretation

For each dataset, the two retained Stage 2 chains matched in configuration, semantic records, package bytes and audio bytes. The evaluator then produced three semantically identical and byte-identical reports in the recorded environment. MOT17's repeated report SHA-256 is `d847e805d0b2d7ccd50cd315bbcecfc0ad525f40e7c4c2013938f955d20f13e5`; KITTI's is `b5589590a8c645bd7b5654d0318bf90fdb412f987719c26c2374bf3e487f9ff2`.

The large descriptive differences can arise from native annotation conventions, sequence duration, frame rate, object density, class semantics, confidence and visibility conventions, MOT17 geometry extending beyond image bounds, KITTI `DontCare` records, dataset-specific class mappings and application of the fixed preset. They cannot be attributed to dataset quality or listener outcomes from these two sequences.

The evidence supports technical statements about accounting, configured timing, traceable records, density, overlap and same-environment deterministic execution. It supplies no human-participant or perceptual evidence and supports no accessibility, usability, navigation, mobility or safety claim.
