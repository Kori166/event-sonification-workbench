# Stage 3 Checklist

## Technical evaluation

Status: active. Milestones 1 and 2 completed on 6 August 2026. The frozen method has been verified
synthetically and applied to one verified real sequence from each dataset. RQ3 is supported by
bounded real technical evidence; Milestone 3 report-ready auditing is next.

## Milestone 1: contract and synthetic oracle

- [x] Confirm Stage 2 close-out and PR #23 merge on the clean Stage 3 base.
- [x] Freeze machine- and human-readable technical-evaluation contract `0.1.0`.
- [x] Define event outcomes, eligible coverage and supporting rates without confusing suppressions
  with misses.
- [x] Separate scheduling, render-placement and end-to-end timing in seconds and samples.
- [x] Define resolved-record traceability through event, annotation, preset, schedule, render and
  WAV/hash evidence.
- [x] Define a zero-based rendered timeline, half-open one-second density windows and null
  zero-duration values.
- [x] Define half-open overlap, deterministic boundary grouping, concurrency, overlap time and
  excess concurrent cue-seconds.
- [x] Separate semantic, byte, audio and configuration reproducibility evidence.
- [x] Create a project-authored five-event manual oracle with exact sample/interval calculations.
- [x] Add missed, orphan, conflicting-outcome, broken-provenance, timing and malformed fault cases.
- [x] Compare the complete evaluator result with the frozen golden report.
- [x] Prove repeated canonical reports are byte-identical with identical SHA-256.
- [x] Pass Ruff and every configured non-integration test/CI gate.
- [x] Keep real-data results, new presets, schema/parser/render changes and user-benefit claims out
  of the milestone.

## Milestone 2: selected real-data reports

- [x] Prepare evaluation inputs from verified Stage 1/2 MOT17 and KITTI Tracking packages without
  changing contract formulas.
- [x] Verify all event, cue, suppression, render, WAV and configuration hashes before calculation.
- [x] Run contract `0.1.0` for selected MOT17 and KITTI evidence chains.
- [x] Write canonical dataset-level reports and repeat each run independently.
- [x] Compare semantic records, exact report bytes, audio bytes and configuration identities.
- [x] Record actual coverage, timing, traceability, density, overlap and diagnostic values.
- [x] Investigate every miss, orphan, broken link, warning or repeat mismatch before interpretation.
- [x] Run configured quality gates and available private integrations with no skipped test reported
  as a pass.
- [x] Document environment-bounded findings and limitations without perceptual or participant
  claims.

## Milestone 3: audited report-ready evidence

- [ ] Link every presented table and figure value to its canonical source report and hash.
- [ ] Audit report-ready tables and figures against the committed JSON/CSV evidence.
- [ ] Convert the verified measures into bounded RQ3 findings without changing the frozen contract.
- [ ] Preserve explicit case-study, environment and non-perceptual interpretation limits.

## Evidence boundary

Milestone 1 proves that the implemented method matches a manually calculated synthetic case.
Milestone 2 adds technical case-study values for MOT17-02-DPM and KITTI sequence 0000 and supports
RQ3 within the selected sequences, preset, renderer and recorded environment. Neither milestone
validates perceived quality, accessibility, usability, navigation, safety or cross-platform byte
identity.

The exact next milestone is **Stage 3 Milestone 3: convert the verified technical-evaluation
evidence into audited report-ready tables, figures and bounded RQ3 findings, with every presented
value linked to its canonical source report.**
