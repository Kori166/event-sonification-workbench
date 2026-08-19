# Stage 5 Phase A Evidence Baseline

This document fixes the reporting baseline for the dissertation. Repository records and committed
canonical evidence take precedence over proposals, interim presentations and uncommitted drafts.
The baseline is descriptive: it does not reopen Stages 1-4 or authorise new experiments.

## 1. Baseline identity

| Field | Baseline | Evidence |
|---|---|---|
| Repository | `Kori166/event-sonification-workbench` | [`CITATION.cff`](../../CITATION.cff), [`README.md`](../../README.md) |
| Branch | `main`, aligned with `origin/main` before Phase A edits | Git status inspected 18 August 2026 |
| Final Stage 0-4 record commit | `e177c39ee7b5496591b29ae965bba82bbb39a908` | Git log; this documentation-only commit records Stage 4 close-out |
| Stage 4 implementation merge | `b6c8310c9f8a731d2ef374e725ba6f99342e85e1` | [`stage-4-milestone-2.md`](../development/stage-4-milestone-2.md), [`stage-4-checklist.md`](../project-management/stage-4-checklist.md) |
| Baseline date | 18 August 2026 | Commit timestamp and Stage 4 close-out records |
| Release/tag | No Git tag is present. `0.1.0` is the project/package release version and the Stage 4 records call the merged artefact a release candidate. | `git tag --list` (empty), [`pyproject.toml`](../../pyproject.toml), [`CITATION.cff`](../../CITATION.cff), [`project-plan.md`](../project-management/project-plan.md) |

The repository root configured for this task was an empty OneDrive folder. The actual clean checkout
was located at `Documents/GitHub/event-sonification-workbench`; all statements and Phase A files use
that checkout. No implementation or retained experimental output was changed.

## 2. Versioned contracts and configuration

| Component | Version | Evidence |
|---|---:|---|
| Project/package | `0.1.0` | [`pyproject.toml`](../../pyproject.toml), [`CITATION.cff`](../../CITATION.cff) |
| Event schema | `0.2.0` | [`event.schema.v0.2.0.json`](../../configs/schemas/event.schema.v0.2.0.json), both retained session declarations |
| Event-package format | `0.1.0` | [`stage-2-closeout.md`](../development/stage-2-closeout.md), retained declarations |
| MOT17 parser/class mapping | `0.1.0` / `0.1.0` | [`stage-1-closeout.md`](../development/stage-1-closeout.md), [`mot17.v0.1.0.json`](../../configs/class-mappings/mot17.v0.1.0.json) |
| KITTI parser/class mapping | `0.1.0` / `0.1.0` | [`stage-1-closeout.md`](../development/stage-1-closeout.md), [`kitti_tracking.v0.1.0.json`](../../configs/class-mappings/kitti_tracking.v0.1.0.json) |
| Workbench Session Contract | `0.1.0` | [`workbench-session.schema.v0.1.0.json`](../../configs/workbench/workbench-session.schema.v0.1.0.json), [`workbench-session.md`](../data-model/workbench-session.md) |
| Retained-session catalogue | `0.1.0` | [`retained-sessions.v0.1.0.json`](../../configs/workbench/retained-sessions.v0.1.0.json) |
| Mapping preset | baseline `0.1.0` | [`baseline-v0.1.0.json`](../../configs/sonification/presets/baseline-v0.1.0.json); SHA-256 `27f9b4e031e12fe9e73e72275aa7359b5255e2f997a35fb2432372dcbd843289` in retained declarations |
| Cue-package format | `0.1.0` | retained declarations and [`stage-2-closeout.md`](../development/stage-2-closeout.md) |
| Renderer | baseline `0.1.0` | [`baseline-v0.1.0.json`](../../configs/sonification/renderers/baseline-v0.1.0.json); SHA-256 `1c741306f67633543f9f16de557173662005c8c21c4a911fb4bcf8bbde18770b` |
| Evaluation contract/report | `0.1.0` / `0.1.0` | [`technical-evaluation-contract.v0.1.0.json`](../../configs/evaluation/technical-evaluation-contract.v0.1.0.json), canonical reports |
| Traceability audit | `0.1.0` | [`mot17_traceability_audit.json`](../evaluation/evidence/mot17/mot17_traceability_audit.json), [`kitti_traceability_audit.json`](../evaluation/evidence/kitti/kitti_traceability_audit.json) |

The baseline preset uses `frame_stride: 1`; it is the only evaluated preset. Event timestamps set cue
start time, horizontal centre sets stereo pan, inverted vertical centre sets frequency and bounding-box
area sets amplitude. `class_modifier` values are logged for traceability but renderer policy `0.1.0`
does not apply them. [`baseline-v0.1.0.json`](../../configs/sonification/presets/baseline-v0.1.0.json)
and [`audio-rendering.md`](../data-model/audio-rendering.md) are authoritative.

## 3. Canonical evaluation cases

### MOT17

| Evidence layer | Canonical identity or location |
|---|---|
| Dataset/sequence | MOT17, `MOT17-02-DPM`; logical input `MOT17/train/MOT17-02-DPM/gt/gt.txt`; source SHA-256 `2e3ecb488da8886d3200d402b2b08890c6d2879923839444e9b74fa43a551440` |
| Inspection session | `session-mot17-mot17-02-dpm-3707826663b210c6`; [`mot17-phase-2-session.v0.1.0.json`](../../configs/workbench/mot17-phase-2-session.v0.1.0.json) |
| Stage 1 | `run-mot17-mot17-02-dpm-03074d7ff016652e`; four-file event package (`events.json`, `events.csv`, `run_metadata.json`, `provenance_log.json`); 30,003 valid events, 0 errors, 988 permitted geometry warnings |
| Stage 2 cues | `cue-mot17-mot17-02-dpm-97bdca8f548747c7`; 26,960 cues and 3,043 `class_excluded` suppressions |
| Stage 2 render | `audio-mot17-mot17-02-dpm-e55d5dc901d5572c`; WAV SHA-256 `0d25af2972ac614790c50d8a86291e0642bb1f69caa751a6ab6189d335ed1ca3` |
| Stage 3 report | `evaluation-mot17-mot17-02-dpm-2636a438409d649e`; [`mot17_technical_evaluation_report.json`](../evaluation/evidence/mot17/mot17_technical_evaluation_report.json); file SHA-256 `d847e805d0b2d7ccd50cd315bbcecfc0ad525f40e7c4c2013938f955d20f13e5` |
| Audit/reporting | [`mot17_traceability_audit.json`](../evaluation/evidence/mot17/mot17_traceability_audit.json), [`stage-3-report-evidence-manifest.json`](../evaluation/reporting/stage-3-report-evidence-manifest.json), [`manual-independent-audit.md`](../evaluation/reporting/audits/manual-independent-audit.md) |

### KITTI Tracking

| Evidence layer | Canonical identity or location |
|---|---|
| Dataset/sequence | KITTI Tracking, `0000`; logical input `training/label_02/0000.txt`; source SHA-256 `97f772a27181dfc7ef51b3e64b86bd42e682753b6855fdc58d259ecbed501fd4` |
| Inspection session | `session-kitti_tracking-0000-9cae092175c68109`; [`kitti-phase-3-session.v0.1.0.json`](../../configs/workbench/kitti-phase-3-session.v0.1.0.json) |
| Stage 1 | `run-kitti_tracking-0000-94a4cdc57ff00109`; same four-file contract; 1,089 valid events, 0 errors/warnings |
| Stage 2 cues | `cue-kitti_tracking-0000-cb42b67e49714a36`; 711 cues and 378 `dont_care_excluded` suppressions |
| Stage 2 render | `audio-kitti_tracking-0000-9472ddb1a4a87617`; WAV SHA-256 `9fe11798dfaca388f10af21c346d49efa3507c1879ae2fff50e2a7d6d7d5e6ce` |
| Stage 3 report | `evaluation-kitti_tracking-0000-d997cdc8f6467c1d`; [`kitti_technical_evaluation_report.json`](../evaluation/evidence/kitti/kitti_technical_evaluation_report.json); file SHA-256 `b5589590a8c645bd7b5654d0318bf90fdb412f987719c26c2374bf3e487f9ff2` |
| Audit/reporting | [`kitti_traceability_audit.json`](../evaluation/evidence/kitti/kitti_traceability_audit.json), reporting manifest and independent audit above |

The full Stage 1/2 packages, evaluator inputs and WAV files are intentionally ignored local evidence,
not committed artefacts. Their expected logical locations, byte sizes, hashes and retention status are
frozen in [`excluded-local-evidence.json`](../evaluation/evidence/excluded-local-evidence.json). The
retained session declarations bind those hashes to the Stage 4 inspection layer. They must not be
described as repository-hosted files.

The canonical Stage 3 numerical sources are the two `*_technical_evaluation_report.json` files.
CSV/Markdown summaries, three SVGs, captions and RQ3 prose are deterministic presentation derivatives.
The reporting package audited 134 manifested values, 136 table cells, 20 figure points and 12 claims
with zero remaining mismatches. [`manual-independent-audit.md`](../evaluation/reporting/audits/manual-independent-audit.md)
records the independent pass.

## 4. Verification state

- Stage 4 is complete. All 16 final researcher-controlled Firefox/Chrome checks passed for both
  sessions; this is engineering acceptance, not a participant or usability study.
- The final implementation head passed Ruff, JavaScript syntax checking, 280 non-integration tests
  and three separately run retained private integrations. The accepted documentation head passed
  hosted CI with Ruff and 280 tests / 6 private integrations deselected; post-merge `main` CI run
  `32135202315` passed the same hosted gate. Evidence: [`stage-4-milestone-2.md`](../development/stage-4-milestone-2.md).
- CI installs on Ubuntu/Python 3.11, runs Ruff and the non-integration suite; private integrations are
  necessarily local. Evidence: [`.github/workflows/ci.yml`](../../.github/workflows/ci.yml).
- The pre-Phase-A worktree was clean and `main` matched `origin/main`. There is no Git tag.
- Open/controlled risks include MOT17 fixture redistribution (R9), cross-platform PCM identity (R14),
  dense-cue interpretation (R20) and bounding-box area interpretation (R21). Evidence:
  [`risk-register.md`](../project-management/risk-register.md).

## 5. Known evidence boundaries

The baseline does **not** establish:

- perceptual intelligibility, listener preference, usability, accessibility, navigation, mobility,
  clinical or safety benefit; no participant evaluation was conducted;
- superiority or optimality of a mapping: one baseline preset/renderer was evaluated and no
  alternative-preset, `frame_stride` or scheduler-ablation experiment was performed;
- generalisation across either dataset: only one selected sequence per dataset was technically
  evaluated, and the two sequences are not equivalent populations;
- complete semantic harmonisation: native ontologies and dataset-specific metadata are preserved;
- zero timing difference in every representation: sample placement error was zero, but MOT17 retained
  small non-zero decimal-seconds differences;
- that all valid events became cues: intentional suppression is a separate, successful accounting
  outcome, not a missed event;
- cross-platform byte reproducibility; equality was demonstrated only in the recorded environments;
- true depth from bounding-box area. Area is the frozen amplitude input and at most an imperfect
  apparent-scale proxy; R21 documents pose sensitivity;
- an audible effect from `class_modifier`; it is trace-only in renderer `0.1.0`;
- workbench generation or recomputation of evidence. Stage 4 is a local, read-only inspection layer
  over retained evidence and plays the retained WAV unchanged.

These boundaries follow [`rq3-findings.md`](../evaluation/reporting/rq3-findings.md),
[`README.md`](../../README.md), the Stage 4 records and R20/R21 in the risk register.
