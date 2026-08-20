# Stage 5 Phase C Manuscript Audit

## 1. Completion boundary

Phase C produced a complete repository working dissertation while leaving the Stage 1–4 technical baseline unchanged. The final formatted Word/PDF assessment artefact, submission-length compression, layout, proofreading and supervisor feedback remain outside this phase. Stage 5 therefore remains in progress.

## 2. Canonical claim audit

| Claim group used in manuscript | Canonical evidence source | Audited value/boundary |
|---|---|---|
| Contracts | Phase A evidence baseline; schema/configuration files | Event schema `0.2.0`; session, preset/renderer and evaluation contracts `0.1.0` |
| MOT17 case | Canonical MOT17 technical evaluation report | `MOT17-02-DPM`; 30,003 valid events; 26,960 cues; 3,043 intentional suppressions |
| KITTI case | Canonical KITTI technical evaluation report | Tracking `0000`; 1,089 valid events; 711 cues; 378 intentional suppressions |
| Coverage/accounting | Canonical reports and audited Table 4/Figure 2 | 100% accounting completeness and eligible-event coverage in both cases; source representation 89.86% and 65.29% |
| Timing | Canonical reports and audited Table 5 | Zero maximum error in all integer-sample domains; small non-zero MOT17 seconds-domain maxima retained |
| Traceability | Canonical reports and traceability audits | 100% cue and suppression traceability; zero broken links |
| Load | Canonical reports, audited Figures 3–4 and Table 6 | 1,342.18 versus 46.11 cues/s; peak concurrency 203 versus 24; overlap burden 160.06 versus 4.53 |
| Reproducibility | Stage 2 close-out and canonical reports | Byte-identical repeated packages/audio and report equality only in the recorded environment |
| Stage 4 acceptance | Stage 4 close-out/Decision 0019 | 16 engineering checks; not usability, accessibility or participant evidence |
| Objectives | Phase A evidence map | O1/O2 achieved; O3/O4 partially achieved |

The only external-draft factual correction required in Phase C concerned Ji *et al.* (2021): the verified citation is *Sensors* 21(10), article 3558. No canonical project value required correction, and no retained implementation or Stage 3 evidence was changed.

## 3. Citation and reference audit

- Unique in-text sources: **21**.
- Reference-list entries: **21**.
- Citation → reference mismatches: **0**.
- Reference → citation mismatches: **0**.
- Unresolved bibliographic markers: **0**.
- Full source-level details and authorities: [`reference-audit.md`](reference-audit.md).

## 4. RQ, scope and language audit

Each frozen research question appears verbatim in the Introduction and as its Discussion heading. Each receives an explicit bounded answer in the Discussion and a concise answer in the Conclusion. The old configurable-presets RQ wording is absent.

The obsolete-history search found no final-evidence occurrence of `1000 event`, `1,000 event`, `39 cue`, `KITTI pending`, `KITTI remains`, `three preset`, `3 preset`, `false cue rate`, `missed cue rate`, `fragmentation` or `time-to-first-cue`. “Scheduler ablations” appears once in Critical Reflection and is explicitly identified as uncompleted proposal scope.

The claim-strength search for `effective`, `usable`, `accessible`, `intuitive`, `clear to listeners`, `navigation`, `safe`, `real-world benefit`, `improves perception`, `accurate depth` and `depth mapping` produced only literature descriptions, explicit non-claim boundaries or future-work statements. No occurrence asserts participant, accessibility, navigation, safety or depth performance for the completed artefact.

R20 appears only as bounded informal researcher inspection and future-study motivation. R21 appears only as the limitation that bounding-box area is an imperfect apparent-scale input rather than metric depth. Same-environment determinism is distinguished from untested cross-platform byte identity.

## 5. Academic-quality and coherence audit

The manuscript follows the progression from interoperability problem, through literature and research gap, to method, implementation, technical evaluation, interpretation, ethics/reflection and bounded conclusion. The Literature Review is organised by arguments and connects each theme to an artefact consequence. Project evidence claims remain distinct from external literature claims. Results state canonical observations; interpretation and comparison occur in the Discussion.

The validity review covers construct, internal, external, conclusion and reproducibility validity. It explicitly addresses shared pipeline/evaluator assumptions and their mitigations through the independent oracle, injected faults, negative tests, a frozen contract and a separate reporting audit. Ethics is linked to no-participant claim restraint, licence-aware repository boundaries, local/private path handling and frozen evidence integrity. Critical Reflection uses documented Stage 4 redraw, control truncation, stale transport and retained-root binding failures rather than a reconstructed success narrative.

## 6. Figures and tables

- Inserted Figure 1: author-created architecture/provenance SVG, visually checked, no experimental values.
- Inserted Figures 2–4: unchanged canonical Stage 3 SVG derivatives.
- Inserted Tables 1–3: documentary summaries of dataset adapters, schema and configuration.
- Inserted Tables 4–6: links to unchanged audited Stage 3 tables with manuscript numbering and provenance captions.
- Excluded Figure 5: the optional workbench screenshot lacks a retained source-image reproduction/privacy clearance decision. The omission is explicit in Chapter 4 and the figures plan.

## 7. Working word counts

Counts are approximate Markdown token counts and include headings, table text and figure captions. Word’s final assessed-content count will differ.

| Section | Approximate words |
|---|---:|
| Abstract | 258 |
| Introduction | 668 |
| Literature Review | 1,760 |
| Methodology and Research Design | 1,163 |
| Workbench Design and Implementation | 1,281 |
| Technical Evaluation and Results | 1,006 |
| Discussion | 1,446 |
| Ethical Considerations and Critical Reflection | 869 |
| Conclusion and Future Work | 410 |
| **Assessed body (Chapters 1–8)** | **approximately 8,603** |
| References | 791 |

## 8. Later compression candidates

No submission-length compression was performed in Phase C. The strongest later candidates are:

1. Combine repeated scope boundaries about participants and cross-platform identity after retaining one clear statement in the Introduction, Results, validity discussion and Conclusion.
2. Reduce the Literature Review’s individual tool capabilities while preserving the comparative synthesis and final gap.
3. Condense Tables 1–3 or move one documentary table to an appendix if its caption/table words materially affect the assessed count.
4. Shorten implementation policy details already represented in Table 3, especially renderer envelope and eligibility prose.
5. Merge repeated RQ evidence recaps between Discussion and Conclusion without weakening the explicit answers.
6. Tighten the Ethics/Reflection retelling of Stage 4 defects while retaining at least two concrete examples and the evidence-boundary lesson.

## 9. Validation record

- Local Markdown links in chapter sources, the working manuscript, visual plan and audit records: **29 checked, 0 broken**.
- Reference verification: **21 checked, 0 unresolved**.
- Bidirectional citation audit: **0 mismatches**.
- Obsolete-history and claim-strength scans: contextual hits reviewed as above.
- Repository lint/tests, `git diff --check`, evidence-preservation review and final working-tree review are recorded in the Phase C progress-log entry after execution.
