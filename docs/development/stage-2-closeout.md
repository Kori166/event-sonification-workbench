# Stage 2 Close-out

- Date completed: 6 August 2026.
- Evidence commit: `488e4eb70c8faf7527b327926b3b2ebc4e1af957` (`origin/main` after PR #22).
- Common event schema: `0.2.0`.

## Status and scope

Stage 2 is complete. The workbench now consumes validated Stage 1 event packages, applies a
versioned deterministic preset, accounts for every event as a cue or coded suppression, and renders
verified cue packages to deterministic stereo PCM16 WAV, render-log and renderer-metadata outputs.

PR #22, `Stage 2: add deterministic WAV rendering`, merged on 5 August 2026. Its GitHub Actions CI
run 59 completed successfully, and Issue #21 closed through the merge. Milestone 1 had previously
merged through PR #20. This close-out adds no evaluation metric, threshold, perceptual claim or
participant result.

## Evidence environment

- Operating system: Windows `10.0.26200`.
- Architecture: AMD64.
- Python: `3.14.3`, 64-bit, MSC `v.1944`.
- Project package: `0.1.0`.
- pytest: `9.1.1`; Ruff: `0.16.1`.
- Private source roots were supplied at runtime through `MOT17_ROOT` and `KITTI_TRACKING_ROOT`.
  They were readable for every real-data command and integration test but are not recorded here.
- All generated evidence was written beneath ignored `.local-fixtures/` directories. No generated
  event, cue, WAV, image, video, private dataset or physical path is committed.

The following shared versioned configuration was used:

| Configuration | Version | SHA-256 |
|---|---:|---|
| Common event schema | 0.2.0 | `a78a6d9a97c9257741678dcbb9422153026507f64f8010a6366122ce72397680` |
| Baseline sonification preset | 0.1.0 | `27f9b4e031e12fe9e73e72275aa7359b5255e2f997a35fb2432372dcbd843289` |
| Sonification-preset schema | 0.1.0 | `a906f873f2c5237d5e27977656a19af74986a73ce7b73f9fb9feb38413fe4a58` |
| Baseline audio renderer | 0.1.0 | `1c741306f67633543f9f16de557173662005c8c21c4a911fb4bcf8bbde18770b` |
| Audio-renderer schema | 0.1.0 | `420fd001904be08b81f33c9c078de9ccce7fb5b4ae93cd07d5bd97dc27d8aea8` |

The event-package, cue-package, mapper, rendering-policy and renderer-metadata formats are all
version `0.1.0`. Both dataset parsers and class mappings are version `0.1.0`.

## Procedure

Two independent directory trees were used for each dataset. Each tree ran the public CLI from the
native private annotation through all three package stages:

1. `mot17-package` or `kitti-package` parsed, collection-validated and wrote the Stage 1 package.
2. `schedule-cues` independently verified that package and wrote the five-file cue package.
3. `render-audio` independently verified the cue package and wrote the WAV package.
4. `compare-packages` compared the two independently generated packages at each stage using exact
   bytes and independently calculated SHA-256 values.

The comparison command was added during close-out because no reusable package comparison utility
existed. It recognises only the exact event, cue and audio package file contracts, emits a stable
path-free report, identifies each mismatching filename and pair of hashes, and returns nonzero for a
difference.

## MOT17 real-data result

- Sequence: `MOT17-02-DPM`.
- Logical annotation: `MOT17/train/MOT17-02-DPM/gt/gt.txt`.

| Field | Result |
|---|---|
| Event run ID | `run-mot17-mot17-02-dpm-03074d7ff016652e` |
| Cue run ID | `cue-mot17-mot17-02-dpm-97bdca8f548747c7` |
| Audio run ID | `audio-mot17-mot17-02-dpm-e55d5dc901d5572c` |
| Source annotation SHA-256 | `2e3ecb488da8886d3200d402b2b08890c6d2879923839444e9b74fa43a551440` |
| Sequence metadata SHA-256 | `5c9a86813ed1e4bf640b11785e9dc51f443712d721f9cc5e334b7e0f21606ad6` |
| Class-mapping SHA-256 | `1bd22ee6b313396a16589ae10356e7de569546872ef4a4687a9610cbbb29aeac` |
| Validation | valid; 30,003 valid, 0 invalid, 0 errors, 988 warnings |
| Cue accounting | 30,003 events = 26,960 cues + 3,043 `class_excluded` suppressions |
| Render accounting | 26,960 scheduled cues = 26,960 rendered cues |
| WAV | 44,100 Hz, stereo, signed PCM16 LE, 885,822 frames, 20.086666666666666 s |
| Peak policy | pre-gain 4.160643703858928; gain 0.2283300536210036; target peak 0.95 applied |
| Stored PCM peak | 31,130 / 32,767 (`0.9500411999877926`) after integer quantisation |

MOT17 event-package file hashes:

| File | SHA-256 |
|---|---|
| `events.json` | `880232f6ea0696a8c74600f51fe46e8221ff8ee40536dbef4570921a8779b96e` |
| `events.csv` | `2b4b5e3dac8e70661719b555fc6578a088e8b3aa18758f99447d3137dd43f3ee` |
| `run_metadata.json` | `e247260608d4aaac72f2b5d3e3a602ebe29d7b8e8d2dedd10a2320b6456c7bee` |
| `provenance_log.json` | `6b44534de1c9ffb9f1f4b7f2d033fa954e08c4dab219e68d8333ef649f55ae5f` |

MOT17 cue-package file hashes:

| File | SHA-256 |
|---|---|
| `cue_schedule.json` | `01591926b4c0b33f7760c081483fd1434b431ca419780a9fee6eb2530ec185a4` |
| `cue_schedule.csv` | `bf61b4b35696f00cad3cc885e97105c498d16d1d65db1c75ad7bbff2ec7cc0fa` |
| `cue_log.json` | `806bffa4cb9cff9ff9d6816b6a17395d82748979daa2cee55d9f668b543b0c23` |
| `suppression_log.json` | `f589c1730f3aa3f3eaf90d60ffeb3f3618faa81679049b6e3a2019089e81dace` |
| `sonification_metadata.json` | `f5a1f66153ea0b61aa25367b78ed1e7fa03499eae2a5e2425e2dec5751fc23ba` |

MOT17 audio-package file hashes:

| File | SHA-256 |
|---|---|
| `sonification.wav` | `0d25af2972ac614790c50d8a86291e0642bb1f69caa751a6ab6189d335ed1ca3` |
| `render_log.json` | `d7f1b7b27e44e4d3fe89d52d40a51e02673595527a1a8840edde8b94b382d181` |
| `renderer_metadata.json` | `18dcdf9fd482a3ca41c27aa63432ca276bf3fb4f7458f579a5c3010af67a8691` |

The 988 warnings are permitted native bounding boxes extending beyond declared image bounds. The
parser preserves that geometry and the validator reports it; the warnings are not hidden or counted
as errors.

## KITTI Tracking real-data result

- Sequence: `0000`.
- Logical annotation: `training/label_02/0000.txt`.

| Field | Result |
|---|---|
| Event run ID | `run-kitti_tracking-0000-94a4cdc57ff00109` |
| Cue run ID | `cue-kitti_tracking-0000-cb42b67e49714a36` |
| Audio run ID | `audio-kitti_tracking-0000-9472ddb1a4a87617` |
| Source annotation SHA-256 | `97f772a27181dfc7ef51b3e64b86bd42e682753b6855fdc58d259ecbed501fd4` |
| Class-mapping SHA-256 | `49ff366b6768ab3803dd0dd125c7ad2092a0eff298400485dd6b311c612c1b14` |
| Validation | valid; 1,089 valid, 0 invalid, 0 errors, 0 warnings |
| Cue accounting | 1,089 events = 711 cues + 378 `dont_care_excluded` suppressions |
| Render accounting | 711 scheduled cues = 711 rendered cues |
| WAV | 44,100 Hz, stereo, signed PCM16 LE, 680,022 frames, 15.42 s |
| Peak policy | pre/post peak 0.7689207693607398; gain 1.0; no limiting required |
| Stored PCM peak | 25,196 / 32,767 (`0.7689443647572253`) after integer quantisation |

KITTI Tracking event-package file hashes:

| File | SHA-256 |
|---|---|
| `events.json` | `542389e4a783380191fdc228b83c37309fa4d483d58913978881ee3cfb6f57a2` |
| `events.csv` | `5068c491c8feace0ba39b91f9398e7b96b6310174c5d63b28a1792c4d8fb0db5` |
| `run_metadata.json` | `89cefd74709226303257f6c315368b75b8bb52e84c4c473c03f0f5bf9a37a47b` |
| `provenance_log.json` | `916703854628b24b0503a56f5bb754204691fe6aa517169fadb3dd5bc2968325` |

KITTI Tracking cue-package file hashes:

| File | SHA-256 |
|---|---|
| `cue_schedule.json` | `96200af25ae04c67294b29a320d86f82b87927a4e23eeb24633a60b8e5b94d19` |
| `cue_schedule.csv` | `b7e941de4c234951edb95fbf6c2335bb1cdc20b82569c6e97249a25b38ac7147` |
| `cue_log.json` | `2acb5e711d4359fd675e21f732b46a15e1344c475836dbf05632e309a37bd503` |
| `suppression_log.json` | `3787ae6f34fb4003c52ba9827d4342670e48e7b27f77023cadaba88fdeb592cc` |
| `sonification_metadata.json` | `d966fb544422d4cf637210c4a0fe0fea6dcd5008107f1794665b8fece4574093` |

KITTI Tracking audio-package file hashes:

| File | SHA-256 |
|---|---|
| `sonification.wav` | `9fe11798dfaca388f10af21c346d49efa3507c1879ae2fff50e2a7d6d7d5e6ce` |
| `render_log.json` | `cfe4fd3a24eedcbc90a45d08a44b900d3e64cc2fa9a26f20081adc1a78a9ee06` |
| `renderer_metadata.json` | `56d6f53ca2fc93e97887cf2c46fc144e10ec81b5ba7e4a9f8f539b9eb1eb704a` |

## Reproducibility and traceability findings

Both independent runs reproduced the same three run IDs for their dataset. For each dataset:

- all four event-package files were byte-identical and hash-identical;
- all five cue-package files were byte-identical and hash-identical;
- all three audio-package files were byte-identical and hash-identical;
- deterministic event ordering was unchanged;
- the physical source annotation hash, declared configuration hashes and every cross-stage input
  hash matched an independent calculation;
- event and cue package loaders revalidated exact file membership, canonical content, identities,
  counts, order and recorded hashes;
- event IDs and cue IDs were unique;
- every source event appeared exactly once across cue and suppression records;
- eligible events without cues: `0`; cues without source events: `0`;
- cue log projections matched the complete schedules;
- every cue or suppression source file/row matched its source event;
- every render-log cue ID and source-event ID matched the schedule; and
- scans of generated content found no configured private root, username or OneDrive marker.

The results support deterministic repeatability in the environment above. They do not establish
byte identity on a different operating system, architecture, Python/libm implementation or future
renderer version.

## Quality checks

Commands were run from the repository root on 6 August 2026:

| Command | Actual result |
|---|---|
| `python -m ruff check .` | Passed with no findings |
| `python -m pytest -m "not integration"` | 184 passed, 2 deselected |
| `python -m pytest -m integration` | 2 passed, 184 deselected; no private-data skip |
| Cue-scheduling/renderer/comparison focused tests | 55 passed |
| `python -m pytest` | 186 passed; no skips |

## Problems encountered and actions

- No reusable exact package comparator existed. The small `compare-packages` utility and six focused
  tests were added; no dependency was introduced.
- An evidence-audit command initially referenced the two configuration schemas under incorrect
  repository subdirectories. The audit was corrected and rerun; all independently calculated
  configuration hashes then matched package metadata. No generated-package defect was found.
- Full MOT17 conversion and rendering took materially longer than fixture tests. Both independent
  runs were allowed to finish against the full sequence; no sample or cached first-run output was
  substituted.
- Unrelated local interface, launcher and ignore-file work was present before close-out. It was
  preserved locally and excluded from this work's intended change set.

## Limitations

- The preset and renderer are technical reference configurations, not validated perceptual,
  accessibility, navigation, usability or safety designs.
- `class_modifier` remains trace-only in rendering policy `0.1.0`.
- MOT17's 988 permitted geometry warnings remain visible evidence, not corrected annotations.
- Private datasets and complete generated derivatives remain unavailable to CI and are not
  distributable through this repository.
- Cross-platform PCM equality remains untested beyond the recorded Windows/AMD64/Python runtime.
- Stage 3 evaluation measures, thresholds, reports and findings do not exist yet.

## Completion decision

Stage 2 completion criteria are satisfied: both real Stage 1 collections validate under schema
`0.2.0`; versioned mapping gives complete cue/suppression accounting; verified cue packages render
to WAV/log/metadata; source, configuration and output hashes form an unbroken chain; repeated full
runs are byte-identical; all available tests pass; and assumptions and limitations are documented.

Stage 3 is the next active stage. No sonification implementation change or evaluation result is
claimed by this status transition.

## Stage 3 handover

Stage 3 may consume only verified Stage 2 package contracts:

- Stage 1 `events.json`, `events.csv`, `run_metadata.json` and `provenance_log.json`;
- Stage 2 cue schedule, cue log, suppression log and sonification metadata;
- Stage 2 WAV, render log and renderer metadata; and
- the exact preset, renderer and schemas identified by version and SHA-256 above.

Before computing results, evaluation code must preserve three distinct accounting categories:

1. **Intentionally suppressed events** have a source event and a coded suppression record. They are
   policy outcomes, not missing cues.
2. **Eligible events without cues** are source events appearing in neither the cue schedule nor the
   suppression log. They are pipeline/accounting defects, not intentional suppression.
3. **Unlinked cues** are cue records whose `source_event_id` does not resolve to an input event. They
   are traceability defects.

Initial Stage 3 metric groups are coverage/accounting, temporal alignment, cue density and overlap,
traceability completeness, and repeat-run reproducibility. Stage 3 must define exact formulas,
denominators, units and controlled fixtures before calculating them. It must not turn technical
measures into perceptual, participant, accessibility or safety claims.
