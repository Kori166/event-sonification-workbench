# 0013: Technical Evaluation Method

## Status

Accepted and tested on 6 August 2026.

The method was first checked against a manually calculated synthetic test case.

It was then applied unchanged to the selected `MOT17-02-DPM` and KITTI Tracking `0000` evidence.

## Context

Stage 2 already provides complete records linking events to cues, suppressions and rendered audio.

However, Stage 2 does not define how evaluation should calculate:

* coverage
* timing
* overlap
* traceability
* repeatability

These rules need to be fixed before real dataset results are calculated. Otherwise, the method could be changed after seeing the results, which would weaken the evaluation.

## Decision

Technical Evaluation Contract `0.1.0` is fixed before real dataset evaluation.

The contract is stored in both machine readable and human readable form.

The main rules are:

* A valid event with no cue, suppression or explicit exclusion is counted as a missed eligible event.
* An intentionally suppressed event is not counted as missed.
* More than one cue may represent the same event.
* An event cannot be both represented and suppressed.
* Orphan links and duplicate outcome records are treated as errors.
* Every rate records its numerator and denominator.
* A zero denominator produces `null`.
* Timing is measured separately for scheduling, render placement and the complete event to audio path.
* Timing is reported in both seconds and audio samples.
* P95 uses the nearest rank method.
* Rendered sample positions and half open intervals are preferred where available.
* Traceability is checked by resolving linked records and hashes, not simply by checking that identifiers exist.
* Repeatability is checked separately for semantic results, file bytes, audio bytes and configuration.
* Untested repeatability levels remain `null`.
* Evaluation reports use canonical JSON and content based identities.
* Repeatability claims are limited to the recorded tested environment.

## Rationale

Fixing the evaluation rules before using the real datasets reduces the risk of changing formulas or definitions to produce more favourable results.

The synthetic test case also provides an independent way to check that the evaluator produces the expected results before it is applied to MOT17 and KITTI.

Separating different types of timing and repeatability evidence also avoids combining distinct technical behaviours into a single result.

## Consequences

* A missed eligible event can produce a valid evaluation report with a warning.
* Broken links or conflicting event outcomes make the report invalid.
* A cue can have zero sample placement error while still showing a very small difference when expressed in seconds.
* Both values are retained rather than hiding the difference.
* Trailing silence is included in density and overlap calculations when it is part of the rendered audio timeline.
* Real dataset evaluation must use Contract `0.1.0` unchanged.
* Any later change to formulas, denominators or boundaries would require a new contract version and a new decision record.
* Technical evaluation does not provide participant or perceptual evidence.
* The results do not establish accessibility, usability or safety.

## Real Dataset Application

The contract was applied unchanged to both selected real dataset cases.

No formula, denominator, threshold or boundary rule was altered after observing the results.

Each dataset was evaluated three times.

Within the recorded environment, all three reports for each dataset were semantically and byte identical.

Additional checks linking cues to mapping rules, schedules and WAV files were recorded separately under Decision 0014. They are supporting traceability checks rather than new fields in Contract `0.1.0`.