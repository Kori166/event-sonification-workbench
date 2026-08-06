# Bounded RQ3 Findings

## 1. Evaluation method

RQ3 was evaluated through frozen contract `0.1.0`, a manually calculated synthetic oracle and two
real technical case studies. The canonical reports, rather than presentation prose, are the
numerical source. This document does not report participant or perceptual evaluation.

## 2. Event accounting and coverage

Accounting completeness was 30,003 / 30,003 (100.00%) for MOT17-02-DPM and
1,089 / 1,089 (100.00%) for KITTI Tracking 0000. Eligible-event coverage was
26,960 / 26,960 (100.00%) and 711 / 711 (100.00%), respectively, with
0 and 0 missed eligible events.
Source representation was 26,960 / 30,003 (89.86%) for MOT17 and
711 / 1,089 (65.29%) for KITTI because the selected evidence chains contained
different proportions of intentionally suppressed source events. Eligible-event coverage and source
representation therefore must not be treated as synonyms.

## 3. Timing alignment

The maximum sample-domain difference was 0 samples in
all three timing domains for both datasets, and the complete sample-domain descriptive statistics
were also zero. KITTI seconds-domain values were zero. MOT17 retained small non-zero maximum
differences: 3.33333335e-07 seconds for scheduling,
3.33333333e-07 seconds for render placement and
1.66666667e-15 seconds end to end. Exact sample placement under the
contract's decimal round-half-up rule is distinct from exact decimal-second equality. No perceptual
threshold was evaluated.

## 4. Traceability

The fully traceable cue rates were 26,960 / 26,960 (100.00%) and
711 / 711 (100.00%); the broken-link counts were
0 and 0.
Suppression-record traceability was likewise complete under the contract. These values establish
resolved provenance links, not listener comprehension.

## 5. Cue density and overlap burden

The fixed baseline produced 1342.18 cues per second for MOT17 and
46.11 for KITTI. Peak concurrency was
203 versus 24, and normalised
overlap burden was 160.06 versus
4.53. These are materially different technical loads for the
selected sequences. They do not establish masking, comprehension, listener difficulty or a better
sonification.

## 6. Reproducibility

Three isolated evaluator reports per dataset were semantically identical and byte-identical in the
recorded environment (Yes/
Yes for MOT17 and
Yes/
Yes for KITTI). The retained Stage 2 audio
chains were also byte-identical. No cross-environment byte comparison was conducted.

## 7. Cross-dataset interpretation

The comparison shows that one fixed contract can account for, align and trace both normalised event
sources while exposing different technical loads. MOT17 and KITTI differ in annotation conventions
and scene composition, so the comparison is descriptive rather than a comparison of equivalent
populations.

## 8. Limitations

Only MOT17-02-DPM and KITTI Tracking 0000 were evaluated. They are selected case studies rather than
representative sequence samples. One baseline preset and renderer were used; no mapping alternative,
participant test or perceptual quality measure was included. High eligible coverage does not mean
all source events were sonified, intentional suppression is not system failure, and high density or
overlap does not establish poor perceptual performance. Reproducibility is bounded to
same recorded Stage 3 execution environment.

## 9. Bounded answer to RQ3

Event-based sonification outputs can be evaluated reproducibly by fixing event-outcome denominators,
measuring alignment separately in sample and seconds domains, resolving provenance links through the
event-to-render chain, quantifying rendered-timeline density and overlap, and comparing semantic and
canonical bytes across isolated repetitions. For these two selected evidence chains, this method
produced complete contract-defined accounting, no missed eligible events, exact sample placement,
complete required traceability and repeat-identical reports in the recorded environment. The result
supports RQ3 as technical case-study evidence only and makes no accessibility, usability, navigation,
mobility, safety or perceptual-effectiveness claim.
