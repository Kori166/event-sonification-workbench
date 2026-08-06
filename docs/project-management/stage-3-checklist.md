# Stage 3 Checklist

## Technical evaluation

Status: active. Milestone 1 method and synthetic-oracle gate completed on 6 August 2026. Milestone 2
real-data evaluation is next. RQ3 is not yet fully answered.

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

- [ ] Prepare evaluation inputs from verified Stage 1/2 MOT17 and KITTI Tracking packages without
  changing contract formulas.
- [ ] Verify all event, cue, suppression, render, WAV and configuration hashes before calculation.
- [ ] Run contract `0.1.0` for selected MOT17 and KITTI evidence chains.
- [ ] Write canonical dataset-level reports and repeat each run independently.
- [ ] Compare semantic records, exact report bytes, audio bytes and configuration identities.
- [ ] Record actual coverage, timing, traceability, density, overlap and diagnostic values.
- [ ] Investigate every miss, orphan, broken link, warning or repeat mismatch before interpretation.
- [ ] Run configured quality gates and available private integrations with no skipped test reported
  as a pass.
- [ ] Document environment-bounded findings and limitations without perceptual or participant
  claims.

## Evidence boundary

Milestone 1 proves that the implemented method matches a manually calculated synthetic case. It
does not establish real MOT17/KITTI metric values, answer RQ3 fully, validate perceived quality or
show cross-platform byte identity.
