# Stage 3 Evaluation Protocol

## Evaluation Purpose And Fixed Rules

Stage 3 applies the existing technical evaluation method to one retained MOT17 sequence and one retained KITTI Tracking sequence.

The evaluation rules were fixed before either real dataset was evaluated. Measures, denominators, timing rules and calculation methods were not changed after seeing the results.

The fixed versions used were:

| Item | Version | SHA-256 |
|---|---:|---|
| Technical Evaluation Contract | 0.1.0 | `68513164a731d977988acc34f7013cc3000c78d5e6aa345b2f7bcbe3e346de3e` |
| Evaluation report schema | 0.1.0 | `bc6be639a9f1939e5797572a405f8cc5b426691da0407d33c3347368cede1b6f` |
| Common event schema | 0.2.0 | `a78a6d9a97c9257741678dcbb9422153026507f64f8010a6366122ce72397680` |
| Baseline sonification preset | 0.1.0 | `27f9b4e031e12fe9e73e72275aa7359b5255e2f997a35fb2432372dcbd843289` |
| Baseline audio renderer | 0.1.0 | `1c741306f67633543f9f16de557173662005c8c21c4a911fb4bcf8bbde18770b` |

The repository base was:

`c1b3d6764c5b376462768d49e9721879a4dc0c73`

Technical Evaluation Contract `0.1.0` remained unchanged. A coding correction could be made if it only enforced the existing contract. Any genuine change to the evaluation method required a new contract version.

## Selected Dataset Cases

The two sequences were chosen during the earlier project stages, before their evaluation results were known.

| Dataset | Sequence | Source Annotation | Source SHA-256 | Event Run | Cue Run | Audio Run |
|---|---|---|---|---|---|---|
| MOT17 | MOT17-02-DPM | `MOT17/train/MOT17-02-DPM/gt/gt.txt` | `2e3ecb488da8886d3200d402b2b08890c6d2879923839444e9b74fa43a551440` | `run-mot17-mot17-02-dpm-03074d7ff016652e` | `cue-mot17-mot17-02-dpm-97bdca8f548747c7` | `audio-mot17-mot17-02-dpm-e55d5dc901d5572c` |
| KITTI Tracking | 0000 | `training/label_02/0000.txt` | `97f772a27181dfc7ef51b3e64b86bd42e682753b6855fdc58d259ecbed501fd4` | `run-kitti_tracking-0000-94a4cdc57ff00109` | `cue-kitti_tracking-0000-cb42b67e49714a36` | `audio-kitti_tracking-0000-9472ddb1a4a87617` |

These are two bounded case studies. They do not represent every sequence in MOT17 or KITTI Tracking and are not treated as equivalent experimental groups.

Any comparison between them is descriptive only.

## Checking The Retained Evidence

Two independently generated Stage 2 evidence chains were retained for each dataset.

Before evaluation, the following checks were required:

1. Confirm that each event package contains exactly four expected files.

2. Confirm that each cue package contains exactly five expected files.

3. Confirm that each audio package contains exactly three expected files.

4. Verify all JSON, CSV and physical file hashes.

5. Recalculate the event, cue and audio run identities.

6. Check that run IDs, package hashes, configuration hashes, counts and ordering agree across stages.

7. Compare the two retained chains using exact file bytes and independently calculated SHA-256 values.

8. Verify the original MOT17 and KITTI source hashes using `MOT17_ROOT` and `KITTI_TRACKING_ROOT` without recording the physical local paths.

A matching run ID or event count alone was not considered sufficient evidence.

Evaluation stopped if a package contained missing files, unexpected files, incorrect hashes, invalid content or unsafe paths.

If retained evidence failed these checks, new evidence chains had to be generated in separate directories using:

`mot17-package`

`kitti-package`

`schedule-cues`

`render-audio`

`compare-packages`

## Preparing And Running The Evaluation

The evaluator combines verified Stage 1 events with Stage 2 cues, suppressions and render records.

It does not:

* remap events
* reschedule cues
* regenerate audio
* modify the retained WAV
* calculate replacement research evidence

The assembled evaluation input preserves source file and row references, event and cue links, preset information, mapping evidence, rendered sample ranges and WAV identity.

The resulting evidence is deterministically ordered, free from local machine paths and identified by its content.

The local evidence structure was:

```text
.local-fixtures/stage-3-real-data-evaluation/

  mot17/
    source-chain-a/
    source-chain-b/
    evaluation-run-01/
    evaluation-run-02/
    evaluation-run-03/

  kitti/
    source-chain-a/
    source-chain-b/
    evaluation-run-01/
    evaluation-run-02/
    evaluation-run-03/
  
  Each dataset used two independently generated Stage 2 chains.

The evaluator was then run three times into separate empty directories. The resulting reports were compared by:

reported values
exact file bytes
SHA-256 values

Existing verified event, cue and audio evidence was reused. The WAV files were not regenerated simply to test whether the evaluator produced repeatable reports.

The execution environment was also recorded without storing private paths. This included the code version, operating environment, dependencies, relevant tool versions, locale, timezone and fixed configuration identities.

## Hashing Rules

Generated JSON, CSV, metadata, evaluation reports and WAV files use their existing hashing rules.

Binary files such as WAV audio are always checked using their exact bytes.

The special text normalisation rule used for the earlier synthetic test fixture does not apply to real dataset packages or generated evaluation reports.

## Failure Handling

Any integrity problem had to be investigated before evaluation continued.

Failed outputs were retained rather than deleted simply because a later run succeeded. This preserves evidence of what happened during development.

If a coding defect was found, a small synthetic regression test was added before the affected evaluation was repeated.

If the real dataset evidence revealed a problem with the evaluation method itself, both dataset evaluations had to stop.

The problem would then be documented and tested using the synthetic case. A new Technical Evaluation Contract version would be required before real dataset evaluation restarted.

Contract 0.1.0 was therefore never changed silently after results had been observed.

## Interpretation Limits

The evaluation can support technical findings about:

event accounting and coverage
timing alignment
traceability
cue density
audio overlap
repeatability within the recorded environment

Differences between MOT17 and KITTI may result from their different frame rates, sequence lengths, annotation rules, object densities, classes, geometry and visibility information. They may also result from KITTI DontCare records, dataset specific class mappings and the fixed sonification preset.

These results do not show that one dataset is better than the other.

They also do not provide evidence about perceptual effectiveness, usability, accessibility, navigation, mobility or safety.

High event coverage does not show that the audio is understandable. Exact timing does not show that the audio is useful to a listener. Lower cue density or overlap does not show that the output is easier to understand.

No statistical ranking between the datasets is made, and byte identical reproducibility across different execution environments is not claimed.