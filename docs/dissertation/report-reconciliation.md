# Report Reconciliation

## Scope and source inventory

No dissertation draft is tracked in the repository or present in Git history. The repository itself
states that an external draft must not be overwritten and records six known legacy findings in
[`outdated-report-findings-replacement-note.md`](../evaluation/reporting/outdated-report-findings-replacement-note.md).

The following external files were inspected read-only on 18 August 2026. They remain outside Git and
their contents are therefore not part of the reproducible repository baseline:

- `revised_sonification_project_proposal_template_aligned.docx` (19 May 2026): closest proposal to
  the final title and two-dataset minimum scope;
- `annotation_video_sonification_workbench_proposal.docx` (17 May 2026): earlier three-dataset,
  multi-preset proposal;
- `MSc Proposal Framing for an Annotation-Driven Video Sonification Workbench.docx` (17 May 2026):
  framing/dataset-options analysis;
- `task_optimised_semantic_sonification_UWE_academic_working_report.docx` and
  `task_optimised_semantic_sonification_working_report_structure.docx` (8 May 2026): a materially
  different mobility-critical-target project and not a draft of the completed artefact;
- `Best Public Datasets for an Interactive Dataset-Grounded Workbench for Sonification of Annotated Vid.docx`
  (17 May 2026): dataset-selection research, not an implementation report;
- `event_sonification_viva_slidepack.pptx` (19 June 2026): interim presentation with exact concise
  RQ wording but obsolete progress/results slides.

The table prioritises claims that could alter research questions, methods, results or conclusions.
“Final evidence” means the paths in [`evidence-baseline.md`](evidence-baseline.md).

| Draft/source | Claim or topic | Status | Final evidence | Required report action |
|---|---|---|---|---|
| Revised proposal | Title: *A Reproducible Workbench for Event-Based Sonification of Annotated Video Datasets* | VERIFIED | README and project plan | Retain. |
| Revised proposal/project plan | Aim is a reproducible workbench converting annotations to common events and deterministic audio, evaluated technically | VERIFIED | [`project-plan.md`](../project-management/project-plan.md), Stages 1-3 close-outs | Use the final project-plan wording. |
| Early proposal/framing | Three core adapters including BDD100K; KITTI MOTS masks | CONTRADICTED | Only MOT17 and KITTI Tracking adapters/configuration/tests exist | Remove BDD100K/MOTS from completed method/results; mention only as abandoned scope or future work if relevant. |
| Revised proposal | Two core adapters, BDD100K/MOTS only stretch | VERIFIED for minimum scope | Stage 1 records | State that the stretch extensions were not implemented. |
| Interim viva deck | “KITTI is implemented but still needs full real-data testing”; only MOT17 end-to-end | OUTDATED | KITTI 0000 has complete Stages 1-4 evidence | Replace with the final KITTI chain and bounded two-case evaluation. |
| Interim viva deck | 1,000 MOT17 events and 39 cues | OUTDATED | 30,003 valid events; 26,960 cues; 3,043 suppressions | Use audited Table 1/3 values only. |
| Interim viva deck | Overall artefact 55-60% complete | OUTDATED | Stage 4 complete, Stage 5 planned | Do not retain progress percentages. |
| Early/revised proposals | At least three presets (or two core plus one experimental) | CONTRADICTED | Only baseline preset `0.1.0` exists and was evaluated | Describe one versioned technical reference mapping. Do not imply comparative mapping results. |
| Early/revised proposals | Compare preset A/B/C, naive baseline and scheduler ablations | PROPOSED/FUTURE WORK | No such canonical runs/reports | Remove from methods/results; retain as future work only. |
| Interim viva deck | Compare `frame_stride` 10, 5 and 2; current baseline stride 10 | CONTRADICTED | Final baseline has `frame_stride: 1`; no stride comparison | Report stride 1 as configuration, not an experimental factor. |
| Revised proposal | Priority, refractory period and polyphony-cap scheduling controls | NOT IMPLEMENTED / PROPOSED | Final preset has deterministic order and suppression rules but none of these planned controls | Do not describe them as implementation. They may motivate future dense-cue mitigation. |
| Interim viva deck | Suppressed events are counted as missed; refine denominator later | OUTDATED | Contract `0.1.0` distinguishes represented/suppressed/missed/excluded | Use final accounting terms and denominators. |
| Interim deck/proposal | “Most skipped” through confidence and frame stride | CONTRADICTED | Final MOT17 suppressions are `class_excluded`; KITTI suppressions are `dont_care_excluded` | Name the actual suppression codes. |
| Proposals | False-cue rate per clip-minute as an experimental metric | OUTDATED / REQUIRES CARE | Contract records orphan/broken links and 0 missed events; it does not publish a metric named false-cue rate | Report zero unlinked/broken-link outcomes only with contract terminology; do not silently relabel as “false cues.” |
| Proposals | Time-to-first-cue/latency and interval onset/offset comparison | OUTDATED | Stage 3 uses scheduling, render-placement and end-to-end alignment in sample/seconds domains | Use the frozen timing definitions. |
| Interim deck | Alignment error `0.0s`; all timing errors zero | CONTRADICTED | Sample errors are zero; MOT17 decimal-seconds maxima are small but non-zero | Preserve sample/seconds distinction and exact maxima from audited Table 2/2a. |
| Proposals | Cue fragmentation metric | PROPOSED/FUTURE WORK | Not in evaluation contract/report | Do not claim it was measured. |
| Completed evidence | Eligible-event coverage 100% for both cases | VERIFIED | Audited Table 1 and canonical reports | Include numerator/denominator; distinguish source representation (89.86%, 65.29%). |
| Completed evidence | Complete traceability and zero broken links | VERIFIED | Canonical reports and traceability audits | Bound to contract `0.1.0` and selected cases; do not infer listener comprehension. |
| Completed evidence | Cue density 1342.18 vs 46.11 cues/s | VERIFIED | Audited Table 3 | Present as descriptive load, not usability or quality. |
| Completed evidence | Peak concurrency 203 vs 24; normalised overlap burden 160.06 vs 4.53 | VERIFIED | Audited Table 3 | Present as technical load, not masking/difficulty evidence. |
| Completed evidence | Three evaluator reports per dataset and retained Stage 2 audio are byte-identical | VERIFIED | Canonical reports, repeat comparisons, Stage 2 close-out | Add recorded-environment boundary; no cross-platform claim. |
| Proposal | Complete semantic harmonisation through a common ontology | UNSUPPORTED if phrased absolutely | Schema shares a core shape while retaining native classes/metadata | Say “common event schema”, not universal ontology or full semantic equivalence. |
| Proposal | Bounding-box geometry supports depth/urgency interpretation | UNSUPPORTED / CONTRADICTED if called depth | R21 and renderer/preset records | Call area an amplitude input and imperfect apparent-scale proxy only. |
| Preset vs renderer | Class modifiers affect rendered loudness/timbre | CONTRADICTED | Renderer says `trace_only_not_applied` | Explain that modifiers are logged but inaudible under renderer `0.1.0`. |
| Early reports | Live detection, door/tripping-hazard optimisation, Bayesian optimisation, speech/hybrid baseline | CONTRADICTED / WRONG PROJECT | Task-optimised reports describe another proposed project | Exclude completely from this dissertation’s implemented methodology/results. |
| Proposals | Replay UI with preset switching, channel mute/solo and broad experiment controls | PARTLY OUTDATED | Stage 4 implements two-session evidence inspection, unchanged WAV playback, overlays/timeline/trace/metrics | Describe actual read-only inspection features; do not call it a live experimentation UI. |
| Interim deck | More tests/README/evaluation refinement still required | OUTDATED | Final Stage 4 gates and current README | Replace with recorded final verification state; retain genuine open limitations only. |
| All bounded proposals | No participant/accessibility/navigation/safety result | VERIFIED | Decision 0001, Stage 3/4 close-outs, R20 | Retain prominently and consistently. |
| Informal researcher inspection | Dense overlapping cues were difficult to distinguish | REQUIRES REVIEW | R20 records an informal observation, explicitly not participant/perceptual evidence | Report as a design limitation/observation, not a measured perceptual result. |
| Workbench acceptance | Stage 4 “passed usability testing” | CONTRADICTED | Acceptance was researcher-controlled engineering/browser testing | Use “technical browser acceptance”; never “usability test.” |
| Proposal/project plan | Artefact would be tagged on release | OUTDATED / NOT ACHIEVED | No Git tag exists | State package/release candidate version `0.1.0`; do not invent a tag. |

## Critical corrections before dissertation writing

1. Replace the 1,000-event/39-cue MOT17 snapshot with the full audited MOT17 and KITTI results.
2. Remove claims that KITTI is pending or that MOT17 was the only evaluated dataset.
3. Remove all three-preset, `frame_stride`, baseline/ablation, optimisation and superiority claims.
4. Keep suppression distinct from missed eligible events; use actual suppression codes.
5. Do not say all timing errors were zero: sample placement was exact, while MOT17 retained tiny
   decimal-seconds differences.
6. Do not report the planned “false-cue rate”, fragmentation or time-to-first-cue as completed
   measures; use contract `0.1.0` terminology.
7. Describe Stage 4 as a read-only inspection layer and its browser checks as engineering acceptance.
8. State that `class_modifier` is trace-only and bounding-box area is not depth.
9. Preserve the evidence boundary: no participant, perceptual, usability, accessibility, navigation,
   mobility or safety conclusion, and no cross-platform byte-identity conclusion.
10. Use the research-question wording confirmed by the Stage 5 Phase B brief exactly as recorded in
    [`evidence-map.md`](evidence-map.md) and [`report-structure.md`](report-structure.md).
