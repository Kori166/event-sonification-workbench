# Technical Evaluation Contract 0.1.0

## Purpose and evidence boundary

This contract fixes the Stage 3 technical measures before they are applied to real MOT17 or KITTI
Tracking packages. It measures record accounting, temporal placement, traceability, schedule
burden and exact repeat evidence. It does not measure or establish accessibility, usability,
navigation, perceptual effectiveness or safety.

The normative machine-readable policy is
`configs/evaluation/technical-evaluation-contract.v0.1.0.json`, validated by its adjacent schema.
Reports conform to `configs/evaluation/technical-evaluation-report.schema.v0.1.0.json`. Contract,
report and evaluator versions are independent and all begin at `0.1.0`.

## Required inputs

An evaluation needs validated common-schema `0.2.0` event records, cue-package `0.1.0` cue and
suppression records, renderer-metadata/render-log `0.1.0` records, and their package identities.
The identity includes dataset, sequence, event/cue/renderer versions, sample rate, rendered frame
count, event-package hash, preset hash, cue-schedule hash, suppression-log hash, render-log hash,
WAV hash when supplied, and renderer/evaluation configuration hashes. A missing optional WAV is
reported as absent evidence; a declared WAV whose hash cannot be resolved is a broken link.

Events supply event ID, timestamp, dataset/sequence, source annotation path/hash and source row.
Cues supply cue/source-event IDs, scheduled interval, matching source location and preset identity.
Suppressions supply source-event ID, coded reason, matching source location and preset identity.
Render entries supply cue/source-event IDs and integer start, duration and exclusive-end samples.
Identifiers must resolve to records whose linked fields agree; plausible text alone is not proof.

## Event accounting and eligibility

Every valid source event has one primary outcome: represented by one or more distinct cues,
intentionally suppressed by one explicit record, missed, or explicitly excluded before evaluation
by one validation record. Multiple cues for one event form one represented outcome. A cue and a
suppression for the same event, duplicate suppression/exclusion records, duplicate cue IDs, orphan
cues and references from suppressions/exclusions to unknown events are errors.

Under contract `0.1.0`, the Stage 2 mapper is total: any valid input event not explicitly
suppressed or excluded is cue-eligible. Such an event is represented when it has at least one cue
and missed when it has none. Suppressed events are never silently reclassified as missed.

Rates are objects containing `numerator`, `denominator` and `value`. A zero denominator always
produces `value: null` (not 0 or 1):

- cue-eligible coverage = represented eligible events / eligible events;
- source representation = unique represented events / valid source events;
- suppression = intentionally suppressed events / valid source events;
- accounting completeness = represented, suppressed or explicitly excluded events / valid source
  events; and
- missed-eligible rate = missed eligible events / eligible events.

## Timing alignment

For every resolvable cue, scheduling error is `abs(cue_start_seconds - event_timestamp_seconds)`.
For every resolvable render entry, render-placement error is
`abs(render_start_sample / sample_rate - cue_start_seconds)`, and end-to-end error is
`abs(render_start_sample / sample_rate - event_timestamp_seconds)`.

Sample errors compare integer positions after the renderer's existing decimal `ROUND_HALF_UP`
conversion: scheduling compares rounded cue and event times; render placement compares actual
start with rounded cue start; end-to-end compares actual start with rounded event time. Thus a
correctly rounded half-sample placement can have zero integer-sample error and a non-zero
seconds-domain quantisation difference. Cue ends remain exclusive.

Each domain reports count, minimum, maximum, arithmetic mean, median and p95. Empty summaries use
`null` for all five statistics. Median is the middle value or the arithmetic midpoint of the two
middle values. P95 uses nearest rank: sort ascending and select index `ceil(0.95*n)-1`.

## Timeline, density and overlap

The evaluated timeline begins at zero. Its preferred end is rendered total frame count divided by
sample rate, including recorded trailing silence. If render metadata is unavailable, the fallback
is the maximum scheduled half-open cue end; an empty schedule ends at zero.

Cue density is cue count / duration; per-minute density is the same rate multiplied by 60; unique
represented-event density uses unique source-event count. Zero duration makes these values null.
The maximum one-second start count uses half-open windows `[t,t+1)` whose candidate `t` values are
the distinct cue starts; an empty schedule returns zero.

Overlap prefers integer rendered intervals `[start_sample,end_sample_exclusive)`. Scheduled
seconds are the fallback. The deterministic sweep groups equal boundaries; duration since the
previous boundary is accumulated with the previous active count, which is equivalent to applying
ends before starts. It reports peak concurrency, time with concurrency at least two, that time /
timeline duration, the integral of `max(concurrency-1,0)`, and that integral / duration. Zero
duration makes both proportions null.

## Traceability and diagnostics

Cue-to-event traceability requires a resolvable source event and matching dataset/sequence.
Cue-to-annotation additionally requires matching source file and row. Cue-to-render requires one
render entry with matching cue/event IDs and valid sample bounds. Full traceability additionally
requires matching preset/mapping identity, schedule membership, cue-package/renderer identities,
declared hashes and a supplied WAV hash. Suppression traceability requires an existing event,
matching source location and preset identity. Every rate includes counts; broken links are grouped
by stable reason code.

Integrity findings use stable codes and deterministic ordering. Errors make the report invalid;
warnings record permitted missing evidence or suspicious results. Missed eligible events are
warnings because the evaluator can still calculate a method result, while orphans,
contradictory outcomes, duplicate IDs and incompatible versions are errors. Malformed top-level
records or an unsupported contract fail before metric calculation.

## Reproducibility

Repeat evidence is reported separately for semantic equality of canonically normalised records and
metrics, byte/hash equality of output files, byte/hash equality of WAV files, and equality of all
relevant configuration versions/hashes. Each compared file reports its name, level, booleans,
expected/observed hashes and mismatch detail. A level without evidence is `null`, never inferred
from successful execution. Claims are limited to the recorded tested environment.

## Deterministic report

Inputs and diagnostics are ordered by documented identifiers; grouped reasons and repeat files are
ordered lexically. JSON uses the shared compact, UTF-8 canonical serializer. The evaluation run ID
is content-derived from the contract and input identities. `report_payload_sha256` hashes the
canonical report before the hash-scope fields are appended, avoiding recursion. The writer also
returns the SHA-256 of the final exact report bytes.

Empty input is valid and produces zero counts, null rate/statistic values, a zero timeline, zero
peak concurrency and no warnings. A zero-duration non-empty input is permitted but produces a
`zero_duration_timeline` warning and null duration-based rates.
