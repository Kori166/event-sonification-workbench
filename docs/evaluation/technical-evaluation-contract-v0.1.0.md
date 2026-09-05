# Technical Evaluation Contract 0.1.0

## Purpose And Scope

This contract defines the Stage 3 technical evaluation rules before they are applied to the real MOT17 and KITTI Tracking evidence.

It measures:

* event accounting and coverage
* timing alignment
* traceability
* cue density
* overlap
* repeatability within the tested environment

It does not measure accessibility, usability, navigation, perceptual effectiveness or safety.

The main machine readable contract is:

`configs/evaluation/technical-evaluation-contract.v0.1.0.json`

This is checked against its accompanying schema.

Evaluation reports must follow:

`configs/evaluation/technical-evaluation-report.schema.v0.1.0.json`

The contract, report schema and evaluator each have their own version. All began at version `0.1.0`.

## Required Evidence

An evaluation requires:

* validated common event schema `0.2.0` records
* cue and suppression records from cue package `0.1.0`
* renderer metadata and render log records from renderer `0.1.0`
* the identities and hashes of the related packages

The retained identity information includes:

* dataset and sequence
* event, cue and renderer versions
* sample rate
* total rendered frames
* event package hash
* preset hash
* cue schedule hash
* suppression log hash
* render log hash
* WAV hash where available
* renderer and evaluation configuration hashes

A missing optional WAV is recorded as missing evidence.

If a WAV is declared but its hash cannot be verified, this is treated as a broken evidence link.

Events provide the event ID, timestamp, dataset, sequence, source annotation, source hash and source row.

Cues provide the cue ID, source event ID, scheduled timing, source location and preset identity.

Suppressions provide the source event ID, reason for suppression, source location and preset identity.

Render records provide cue and event IDs together with the start sample, duration and exclusive end sample.

Identifiers must link to records whose details agree. Matching text alone is not considered sufficient evidence.

## Event Accounting And Coverage

Every valid source event must have one main outcome:

* represented by one or more cues
* intentionally suppressed
* missed
* explicitly excluded before evaluation

Several cues linked to one event still count as one represented event.

The following are treated as errors:

* the same event having both a cue and suppression
* duplicate suppression or exclusion records
* duplicate cue IDs
* cues linked to unknown events
* suppressions or exclusions linked to unknown events

Under contract `0.1.0`, every valid event that is not intentionally suppressed or excluded is eligible to produce a cue.

An eligible event is represented when at least one cue exists.

It is missed when no cue exists.

An intentionally suppressed event is never counted as missed.

Rates are recorded using a numerator, denominator and calculated value.

If the denominator is zero, the result is `null`.

The main rates are:

* **Eligible event coverage** = represented eligible events / eligible events
* **Source representation** = represented events / valid source events
* **Suppression rate** = intentionally suppressed events / valid source events
* **Accounting completeness** = represented, suppressed or excluded events / valid source events
* **Missed eligible rate** = missed eligible events / eligible events

## Timing Alignment

Timing is checked for scheduling, rendering and the complete event to audio path.

### Scheduling Error

Scheduling error is the absolute difference between the cue start time and source event timestamp:

`abs(cue_start_seconds - event_timestamp_seconds)`

### Render Placement Error

Render placement error compares the rendered audio start position with the scheduled cue time:

`abs(render_start_sample / sample_rate - cue_start_seconds)`

### End To End Error

End to end error compares the rendered audio position with the original event timestamp:

`abs(render_start_sample / sample_rate - event_timestamp_seconds)`

Timing is also checked directly in audio samples.

Sample positions use the renderer's existing decimal `ROUND_HALF_UP` rule.

This means a cue can have an exact sample position while still showing a very small decimal difference when expressed in seconds.

Cue end positions remain exclusive.

For each timing measure the evaluator records:

* count
* minimum
* maximum
* mean
* median
* p95

If there are no values, these statistics are recorded as `null`.

The median uses the middle value or the average of the two middle values when the count is even.

P95 uses the nearest rank method.

## Timeline, Density And Overlap

The evaluated timeline starts at zero.

Where render metadata is available, the timeline ends at:

`total rendered frames / sample rate`

This includes any recorded trailing silence.

If render metadata is unavailable, the final scheduled cue end is used instead.

An empty cue schedule has a duration of zero.

### Cue Density

Cue density is:

`cue count / duration`

Cue density per minute is the same value multiplied by 60.

Represented event density uses the number of unique source events instead of cue count.

If duration is zero, these values are recorded as `null`.

The maximum number of cue starts in one second is calculated using fixed one second windows beginning at each distinct cue start time.

An empty schedule returns zero.

### Overlap

Overlap is calculated using rendered sample intervals where possible.

Each cue uses the interval:

`[start_sample, end_sample_exclusive)`

Scheduled times are used only when rendered sample information is unavailable.

The evaluator records:

* peak number of simultaneous cues
* time containing two or more simultaneous cues
* proportion of the timeline containing overlap
* excess concurrent cue time
* normalised overlap burden

If timeline duration is zero, duration based proportions are recorded as `null`.

## Traceability Checks

Cue traceability checks whether each cue can be linked back through the retained evidence.

A cue must link to:

* its source event
* the correct dataset and sequence
* the correct source annotation and row
* its render record
* the correct preset and mapping information
* the cue schedule
* the cue and renderer package identities
* the required hashes
* the WAV hash where WAV evidence is supplied

A fully traceable cue must satisfy all required links.

Suppression traceability checks that each suppression links to:

* an existing source event
* the correct source location
* the correct preset

Broken links are grouped using stable reason codes.

## Errors And Warnings

Integrity findings use stable codes and deterministic ordering.

Errors make the evaluation report invalid.

Warnings identify issues where the evaluator can still produce meaningful technical results.

For example, a missed eligible event is recorded as a warning because the evaluator can still calculate coverage.

The following are treated as errors:

* orphan cues
* conflicting event outcomes
* duplicate identifiers
* incompatible versions
* malformed required records

Unsupported contract versions or invalid top level records stop evaluation before metrics are calculated.

## Repeatability Checks

Repeatability evidence is recorded separately for:

* semantic equality of records and metrics
* exact file byte and hash equality
* WAV byte and hash equality
* configuration version and hash equality

Each file comparison records its filename, comparison level, result, expected hash, observed hash and any mismatch details.

If no evidence exists for a comparison level, the result is `null`.

Repeatability claims are limited to the recorded tested environment.

## Deterministic Evaluation Report

Evaluation reports are produced deterministically.

Inputs and diagnostics use fixed ordering rules.

Grouped reasons and repeated file comparisons are ordered alphabetically.

JSON uses the shared UTF-8 serialisation format.

The evaluation run ID is generated from the contract and input identities rather than from time or random values.

`report_payload_sha256` is calculated before the report hash fields are added. This avoids the report attempting to hash a value that includes itself.

The final exact report bytes are also assigned a SHA-256 hash.

## Empty And Zero Duration Cases

An empty input is valid.

It produces:

* zero event counts
* `null` rate values
* `null` timing statistics
* a zero length timeline
* zero peak concurrency
* no warnings

A non empty input with a zero duration timeline is also permitted.

In this case, the evaluator records a `zero_duration_timeline` warning and any rate that requires duration is recorded as `null`.