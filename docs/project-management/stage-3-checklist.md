# Stage 3 Checklist

## Milestone 1: Define and Validate the Evaluation Method

- [x] Confirmed Stage 2 was complete before beginning technical evaluation.
- [x] Defined event accounting and coverage so intentional suppressions are kept separate from missed eligible events.
- [x] Defined timing measures for cue scheduling, audio rendering and the complete processing chain.
- [x] Measured timing in both seconds and audio samples.
- [x] Defined traceability checks linking cues and suppressions back to events, source annotations, configurations and retained outputs.
- [x] Defined cue density using the rendered timeline and fixed one second windows.
- [x] Defined overlap using consistent timing boundaries, concurrency and overlapping cue duration.
- [x] Defined separate checks for semantic, file byte, audio and configuration repeatability.
- [x] Created a five event synthetic test case with manually calculated expected results.
- [x] Added deliberate faults covering missing cues, orphan cues, conflicting outcomes, broken provenance and timing errors.
- [x] Confirmed the evaluator reproduced the expected synthetic results.
- [x] Confirmed repeated canonical evaluation reports produced identical bytes and SHA-256 values.
- [x] Confirmed Ruff and all configured tests excluding integration tests passed.
- [x] Kept real dataset results and perceptual claims outside this milestone.

## Milestone 2: Apply the Evaluation to MOT17 and KITTI

- [x] Prepared evaluation inputs from the verified MOT17 and KITTI Stage 1 and Stage 2 packages.
- [x] Kept the evaluation formulas unchanged when moving from synthetic to real data.
- [x] Verified event, cue, suppression, render, WAV and configuration hashes before evaluation.
- [x] Applied Technical Evaluation Contract `0.1.0` to the retained MOT17 and KITTI evidence.
- [x] Produced canonical evaluation reports for both datasets.
- [x] Repeated the evaluator independently to check consistency.
- [x] Compared evaluation results, report bytes, audio bytes and configuration identities.
- [x] Recorded event accounting, coverage, timing, traceability, cue density and overlap results.
- [x] Checked for missed events, orphan cues, broken provenance links, warnings and repeatability differences before interpreting the results.
- [x] Ran the configured quality checks and available private integrations without treating skipped tests as successful results.
- [x] Limited the findings to the recorded execution environment and avoided participant or perceptual claims.

## Milestone 3: Verify and Prepare the Final Results

- [x] Linked reported values to their canonical evaluation evidence and source hashes.
- [x] Produced report ready tables and detailed timing evidence from the canonical reports.
- [x] Recorded the source, raw value, displayed value, calculation and formatting rules for reported results.
- [x] Independently recalculated the main reported values.
- [x] Checked table values against the canonical evaluation reports.
- [x] Checked the principal written claims against retained evidence.
- [x] Confirmed the reporting audit found no remaining numerical or provenance mismatches.
- [x] Rebuilt the reporting evidence independently to check deterministic output.
- [x] Used the verified results to answer RQ3 without changing the frozen evaluation contract.
- [x] Kept the case study, execution environment and non perceptual limitations explicit.
- [x] Confirmed the final configured Stage 3 test suites and private integrations passed.

