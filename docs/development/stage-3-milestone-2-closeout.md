# Stage 3 Milestone 2 Close-out

## Outcome

Stage 3 Milestone 2 is complete on 6 August 2026. Frozen technical-evaluation contract `0.1.0` was applied unchanged to one verified real sequence from each dataset: MOT17-02-DPM and KITTI Tracking 0000. Three isolated evaluator repetitions per dataset produced semantically identical and byte-identical canonical reports in the recorded environment.

This is technical case-study evidence. RQ3 is now supported by real accounting, timing, traceability, density, overlap and reproducibility evidence, bounded by the selected sequences, baseline preset `0.1.0`, baseline renderer `0.1.0` and tested environment. No human-participant or perceptual evidence exists, and no accessibility, usability, navigation, mobility or safety claim is supported.

## Repository and frozen identities

- Repository base: `c1b3d6764c5b376462768d49e9721879a4dc0c73`.
- Branch: `stage-3-real-data-evaluation`.
- Protocol commit: `62269f7`.
- Experiment-manifest commits: `542839d`, with native/common sequence clarification `76146b6`.
- Assembler and integrity-test commits: `7f88666` and `8ef57aa`.
- Environment commit: `4084e15`.
- MOT17 evidence commit: `38eb4ac`.
- KITTI evidence commit: `96f0268`.
- Lossless summary correction commit: `4531bda`.
- Excluded-evidence inventory commit: `1c7d390`.
- Traceability/cross-dataset audit commit: `e3f28b4`.
- Experiment manifest SHA-256: `320e0054c670fe5fd4c422aff52d5f9cada49853073e0d5bed9fcbabf1bc2733`.
- Path-free environment manifest SHA-256: `02c902984008d0499ad1b2f3f5bae4fef54937f51ff9de4450a5c6aae32fa949`.
- Evaluation contract SHA-256: `68513164a731d977988acc34f7013cc3000c78d5e6aa345b2f7bcbe3e346de3e`.
- Contract schema SHA-256: `05dcb1c0fb92f4ca577b755985056e0551aaadb99355bfefb783181378a3e85b`.
- Report schema SHA-256: `bc6be639a9f1939e5797572a405f8cc5b426691da0407d33c3347368cede1b6f`.
- Event schema `0.2.0` SHA-256: `a78a6d9a97c9257741678dcbb9422153026507f64f8010a6366122ce72397680`.
- Preset `0.1.0` SHA-256: `27f9b4e031e12fe9e73e72275aa7359b5255e2f997a35fb2432372dcbd843289`.
- Renderer `0.1.0` SHA-256: `1c741306f67633543f9f16de557173662005c8c21c4a911fb4bcf8bbde18770b`.

The environment record contains Windows 11, AMD64, CPython 3.14.3, pytest 9.1.1, Ruff 0.16.1, jsonschema 4.26.0, UK locale and the environment-variable names `MOT17_ROOT`, `KITTI_TRACKING_ROOT` and `STAGE2_EVIDENCE_ROOT`. It contains no value or physical path. No dependency lock file exists; the manifest records the `pyproject.toml` hash as the available fallback declaration.

## Source and package-integrity gate

Existing Stage 2 evidence was reused, not regenerated. Both independent chains were outside the dirty checkout, were not recovered from either stash and matched the complete Stage 2 close-out tables.

| Evidence | MOT17-02-DPM | KITTI 0000 |
|---|---|---|
| Logical source annotation | `MOT17/train/MOT17-02-DPM/gt/gt.txt` | `training/label_02/0000.txt` |
| Source SHA-256 | `2e3ecb488da8886d3200d402b2b08890c6d2879923839444e9b74fa43a551440` | `97f772a27181dfc7ef51b3e64b86bd42e682753b6855fdc58d259ecbed501fd4` |
| Event run ID | `run-mot17-mot17-02-dpm-03074d7ff016652e` | `run-kitti_tracking-0000-94a4cdc57ff00109` |
| Cue run ID | `cue-mot17-mot17-02-dpm-97bdca8f548747c7` | `cue-kitti_tracking-0000-cb42b67e49714a36` |
| Audio run ID | `audio-mot17-mot17-02-dpm-e55d5dc901d5572c` | `audio-kitti_tracking-0000-9472ddb1a4a87617` |
| Event package identity | `1e0ed932f3708be9e35e592361c8c937a583ee2b42b6abd61df8db8e5974bee9` | `1295e2fa2c4586308fdd0f4b75a36bd9a9b08a2218569a539a7b60a0f6dd15e2` |
| Cue package identity | `6000edf1a4f10dbdb00e85941ea08f3f7ce4257212b40aac47751dbb6318f0c9` | `49b5a778c3cefa694cc8d93fbc643bf088c5fbbe69b30aa201af43a76ec32ec0` |
| Audio package identity | `d3812fceea51fc04c575f1a3bdd23f61ec58b3cc46005d30cc078a315e8f0949` | `1bd13cd2e0272ca2b3f5365881e0e8dbddc88cff1c4c2675272b3f963ddb99b0` |
| WAV SHA-256 | `0d25af2972ac614790c50d8a86291e0642bb1f69caa751a6ab6189d335ed1ca3` | `9fe11798dfaca388f10af21c346d49efa3507c1879ae2fff50e2a7d6d7d5e6ce` |
| Stage 1 validation | 30,003 valid; 0 invalid; 0 errors; 988 permitted geometry warnings | 1,089 valid; 0 invalid; 0 errors; 0 warnings |
| Stage 2 accounting | 26,960 cues; 3,043 `class_excluded`; 0 unlinked or missed eligible | 711 cues; 378 `dont_care_excluded`; 0 unlinked or missed eligible |
| Integrity result | All 12 package files matched in run A and run B | All 12 package files matched in run A and run B |

Exact membership, canonical JSON, LF-stable CSV, physical hashes, package identities, source/configuration hashes, ordering, accounting, render links and renderer metadata all passed. The full 60-file ignored-evidence inventory is committed as `docs/evaluation/evidence/excluded-local-evidence.json` with SHA-256 `4557983c22fa0ee41661c7ecc714fa94ceab6313d169a630ef35f7ec8d88a038`.

## Evaluator input and execution

| Evidence | MOT17-02-DPM | KITTI 0000 |
|---|---:|---:|
| Input ID | `evaluation-input-mot17-mot17-02-dpm-3ea20501b41b31f6` | `evaluation-input-kitti_tracking-0000-1429cceacb2300f9` |
| Input bytes | 80,747,281 | 3,159,143 |
| Input SHA-256 | `718c452d51d943628bf191ff59ff71a2bbe59c8545c05b0d06180c76dccc2fdd` | `bfbc9c339abc7dca3f8a118d2698da20e2bb34fc15863cbcce5c74878ef3cf0e` |
| Input-manifest SHA-256 | `20a403845fcc504da9e15a770ae74db478c0372ba9241a082748de041e81901b` | `078a93065665e32a91d07d298d309e8781448f683dd138a196ea7b1aa79f0c23` |
| Evaluation run ID | `evaluation-mot17-mot17-02-dpm-2636a438409d649e` | `evaluation-kitti_tracking-0000-d997cdc8f6467c1d` |
| Report bytes | 5,077,477 | 189,730 |
| Canonical report SHA-256 | `d847e805d0b2d7ccd50cd315bbcecfc0ad525f40e7c4c2013938f955d20f13e5` | `b5589590a8c645bd7b5654d0318bf90fdb412f987719c26c2374bf3e487f9ff2` |
| Embedded report-core SHA-256 | `dec7edb403657b7638e444ac5c19e4480b660baa6c4601c5a4d0b1edff66cfbe` | `d2e7ed5147cd74143381cc8e4d9fd94d16f5a69969fef503f4f252b17cdcb713` |

The assembler consumed the existing package files, preserved source file/row and record links, referenced WAV identity without embedding audio, and refused missing, unexpected or mismatching package evidence. The input documents remain ignored; their path-free hash manifests are committed.

Path-free command templates used were:

```text
python -m event_sonification_workbench.cli prepare-technical-evaluation --event-package <event-package> --cue-package <cue-package> --audio-package <audio-package> --repeat-event-package <repeat-event-package> --repeat-cue-package <repeat-cue-package> --repeat-audio-package <repeat-audio-package> --output <isolated-evaluation-input>
python -m event_sonification_workbench.cli evaluate-technical --input <technical-evaluation-input> --output <isolated-report>
python -m event_sonification_workbench.technical_evaluation_evidence --prefix <dataset-prefix> --report <run-01-report> --report <run-02-report> --report <run-03-report> --input <technical-evaluation-input> --input-manifest <input-manifest> --experiment-manifest configs/evaluation/stage-3-real-data-evaluation-v0.1.0.json --environment-manifest configs/evaluation/stage-3-real-data-environment-v0.1.0.json --preset configs/sonification/presets/baseline-v0.1.0.json --report-schema configs/evaluation/technical-evaluation-report.schema.v0.1.0.json --output-directory <empty-evidence-directory>
```

## Complete technical results

### Event accounting and coverage

| Measure | MOT17-02-DPM | KITTI 0000 |
|---|---:|---:|
| Valid events | 30,003 | 1,089 |
| Eligible events | 26,960 | 711 |
| Represented | 26,960 | 711 |
| Intentionally suppressed | 3,043 | 378 |
| Missed eligible | 0 | 0 |
| Explicitly excluded | 0 | 0 |
| Duplicate outcome / contradictory outcome | 0 / 0 | 0 / 0 |
| Unresolved / orphan cue / orphan suppression | 0 / 0 / 0 | 0 / 0 / 0 |
| Accounting completeness | 30,003 / 30,003 = 1.0 | 1,089 / 1,089 = 1.0 |
| Eligible-event coverage | 26,960 / 26,960 = 1.0 | 711 / 711 = 1.0 |
| Source representation | 26,960 / 30,003 = 0.8985768089857681 | 711 / 1,089 = 0.6528925619834711 |
| Suppression | 3,043 / 30,003 = 0.10142319101423192 | 378 / 1,089 = 0.34710743801652894 |
| Missed eligible | 0 / 26,960 = 0.0 | 0 / 711 = 0.0 |

### Timing alignment

Every sample-domain minimum, maximum, mean, median and p95 was `0.0` for all three domains and both datasets. Observation counts were 26,960 for MOT17 and 711 for KITTI. KITTI's second-domain statistics were also all `0.0`. MOT17's complete seconds statistics were:

| Domain | Minimum | Maximum | Mean | Median | P95 |
|---|---:|---:|---:|---:|---:|
| Scheduling | 0.0 | 3.33333335e-07 | 2.2226755693066802e-07 | 3.33333333e-07 | 3.33333334e-07 |
| Render placement | 0.0 | 3.3333333333333335e-07 | 2.222675568743818e-07 | 3.3333333333333335e-07 | 3.3333333333333335e-07 |
| End to end | 0.0 | 1.66666666667e-15 | 3.292202027694528e-16 | 3.3333333333e-16 | 1.33333333333e-15 |

Decimal round-half-up sample placement, nearest-rank p95 and contract median semantics were unchanged.

### Traceability

Contract cue-to-event, cue-to-source-annotation, cue-to-rendered-sample and fully traceable cue rates were 26,960 / 26,960 = 1.0 for MOT17 and 711 / 711 = 1.0 for KITTI. Suppression traceability was 3,043 / 3,043 = 1.0 and 378 / 378 = 1.0. Broken-link groups were empty. Supplemental resolved-link audits for mapping rule, cue schedule and WAV were also 1.0 for every cue and remain explicitly outside the frozen contract fields.

The deterministic audit selected first, lower-middle and final represented events; maximum scheduling and placement error; an event active at the first peak interval; first/final suppressions; a MOT17 class exclusion; and a KITTI `DontCare` suppression. Every selected source, row, event, preset/mapping, cue, schedule, render range, WAV hash and suppression link agreed.

### Density and overlap

| Measure | MOT17-02-DPM | KITTI 0000 |
|---|---:|---:|
| Rendered duration (seconds) | 20.086666666666666 | 15.42 |
| Cue count | 26,960 | 711 |
| Cues/second | 1342.1838698971126 | 46.10894941634241 |
| Cues/minute | 80531.03219382676 | 2766.536964980545 |
| Maximum starts in `[t,t+1)` | 1,500 | 116 |
| Peak concurrency | 203 | 24 |
| Overlap duration (seconds) | 20.086666666666666 | 15.42 |
| Overlap proportion | 20.086666666666666 / 20.086666666666666 = 1.0 | 15.42 / 15.42 = 1.0 |
| Excess concurrent cue-seconds | 3215.1133333333332 | 69.9 |
| Normalised overlap burden | 3215.1133333333332 / 20.086666666666666 = 160.0620643876535 | 69.9 / 15.42 = 4.533073929961089 |

Overlap uses rendered integer samples, half-open `[start,end)` intervals and end-before-start boundary ordering. Density and overlap values describe the configured output; they do not measure listener benefit or difficulty.

## Reproducibility results

For each dataset:

- the two retained event/cue/audio chains matched in configuration identity, semantic records, exact package bytes and audio bytes;
- all three evaluation run IDs were identical;
- all three parsed reports were semantically identical;
- all three physical canonical report files were byte-identical and had the same SHA-256;
- the generated summaries, CSVs, comparison reports, input manifests and selected-record audits repeated byte-for-byte in separate evidence builds; and
- the bounded result is `identical_in_recorded_environment`.

Comparison-report SHA-256 is `a21990ef56e1e82516babf248c7ac782384ba39cb88b896a25fc30da2a8b38b7` for MOT17 and `42205454e27c1df71669e1d2b75c1928d2986232e46ed4e48fb08c4d9940dd79` for KITTI. The claim does not extend to an untested operating system, architecture, Python runtime, preset or renderer.

## Quality evidence

All commands resolved imports from this worktree's `src` directory. Actual final results:

| Command | Exit | Passed | Failed | Skipped | Deselected |
|---|---:|---:|---:|---:|---:|
| `python -m ruff check .` | 0 | n/a | 0 | n/a | n/a |
| `python -m pytest tests/test_technical_evaluation.py -q` | 0 | 26 | 0 | 0 | 0 |
| `python -m pytest -m "not integration"` | 0 | 231 | 0 | 0 | 3 |
| `python -m pytest -m integration` | 0 | 3 | 0 | 0 | 231 |
| `python -m pytest` | 0 | 234 | 0 | 0 | 0 |

The integration run took 339.26 seconds and actually executed all three private tests. The full suite took 307.69 seconds. No type checker is configured, so no type-check result is claimed.

## Problems and corrections

- The first private evaluation integration invocation exceeded a four-minute shell limit and was terminated without a pytest result. The unchanged focused test was rerun with a longer bound and passed in 261.12 seconds; the final required integration and full runs also completed successfully.
- An initial MOT17 evaluator invocation used an output argument containing `..`. The safe writer rejected it after calculation with `evaluation_output_path_unsafe`; no report was written or counted. All six accepted repetitions used resolved regular output paths.
- The package model exposed native `MOT17-02-DPM` versus common `mot17-02-dpm` sequence identity. The experiment manifest/schema was corrected before accepted assembly or metric evidence, in focused commit `76146b6`.
- A pre-correction KITTI input assembly was retained locally as superseded evidence. It was not used for evaluation; its files and hashes appear in the excluded-evidence manifest.
- The first generated KITTI summary referred to a dataset-derived report filename rather than the emitted prefix. The evidence writer was corrected and all affected summaries were regenerated twice. A later losslessness review added the full diagnostics array; both datasets were again generated twice and matched exactly.
- No real-data result exposed a contract defect. Contract `0.1.0`, its report schema, oracle and formulas were not altered.

## Committed and excluded evidence

Committed evidence includes the protocol; experiment/schema and environment manifests; package assembler and tests; one canonical report per dataset; JSON, fixed-column CSV and Markdown summaries; input hash manifests; three-run comparisons; machine-readable and Markdown traceability audits; a cross-dataset summary; Decision 0014; and this close-out.

The following remain ignored and uncommitted: raw MOT17/KITTI data, private roots, both full Stage 2 chains, full event/cue packages, WAV files, 80.7 MB/3.16 MB evaluator inputs, all isolated repeat directories, temporary evidence-build directories and the superseded assembly. Their 60 retained evidence files have exact sizes, hashes, command templates and logical relative locations in the excluded-evidence manifest. No `.env`, image, video or audio file is committed.

## Limitations and RQ3 boundary

- One sequence per dataset is a bounded case study and is not representative of every MOT17 or KITTI sequence.
- MOT17 and KITTI differ in frame rate, annotation conventions, class semantics, visibility/confidence conventions, geometry and `DontCare` handling; descriptive values are not rankings.
- Results apply to the fixed baseline preset and renderer, not to arbitrary sonification designs.
- MOT17's 988 Stage 1 geometry warnings were permitted and preserved; evaluation diagnostics were 0 errors and 0 warnings for both datasets.
- Exact report/package/audio repetition is established only in the recorded environment. Cross-environment audio or report byte identity is untested.
- No participant, perception, accessibility, usability, navigation, mobility or safety evidence exists.

## Next milestone

**Stage 3 Milestone 3: convert the verified technical-evaluation evidence into audited report-ready tables, figures and bounded RQ3 findings, with every presented value linked to its canonical source report.**
