# 5. Technical Evaluation and Results

## 5.1 Evaluation design

The workbench was evaluated against the frozen Technical Evaluation Contract version 0.1.0. The contract was defined before the two public-dataset cases were run and was not altered during the real-data evaluation. It separates four questions that can otherwise be conflated: whether every valid event has an accountable outcome; whether represented events are scheduled and rendered at the intended time; whether an audio cue can be traced to its source and configuration; and whether the pipeline produces the same artefacts when repeated in the recorded environment. The evaluation is technical. It does not measure perceptual discriminability, usability, accessibility, or task performance.

The contract was first exercised against a manually specified synthetic oracle containing five events, five cues and one suppression. This case covered multiple cues for one event, overlapping cues, touching half-open intervals and round-half-up sample conversion. Negative cases deliberately introduced an eligible miss, orphan cue, unknown suppression, contradictory event outcome, broken annotation link and one-sample displacement. Empty, zero-duration and malformed inputs were also tested. At evaluation close-out, 26 focused tests covered the evaluator and reporting path.

Two canonical public-data cases were then evaluated end to end: MOT17-02-DPM and KITTI Tracking sequence 0000. The reports were generated from validated event, cue and audio packages rather than from manually transcribed counts. An independent reporting audit checked 134 source or derived values, 136 table cells, 20 figure points, 12 written claims, seven captions and 23 hashes, with no mismatches recorded. The audited source reports and their digests are listed in the [Phase A evidence baseline](../evidence-baseline.md).

## 5.2 Event accounting and coverage

MOT17-02-DPM contained 30,003 valid normalised events. Of these, 26,960 were represented by one or more cues and 3,043 were intentionally suppressed because their classes were excluded by the preset. KITTI 0000 contained 1,089 valid events, of which 711 were represented and 378 `DontCare` observations were intentionally suppressed. Neither case contained a missed event, an invalidly excluded outcome, or an unaccounted event. Both therefore achieved 100% accounting completeness and 100% eligible-event coverage.

Source-event representation was lower because its denominator includes valid intentional suppressions: 89.86% for MOT17 and 65.29% for KITTI. This distinction is important. The lower KITTI value is not evidence of a mapping failure; it results from the retained `DontCare` annotations and the declared suppression policy. Table 1 and Figure 2 preserve the audited outcome data.

[Table 1: Audited event accounting by dataset](../../evaluation/reporting/tables/table-1-event-accounting-and-coverage.md)

![Figure 2. Audited event outcomes for the two canonical datasets.](../../evaluation/reporting/figures/figure-1-event-outcomes.svg)

## 5.3 Temporal alignment

All scheduled and rendered cue boundaries agreed exactly with their expected integer sample indices. The maximum error was zero samples in the scheduling, render-placement and end-to-end domains for both datasets. KITTI also had zero maximum error when expressed in seconds. For MOT17, the corresponding maxima were approximately 3.33 × 10^-7 seconds for scheduling and render placement and 1.67 × 10^-15 seconds end to end. These very small decimal differences arise from representing frame-derived times in floating-point seconds; they do not contradict the exact sample-domain result. They are reported as numerical observations, not interpreted through an untested perceptual threshold.

## 5.4 Traceability

Every represented event had a complete trace from source annotation through event and cue records to its rendered sample interval. The fully traceable cue rates were 26,960 of 26,960 for MOT17 and 711 of 711 for KITTI. Suppression traceability was likewise complete at 3,043 of 3,043 and 378 of 378 respectively, and neither report contained a broken trace link. Traceability required identifiers and hashes to resolve and agree across artefacts; the presence of a plausible-looking identifier alone was insufficient.

## 5.5 Density and overlap

The same mapping policy produced markedly different output density across the cases. Over 20.0867 seconds, MOT17 generated 26,960 cues, or 1,342.18 cues per second. KITTI generated 711 cues over 15.42 seconds, or 46.11 cues per second. The maximum number of cue starts in a half-open one-second window was 1,500 for MOT17 and 116 for KITTI. Peak concurrency was 203 and 24 cues respectively.

Both timelines contained overlapping cues throughout their evaluated duration, giving an overlap-duration proportion of 1.0. The normalised overlap burden, which measures excess concurrent cue-seconds per timeline second, was 160.06 for MOT17 and 4.53 for KITTI. These metrics establish substantial technical crowding, particularly in MOT17, but do not by themselves show what a listener can distinguish.

![Figure 3. Audited cue density comparison.](../../evaluation/reporting/figures/figure-2-cue-density.svg)

![Figure 4. Audited overlap-burden comparison.](../../evaluation/reporting/figures/figure-3-overlap-burden.svg)

[Table 2: Audited timing, traceability and reproducibility results](../../evaluation/reporting/tables/table-2-timing-traceability-reproducibility.md)

[Table 3: Audited density and overlap metrics](../../evaluation/reporting/tables/table-3-density-and-overlap.md)

## 5.6 Reproducibility

Two independent Stage 2 pipeline runs were performed for each dataset in the recorded Windows/AMD64/Python 3.14.3 environment. Across those paired runs, all four event-package files, five cue-package files and three audio-package files were byte-for-byte and hash identical. Three isolated evaluator runs per dataset produced semantically and byte-identical reports, and fresh reporting builds reproduced all 24 reporting artefacts. These results support deterministic reproduction within the recorded environment. They do not establish byte-identical behaviour on other operating systems, architectures or Python versions.
