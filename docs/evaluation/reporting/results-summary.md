# Technical Evaluation Summary

## Evaluation Approach

Evaluation Contract `0.1.0` was fixed before the retained real-data evaluation. A manually calculated synthetic case and deliberate fault cases first checked the evaluator against known outcomes.

The unchanged measures were then applied to MOT17-02-DPM and KITTI Tracking 0000. They cover event accounting, eligible-event coverage, timing, traceability, cue density, overlap and repeatability. The canonical reports contain the complete calculations and remain the numerical source.

## Main Results

| Area | MOT17-02-DPM | KITTI Tracking 0000 |
|---|---|---|
| Event outcomes | 30,003 valid; 26,960 cues; 3,043 intentional suppressions | 1,089 valid; 711 cues; 378 intentional suppressions |
| Coverage | 100% accounting; 100% eligible-event coverage; 89.86% source representation; no eligible misses | 100% accounting; 100% eligible-event coverage; 65.29% source representation; no eligible misses |
| Timing | 0-sample maximum error; scheduling 3.3333334e-07 s, placement 3.3333333e-07 s and end-to-end 1.6666667e-15 s maximum decimal-second differences | 0-sample maximum error; 0 s maximum decimal-second differences |
| Traceability | All 26,960 cues and 3,043 suppressions traceable; no broken links | All 711 cues and 378 suppressions traceable; no broken links |
| Density and overlap | 1342.18 cues/s; peak 203; normalised burden 160.06 | 46.11 cues/s; peak 24; normalised burden 4.53 |
| Repeatability | Repeated reports and retained Stage 2 outputs matched in the recorded environment | Repeated reports and retained Stage 2 outputs matched in the recorded environment |

The detailed values are separated into [accounting and coverage](tables/event-accounting-and-coverage.md), [timing, traceability and repeatability](tables/timing-traceability-repeatability.md), and [density and overlap](tables/density-and-overlap.md).

## Interpretation

For these two cases, the results support complete eligible-event coverage, exact sample placement, complete traceability and same-environment repeatability. MOT17 had higher technical density and overlap than KITTI. These load measures describe the generated audio, not perceptual difficulty, comprehension or quality.

## Limitations

The evidence covers two selected sequences, one baseline mapping, one renderer and one recorded environment. It includes no participant study and no cross-platform byte-identity test. The results therefore support technical correctness and provenance for these cases, not human effectiveness or general performance across datasets and platforms.
