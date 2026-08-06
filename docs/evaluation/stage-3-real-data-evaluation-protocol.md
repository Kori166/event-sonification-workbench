# Stage 3 Real-Data Technical-Evaluation Protocol

## Purpose and frozen method

Stage 3 Milestone 2 applies the already reviewed technical-evaluation contract to the verified
Stage 2 evidence chains for one MOT17 sequence and one KITTI Tracking sequence. The metric
definitions were fixed before either real-data result was calculated. Contract thresholds,
denominators, time references, percentile rules and interval boundaries will not be changed in
response to the observed values.

The normative identities are:

| Item | Version | SHA-256 |
|---|---:|---|
| Technical-evaluation contract | 0.1.0 | `68513164a731d977988acc34f7013cc3000c78d5e6aa345b2f7bcbe3e346de3e` |
| Technical-evaluation report schema | 0.1.0 | `bc6be639a9f1939e5797572a405f8cc5b426691da0407d33c3347368cede1b6f` |
| Common event schema | 0.2.0 | `a78a6d9a97c9257741678dcbb9422153026507f64f8010a6366122ce72397680` |
| Baseline sonification preset | 0.1.0 | `27f9b4e031e12fe9e73e72275aa7359b5255e2f997a35fb2432372dcbd843289` |
| Baseline audio renderer | 0.1.0 | `1c741306f67633543f9f16de557173662005c8c21c4a911fb4bcf8bbde18770b` |

The repository base is `c1b3d6764c5b376462768d49e9721879a4dc0c73`. Contract `0.1.0` remains
unchanged. Any implementation correction must enforce that contract; a genuine method or schema
defect triggers the stop-and-version policy below.

## Selected evidence chains

The sequences are fixed by the earlier Stage 1 and Stage 2 close-outs rather than selected after
inspecting evaluation values.

| Dataset | Sequence | Logical annotation | Source SHA-256 | Event run | Cue run | Audio run |
|---|---|---|---|---|---|---|
| MOT17 | MOT17-02-DPM | `MOT17/train/MOT17-02-DPM/gt/gt.txt` | `2e3ecb488da8886d3200d402b2b08890c6d2879923839444e9b74fa43a551440` | `run-mot17-mot17-02-dpm-03074d7ff016652e` | `cue-mot17-mot17-02-dpm-97bdca8f548747c7` | `audio-mot17-mot17-02-dpm-e55d5dc901d5572c` |
| KITTI Tracking | 0000 | `training/label_02/0000.txt` | `97f772a27181dfc7ef51b3e64b86bd42e682753b6855fdc58d259ecbed501fd4` | `run-kitti_tracking-0000-94a4cdc57ff00109` | `cue-kitti_tracking-0000-cb42b67e49714a36` | `audio-kitti_tracking-0000-9472ddb1a4a87617` |

These are bounded case studies. MOT17 and KITTI Tracking are not equivalent experimental
populations, and neither selected sequence represents every sequence in its dataset. Comparisons
are descriptive only.

## Package availability and integrity gate

Two independently generated Stage 2 chains per dataset are available beneath an ignored local
evidence root outside the dirty original checkout. They were not recovered from a stash. Before
assembly, the evaluator must:

1. require exact four-file event, five-file cue and three-file audio package membership;
2. verify canonical JSON/CSV projections and all physical SHA-256 values;
3. recompute content-derived event, cue and audio identities;
4. verify cross-stage run IDs, package hashes, configuration hashes, counts and ordering;
5. compare the two chains byte-for-byte and by independently calculated SHA-256; and
6. verify the native source hashes through `MOT17_ROOT` and `KITTI_TRACKING_ROOT` without recording
   either physical root.

The complete expected file-hash tables are frozen in the experiment manifest and originate from
`docs/development/stage-2-closeout.md`. A run ID or count match alone is insufficient. Any missing,
extra, non-canonical, mismatching or unsafe file stops evaluation. Existing evidence is reused only
when every gate passes; otherwise two new chains must be generated in new isolated directories by
`mot17-package`/`kitti-package`, `schedule-cues`, `render-audio` and `compare-packages`.

## Assembly and execution

The package-chain assembler joins verified Stage 1 events, Stage 2 cues/suppressions and Stage 2
render records into the existing frozen evaluator input model. It does not remap events, reschedule
cues, rerender audio or embed WAV bytes. It preserves source file/row, cue/event links, preset and
mapper evidence, integer rendered sample ranges and the WAV identity. Output is canonical,
deterministically ordered, path-free and content identified.

Local evidence uses this ignored layout:

```text
.local-fixtures/stage-3-real-data-evaluation/
  mot17/{source-chain-a,source-chain-b,evaluation-run-01,evaluation-run-02,evaluation-run-03}/
  kitti/{source-chain-a,source-chain-b,evaluation-run-01,evaluation-run-02,evaluation-run-03}/
```

Each dataset uses two independently generated Stage 2 chains and three evaluator executions into
separate empty directories. The three canonical reports are compared semantically, byte-for-byte
and by SHA-256. Existing two-chain event/cue/audio evidence is reused when verified; WAV rendering
is not repeated merely to test deterministic report generation.

The exact command sequence is recorded in the Milestone 2 close-out. The execution environment is
captured in a committed path-free manifest containing the evaluator-code commit, platform/runtime,
dependency specification hash, relevant tool versions, locale, timezone, frozen configuration
identities and only the names of private-root environment variables.

## Hash scopes

Generated JSON, CSV, metadata, report and WAV files use their existing exact-byte and canonical
package contracts. Binary evidence is always byte-hashed. The LF-normalised text rule belongs only
to the explicitly documented synthetic-oracle fixture manifest; it is not reused for real package
files or generated evaluation evidence.

## Failure policies

An integrity mismatch is retained, classified by its first diverging stage and investigated before
either dataset evaluation continues. Failed outputs are not overwritten or deleted merely because
a later run succeeds. The smallest synthetic regression case is added for any implementation
defect, followed by all affected local and real-data reruns.

If real packages expose an ambiguity, incompatible assumption, calculation error or schema defect
in the frozen method, both dataset evaluations stop. Current outputs are preserved, the defect is
classified and documented, a synthetic regression and manual-oracle update are prepared, and a
new contract version is reviewed before evaluation restarts from empty directories. Contract
`0.1.0` is never silently mutated. An implementation correction that only enforces existing
contract text is documented separately and does not itself change the contract version.

## Evidence boundary and prohibited interpretation

The evaluation may establish only technical accounting, placement, traceability, density, overlap
and tested-environment repeat evidence for the fixed chains. Differences can reflect frame rate,
duration, annotation conventions, object density, geometry, class semantics, confidence or
visibility fields, KITTI `DontCare`, dataset-specific class mappings and the fixed baseline preset.

No metric establishes accessibility, usability, navigation, perceptual effectiveness, mobility,
safety or suitability for visually impaired people. High coverage is not perceptual superiority;
exact timing is not listener usefulness; lower density or overlap is not easier or more accessible.
No inferential statistical test, dataset ranking or cross-environment byte-identity claim is made.
