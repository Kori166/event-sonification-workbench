# Stage 3 Traceability Audit

This audit checks whether selected cues and suppressions can be traced through the retained evidence.

It checks technical record links only. It does not assess audio quality and does not provide evidence about usability, accessibility, navigation or safety.

## MOT17 02 DPM

All selected traceability checks passed.

The first point of peak overlap begins at audio sample `546840`, where 203 cues are active at the same time.

### Checked Cues

| Selection | Event | Source Row | Cue | Sample Range | Result |
|---|---|---:|---|---|---|
| First represented event | `evt:mot17:mot17-02-dpm:f000000:t1:r000001` | 1 | `cue:0d756012a5f30018bb16c3d9` | `[0, 5292)` | Pass |
| Middle represented event | `evt:mot17:mot17-02-dpm:f000309:t13:r006188` | 6188 | `cue:a5d58c925a212c8bfdeae3f3` | `[454230, 459522)` | Pass |
| Final represented event | `evt:mot17:mot17-02-dpm:f000599:t9:r004255` | 4255 | `cue:3a76de3ea91f2b7fbe8b704c` | `[880530, 885822)` | Pass |
| Maximum scheduling error case | `evt:mot17:mot17-02-dpm:f000481:t10:r004737` | 4737 | `cue:50408478e6d0da96427082d6` | `[707070, 712362)` | Pass |
| Maximum render placement error case | `evt:mot17:mot17-02-dpm:f000481:t10:r004737` | 4737 | `cue:50408478e6d0da96427082d6` | `[707070, 712362)` | Pass |
| Cue active during first peak overlap | `evt:mot17:mot17-02-dpm:f000372:t52:r023040` | 23040 | `cue:00b94bbad1c7eed0981e59bc` | `[546840, 552132)` | Pass |

### Checked Suppressions

| Selection | Event | Source Row | Reason | Result |
|---|---|---:|---|---|
| First suppressed event | `evt:mot17:mot17-02-dpm:f000000:t4:r001232` | 1232 | `class_excluded` | Pass |
| Final suppressed event | `evt:mot17:mot17-02-dpm:f000599:t75:r029752` | 29752 | `class_excluded` | Pass |
| First class exclusion | `evt:mot17:mot17-02-dpm:f000000:t4:r001232` | 1232 | `class_excluded` | Pass |

## KITTI Tracking 0000

All selected traceability checks passed.

The first point of peak overlap begins at audio sample `612990`, where 24 cues are active at the same time.

### Checked Cues

| Selection | Event | Source Row | Cue | Sample Range | Result |
|---|---|---:|---|---|---|
| First represented event | `evt:kitti_tracking:0000:f000000:t0:r000003` | 3 | `cue:57907e99497be6095e8ca03c` | `[0, 5292)` | Pass |
| Middle represented event | `evt:kitti_tracking:0000:f000115:t1:r000655` | 655 | `cue:82c6c4e1093eaa50313665da` | `[507150, 512442)` | Pass |
| Final represented event | `evt:kitti_tracking:0000:f000153:t9:r001084` | 1084 | `cue:a822c8230e50e300a0736ad4` | `[674730, 680022)` | Pass |
| Maximum scheduling error case | `evt:kitti_tracking:0000:f000000:t0:r000003` | 3 | `cue:57907e99497be6095e8ca03c` | `[0, 5292)` | Pass |
| Maximum render placement error case | `evt:kitti_tracking:0000:f000000:t0:r000003` | 3 | `cue:57907e99497be6095e8ca03c` | `[0, 5292)` | Pass |
| Cue active during first peak overlap | `evt:kitti_tracking:0000:f000139:t1:r000908` | 908 | `cue:101f5418b2282568d1f38653` | `[612990, 618282)` | Pass |

### Checked Suppressions

| Selection | Event | Source Row | Reason | Result |
|---|---|---:|---|---|
| First suppressed event | `evt:kitti_tracking:0000:f000000:t-1:r000001` | 1 | `dont_care_excluded` | Pass |
| Final suppressed event | `evt:kitti_tracking:0000:f000153:t-1:r001080` | 1080 | `dont_care_excluded` | Pass |
| First `DontCare` exclusion | `evt:kitti_tracking:0000:f000000:t-1:r000001` | 1 | `dont_care_excluded` | Pass |

## What Was Checked

The full machine readable audit contains the detailed evidence behind these selections. For each relevant record it checks:

* source file and source hash
* source row
* common event
* sonification preset and mapping rule
* cue schedule
* rendered audio sample range
* WAV hash
* suppression reason where applicable
* result of each traceability check

The audit therefore confirms that the selected cues and suppressions can be followed through the retained processing evidence without broken links.