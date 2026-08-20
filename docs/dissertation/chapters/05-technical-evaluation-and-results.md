# 5. Technical Evaluation and Results

## 5.1 Evaluation design

The frozen Technical Evaluation Contract `0.1.0` separated event accounting, timing, traceability, output load and same-environment reproduction. Before the real cases, a manual oracle verified known cue/suppression outcomes and sample calculations; negative tests introduced misses, orphan cues, contradictory outcomes, broken links and one-sample displacement. The unchanged contract was then applied to MOT17-02-DPM and KITTI Tracking 0000. An independent audit checked 134 source/derived values, 136 table cells, 20 figure points, 12 claims, seven captions and 23 hashes with no mismatches. Canonical report identities are listed in the [Phase A evidence baseline](../evidence-baseline.md).

The evaluation unit was a valid normalised event, not a unique object track or source frame. Consequently, repeated observations of one tracked object were counted separately, matching the implemented event-to-cue policy. Metrics were computed from retained packages rather than the browser view, and the publication tables and figures were regenerated from frozen reports. This separation limited presentation code from becoming an alternative source of results.

## 5.2 Accounting and coverage

MOT17 contained 30,003 valid events: 26,960 were represented by cues and 3,043 intentionally suppressed under the class policy. KITTI contained 1,089 valid events: 711 represented and 378 `DontCare` observations suppressed. Neither case had a missed, invalidly excluded or unaccounted event, giving 100% accounting completeness and 100% eligible-event coverage.

Source representation, whose denominator includes suppressions, was 89.86% for MOT17 and 65.29% for KITTI. KITTI’s lower value therefore reflects policy rather than mapping failure. Table 4 and Figure 2 contain the audited outcomes.

[**Table 4. Audited event accounting and coverage. Presentation derivative of the canonical reports under contract `0.1.0`.**](../../evaluation/reporting/tables/table-1-event-accounting-and-coverage.md)

The equality between valid events and represented-plus-suppressed outcomes is the accounting claim. Eligible-event coverage uses only events allowed by the frozen policy as its denominator. Reporting both measures avoids the superficially contradictory conclusion that KITTI simultaneously had complete eligible coverage and a lower proportion of all source observations rendered as sound.

![Figure 2. Audited event outcomes for the two canonical cases. Contract `0.1.0`; valid-event denominator.](../../evaluation/reporting/figures/figure-1-event-outcomes.svg)

## 5.3 Alignment and traceability

All scheduled and rendered boundaries matched expected integer sample indices: maximum error was zero samples in scheduling, placement and end-to-end domains. KITTI also had zero seconds-domain error. MOT17 maxima were approximately 3.33 × 10^-7 seconds for scheduling/placement and 1.67 × 10^-15 seconds end to end, floating-point observations that do not contradict exact sample placement.

Every represented event resolved from source annotation through cue to rendered interval: 26,960/26,960 MOT17 cues and 711/711 KITTI cues. All 3,043 and 378 suppressions were traceable, with no broken links.

## 5.4 Density and overlap

MOT17 generated 26,960 cues over 20.0867 seconds (1,342.18 cues/s), compared with 711 over 15.42 seconds for KITTI (46.11 cues/s). Maximum cue starts in a half-open one-second window were 1,500 and 116; peak concurrency was 203 and 24. Both timelines overlapped throughout. Normalised overlap burden was 160.06 for MOT17 and 4.53 for KITTI. These values describe technical load, not listener performance.

![Figure 3. Audited cue density in cues per rendered-timeline second. Fixed baseline; not perceptual evidence.](../../evaluation/reporting/figures/figure-2-cue-density.svg)

![Figure 4. Audited normalised overlap burden using half-open intervals. Not a listener-difficulty measure.](../../evaluation/reporting/figures/figure-3-overlap-burden.svg)

[**Table 5. Audited timing, traceability and reproducibility. Sample/seconds and environment boundaries preserved.**](../../evaluation/reporting/tables/table-2-timing-traceability-reproducibility.md)

[**Table 6. Audited density and overlap metrics. Frozen preset/renderer and half-open intervals.**](../../evaluation/reporting/tables/table-3-density-and-overlap.md)

## 5.5 Reproducibility

For each dataset, two Stage 2 runs reproduced all four event-package, five cue-package and three audio-package files byte-for-byte. Three evaluator runs produced semantically and byte-identical reports, and fresh reporting builds reproduced all 24 reporting artefacts. This establishes deterministic reproduction in the recorded Windows/AMD64/Python 3.14.3 environment, not cross-platform byte identity.

These repetitions test the frozen implementation and retained inputs; they do not estimate variability across operating systems, audio libraries or future dependency versions. The environment qualifier is therefore part of the result rather than a reporting footnote.
