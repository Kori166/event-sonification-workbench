# Stage 4 Milestone 1 Phase 3: Cross-Dataset Completion and Release Preparation

## Status

Implementation in progress under Issue #37 from clean `main` at
`16e20e811d4ed654fe60e36f2769b9884ad871ae`.

## Frozen scope

Decision 0018 freezes Phase 3 as retained-evidence assembly and cross-dataset verification through
Workbench Session Contract `0.1.0`. The same validated-session, immutable inspection-model,
loopback-service and browser-client path will expose only:

- MOT17 session `session-mot17-mot17-02-dpm-3707826663b210c6`; and
- KITTI Tracking session `session-kitti_tracking-0000-9cae092175c68109`.

No Stage 1 parsing/normalisation, Stage 2 scheduling/rendering or Stage 3 evaluation logic is added
to the workbench. No accepted research output will be regenerated or modified.

## Audited retained KITTI evidence

The existing Stage 3 manifest identifies retained KITTI Tracking sequence `0000` evidence with
1,089 valid events, 711 cues, 378 `dont_care_excluded` suppressions and 711 rendered cues. The exact
retained WAV SHA-256 is
`9fe11798dfaca388f10af21c346d49efa3507c1879ae2fff50e2a7d6d7d5e6ce`. The verified Stage 3 report
is `evaluation-kitti_tracking-0000-d997cdc8f6467c1d`, with repository report SHA-256
`b5589590a8c645bd7b5654d0318bf90fdb412f987719c26c2374bf3e487f9ff2`.

The runtime media binding is logical path `training/image_02/0000` below
`KITTI_TRACKING_ROOT`. The retained evidence records 154 zero-based 1242 by 375 PNG frames at 10 fps.
Private dataset/package roots and media remain outside Git.

## Acceptance evidence

Implementation, automated/private validation, controlled browser acceptance, privacy audit, hosted
CI, PR and release-candidate merge evidence will be added here as each gate is actually completed.

