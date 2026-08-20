# Stage 5 Phase D Compression Plan

## Compression objective

Reduce the assessed Chapters 1–8 from approximately 8,603 words to a safe target near 5,500 words. The reduction will remove repetition and technical duplication while preserving the research problem, critical literature synthesis, methodological justification, canonical findings, explicit RQ answers, validity threats, ethics, reflection, objective status and evidence boundaries. Abstract and References remain outside the assessed-body target.

## Chapter plan

| Chapter | Phase C words | Phase D target | Essential content to preserve | Primary compression candidates | Over-compression risk |
|---|---:|---:|---|---|---|
| 1. Introduction | 668 | 400–450 | Problem, qualified gap, aim, frozen RQs, objective status, scope, contribution | Dataset detail; extended mapping explanation; repeated claim boundary; chapter-route detail | Losing the precise infrastructure gap or making the contribution appear universal |
| 2. Literature Review | 1,760 | 1,050–1,150 | Mapping foundations; reusable tools; participant-evidence boundary; dataset heterogeneity; provenance/reproducibility; synthesis and gap | Combine tool descriptions; shorten individual dataset/tool capabilities; merge repeated participant and reproducibility cautions | Turning the review into a descriptive catalogue or weakening the literature-to-design link |
| 3. Methodology | 1,163 | 650–725 | Artefact method; cases and selection rationale; event/cue/suppression definitions; frozen evaluation; oracle/negative tests; technical scope | Four-stage chronology; raw/package mechanics duplicated in Chapter 4; detailed metric definitions; repeated validity caveats | Obscuring why the method was selected or how shared-assumption bias was mitigated |
| 4. Design and Implementation | 1,281 | 750–825 | Architecture; adapters/schema; deterministic IDs/provenance; mapping and suppression; renderer; session/inspection layer; objective outcome | Remove Table 2 because prose communicates the schema more efficiently; shorten Table 3 to core rules; remove prose that repeats tables; compress renderer constants and UI feature list | Reducing the contribution to a superficial component list or losing class-modifier/area caveats |
| 5. Evaluation and Results | 1,006 | 675–725 | Evaluation design; canonical accounting/coverage; timing; traceability; density/overlap; same-environment reproducibility | Compress oracle/fault inventory; avoid prose duplication of Tables 4–6; shorten repeated non-perceptual caveats | Dropping denominators, seconds/sample distinction or environment boundary |
| 6. Discussion | 1,446 | 925–1,000 | Explicit RQ1–RQ3 answers; literature relation; cross-dataset implications; construct/internal/external/conclusion/reproducibility validity; R20/R21 | Remove implementation recap and repeated numeric reporting; consolidate contribution comparison and validity statements | Weakening explicit RQ answers or removing necessary threats to validity |
| 7. Ethics and Reflection | 869 | 500–575 | Participant boundary; licensing/redistribution; private paths; evidence integrity; problem→correction→lesson examples; O1–O4; frozen baseline; R20/R21 | Merge licence/privacy paragraphs; retain two Stage 4 examples rather than defect chronology; shorten repeated future work | Becoming generic ethics prose or losing genuine evidence-based reflection |
| 8. Conclusion | 410 | 300–350 | Concise RQ answers; contribution; objective status; principal limitation; prioritised future work | Remove detailed result repetition and architecture recap; combine future-work list | Failing to answer each RQ explicitly or hiding partial achievement |
| **Assessed body** | **8,603** | **approximately 5,500** |  |  |  |

## Cross-chapter consolidation map

| Topic | Primary location(s) | Treatment elsewhere |
|---|---|---|
| Participant/perceptual boundary | Methodology, Discussion and Ethics | One sentence in Abstract/Introduction; brief result qualifier only |
| One frozen baseline | Methodology and Discussion | Configuration fact in Implementation; no repeated defence |
| Cross-platform reproducibility | Results and validity discussion | Concise scope signal in Abstract/Conclusion |
| Two-sequence generalisation | Validity discussion and Conclusion | Brief scope statement in Introduction |
| Bounding-box area/apparent-scale proxy (R21) | Discussion and Reflection | One implementation caveat in shortened Table 3 |
| Dense cue-stream reflection (R20) | Discussion and Reflection | Results report load only, without listener interpretation |
| Mapping mechanics | Shortened Table 3 in Chapter 4 | Discussion refers to the design without restating ranges |
| Objective status | Introduction, Reflection and Conclusion | Implementation gives only a compact outcome sentence |

## Table and figure decisions

- Retain Figure 1 and audited Figures 2–4 unchanged.
- Retain Table 1 in shortened form because it efficiently compares native conventions.
- Remove documentary Table 2 from the final body; replace it with one concise schema paragraph.
- Shorten documentary Table 3 to the mapping, eligibility, placement and two interpretation caveats.
- Preserve audited Tables 4–6 without changing numerical content or provenance; reduce surrounding prose instead.
- Keep the optional workbench screenshot excluded because reproduction/privacy clearance remains unresolved.

## Word-transfer and formatting plan

No post-implementation canonical DOCX exists. The May proposal will remain untouched as historical source material. A new private submission source will be created under `C:\Users\korif\OneDrive\Documents\MSc Project - Event-Based Sonification Workbench\Submission` using:

- title: *A Reproducible Workbench for Event-Based Sonification of Annotated Video Datasets*;
- author: Kori Flowers;
- student ID: 24046378;
- programme: MSc Data Science;
- module: UFCF9Y-60-M CSCT Masters Project;
- institution: University of the West of England;
- submission month: August 2026.

The Word design will use a restrained academic-report variant of the `narrative_proposal` preset: A4 portrait as a university-submission override, 2.54 cm margins, Aptos/Calibri-compatible 11 pt body, 1.15 line spacing, black heading hierarchy, automatic styles, inline figures, fixed-width tables, static contents/list pages for deterministic QA, and page-number footers. No module detail or exact submission day will be invented beyond the recorded information above.

## Outcome recorded after editing

The repository-side Chapters 1–8 were reduced to 5,294 words. The formatted Word count is 5,650
assessed words because it includes headings, captions and the content of linked audited tables. This
is within the required 5,000–6,000 range and the 5,400–5,700 safety target. Table 2 was retained,
contrary to the initial candidate action, because the compact grouped-field presentation remained
more efficient and clearer than replacement prose. The final title uses the planned full dissertation
title. Detailed evidence, citation, formatting and validation results are recorded in
[`phase-d-audit.md`](phase-d-audit.md).
