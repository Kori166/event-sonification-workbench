# Stage 3 Dataset Results Summary

This section compares the two retained evaluation cases, `MOT17-02-DPM` and KITTI Tracking sequence `0000`.

Both were processed using the same Technical Evaluation Contract `0.1.0`, common event schema `0.2.0`, baseline preset `0.1.0` and renderer `0.1.0`.

The two sequences are different in size, frame rate, scene type and annotation structure. The results are therefore a descriptive comparison only. They do not show that one dataset is better than the other.

## Accounting, Coverage And Density

| Measure | MOT17-02-DPM | KITTI 0000 |
|---|---:|---:|
| Valid source events | 30,003 | 1,089 |
| Events represented by cues | 26,960 | 711 |
| Intentionally suppressed events | 3,043 | 378 |
| Missed eligible events | 0 | 0 |
| Accounting completeness | 100% | 100% |
| Eligible event coverage | 100% | 100% |
| Source representation | 89.86% | 65.29% |
| Suppression rate | 10.14% | 34.71% |
| Evaluated duration | 20.09 s | 15.42 s |
| Cue count | 26,960 | 711 |
| Cues per second | 1,342.18 | 46.11 |
| Cues per minute | 80,531.03 | 2,766.54 |
| Maximum cue starts within one second | 1,500 | 116 |

MOT17 suppressions were recorded as `class_excluded`. KITTI suppressions were recorded as `dont_care_excluded`, preserving the original `DontCare` annotations before excluding them from sound.

A suppression is therefore an intentional processing decision. It is not a missed event.

## Timing Alignment

All cues in both datasets were placed at the correct audio sample positions.

The maximum scheduling, rendering and end to end error was 0 samples for both datasets.

KITTI also recorded zero timing difference when measured in seconds.

MOT17 contained very small differences when the same timing was represented as decimal seconds. The largest was approximately 0.00000033 seconds. These differences came from numerical representation and did not change the actual audio sample positions.

| MOT17 Timing Measure | Cues Checked | Maximum Difference |
|---|---:|---:|
| Scheduling | 26,960 | approximately 0.00000033 s |
| Render placement | 26,960 | approximately 0.00000033 s |
| End to end | 26,960 | approximately 0.0000000000000017 s |

The evaluation rules were fixed before these results were produced. No timing threshold, formula or denominator was changed after seeing the dataset results.

## Traceability

All generated cues and suppressions could be traced back through the retained evidence.

| Traceability Check | MOT17-02-DPM | KITTI 0000 |
|---|---:|---:|
| Cue linked to event | 100% | 100% |
| Cue linked to source annotation | 100% | 100% |
| Cue linked to rendered sample range | 100% | 100% |
| Fully traceable cues | 100% | 100% |
| Traceable suppressions | 100% | 100% |
| Broken links | 0 | 0 |
| Cue linked to mapping rule | 100% | 100% |
| Cue linked to schedule | 100% | 100% |
| Cue linked to WAV evidence | 100% | 100% |

The final three checks are additional evidence audits rather than separate measures defined by Technical Evaluation Contract `0.1.0`.

They confirm that cue identifiers, source rows, configuration hashes, schedule records and rendered sample ranges agree across the retained processing chain.

## Overlap And Audio Load

Both datasets contained overlapping cues throughout their rendered audio.

| Measure | MOT17-02-DPM | KITTI 0000 |
|---|---:|---:|
| Peak simultaneous cues | 203 | 24 |
| Overlap duration | 20.09 s | 15.42 s |
| Timeline containing overlap | 100% | 100% |
| Excess concurrent cue seconds | 3,215.11 | 69.90 |
| Normalised overlap burden | 160.06 | 4.53 |

MOT17 produced much denser and more heavily overlapping audio than KITTI.

These values describe the technical output of the fixed baseline mapping. They do not show whether listeners would find either output understandable, comfortable or useful.

## Repeatability

Each dataset was processed twice through Stage 2.

For both datasets, the repeated runs produced the same:

* configuration
* event records
* cue and suppression records
* package bytes
* audio bytes

The technical evaluator was then run three times for each dataset. The resulting reports contained the same values and were byte identical within the recorded environment.

The repeated report hashes were:

| Dataset | Report SHA-256 |
|---|---|
| MOT17-02-DPM | `d847e805d0b2d7ccd50cd315bbcecfc0ad525f40e7c4c2013938f955d20f13e5` |
| KITTI Tracking 0000 | `b5589590a8c645bd7b5654d0318bf90fdb412f987719c26c2374bf3e487f9ff2` |

## Interpretation

The large differences between MOT17 and KITTI can be influenced by factors including:

* sequence size and duration
* frame rate
* number of objects
* object classes
* native annotation rules
* confidence and visibility information
* KITTI `DontCare` observations
* dataset specific class mappings
* application of the fixed sonification preset

The results should therefore not be interpreted as evidence that one dataset is higher quality than the other.

The evaluation supports technical findings about event accounting, timing, traceability, cue density, overlap and repeatability within the recorded execution environment.

It does not provide participant evidence and does not support claims about perceptual effectiveness, usability, accessibility, navigation, mobility or safety. It also does not establish byte identical reproducibility across different operating systems or execution environments.