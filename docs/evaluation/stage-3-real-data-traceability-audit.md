# Stage 3 real-data traceability audit

This audit resolves technical record links only. It does not assess subjective audio quality or support perceptual, accessibility, usability, navigation or safety claims.

## mot17 mot17-02-dpm

All selected-chain checks passed: `true`. The first peak-concurrency interval begins at sample 546840 with 203 active cues.

### Represented selections

| Rule | Event | Source row | Cue | Sample range | Checks |
|---|---|---:|---|---|---|
| first_represented | `evt:mot17:mot17-02-dpm:f000000:t1:r000001` | 1 | `cue:0d756012a5f30018bb16c3d9` | [0, 5292) | true |
| middle_represented_lower_middle | `evt:mot17:mot17-02-dpm:f000309:t13:r006188` | 6188 | `cue:a5d58c925a212c8bfdeae3f3` | [454230, 459522) | true |
| final_represented | `evt:mot17:mot17-02-dpm:f000599:t9:r004255` | 4255 | `cue:3a76de3ea91f2b7fbe8b704c` | [880530, 885822) | true |
| maximum_scheduling_error | `evt:mot17:mot17-02-dpm:f000481:t10:r004737` | 4737 | `cue:50408478e6d0da96427082d6` | [707070, 712362) | true |
| maximum_render_placement_error | `evt:mot17:mot17-02-dpm:f000481:t10:r004737` | 4737 | `cue:50408478e6d0da96427082d6` | [707070, 712362) | true |
| active_at_first_peak_concurrency_interval | `evt:mot17:mot17-02-dpm:f000372:t52:r023040` | 23040 | `cue:00b94bbad1c7eed0981e59bc` | [546840, 552132) | true |

### Suppressed selections

| Rule | Event | Source row | Code | Checks |
|---|---|---:|---|---|
| first_intentionally_suppressed | `evt:mot17:mot17-02-dpm:f000000:t4:r001232` | 1232 | `class_excluded` | true |
| final_intentionally_suppressed | `evt:mot17:mot17-02-dpm:f000599:t75:r029752` | 29752 | `class_excluded` | true |
| first_class_excluded | `evt:mot17:mot17-02-dpm:f000000:t4:r001232` | 1232 | `class_excluded` | true |

## kitti_tracking 0000

All selected-chain checks passed: `true`. The first peak-concurrency interval begins at sample 612990 with 24 active cues.

### Represented selections

| Rule | Event | Source row | Cue | Sample range | Checks |
|---|---|---:|---|---|---|
| first_represented | `evt:kitti_tracking:0000:f000000:t0:r000003` | 3 | `cue:57907e99497be6095e8ca03c` | [0, 5292) | true |
| middle_represented_lower_middle | `evt:kitti_tracking:0000:f000115:t1:r000655` | 655 | `cue:82c6c4e1093eaa50313665da` | [507150, 512442) | true |
| final_represented | `evt:kitti_tracking:0000:f000153:t9:r001084` | 1084 | `cue:a822c8230e50e300a0736ad4` | [674730, 680022) | true |
| maximum_scheduling_error | `evt:kitti_tracking:0000:f000000:t0:r000003` | 3 | `cue:57907e99497be6095e8ca03c` | [0, 5292) | true |
| maximum_render_placement_error | `evt:kitti_tracking:0000:f000000:t0:r000003` | 3 | `cue:57907e99497be6095e8ca03c` | [0, 5292) | true |
| active_at_first_peak_concurrency_interval | `evt:kitti_tracking:0000:f000139:t1:r000908` | 908 | `cue:101f5418b2282568d1f38653` | [612990, 618282) | true |

### Suppressed selections

| Rule | Event | Source row | Code | Checks |
|---|---|---:|---|---|
| first_intentionally_suppressed | `evt:kitti_tracking:0000:f000000:t-1:r000001` | 1 | `dont_care_excluded` | true |
| final_intentionally_suppressed | `evt:kitti_tracking:0000:f000153:t-1:r001080` | 1080 | `dont_care_excluded` | true |
| first_dont_care_excluded | `evt:kitti_tracking:0000:f000000:t-1:r000001` | 1 | `dont_care_excluded` | true |

The machine-readable audit records the logical source file, source hash and row; common event; preset and mapping methods; cue schedule identity; render-log sample range; WAV hash; suppression rule; and each individual validation result.
