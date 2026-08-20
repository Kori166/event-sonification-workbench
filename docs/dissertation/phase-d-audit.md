# Stage 5 Phase D Audit

## Scope and baseline

Phase D was an editorial and quality-assurance pass. It did not alter the implementation, mapping,
renderer, evaluation contracts, retained audio or canonical Stage 3 evidence. The compression plan
was created before chapter editing. The Phase C assessed-body estimate was 8,603 words.

## Compression outcome

| Chapter | Phase C estimate | Phase D Markdown source |
|---|---:|---:|
| 1. Introduction | 668 | 407 |
| 2. Literature Review | 1,760 | 1,076 |
| 3. Methodology and Research Design | 1,163 | 761 |
| 4. Workbench Design and Implementation | 1,281 | 743 |
| 5. Technical Evaluation and Results | 1,006 | 696 |
| 6. Discussion | 1,446 | 770 |
| 7. Ethical Considerations and Critical Reflection | 869 | 570 |
| 8. Conclusion and Future Work | 410 | 271 |
| **Chapters 1–8** | **8,603** | **5,294** |

The formatted Word manuscript contains **5,650 assessed words** across Chapters 1–8, including
headings, captions and embedded table content and excluding the title/front matter, Abstract and
References. Relative to the Phase C estimate, this is a reduction of **2,953 words (34.3%)**. The
formatted count is authoritative and lies within both the 5,000–6,000 requirement and the preferred
5,400–5,700 safety range. The Abstract contains 258 repository-source words.

Compression consolidated individual tool descriptions, implementation mechanics, repeated metric
definitions, duplicated results and repeated limitation statements. It retained the critical
literature synthesis, methodological rationale, descriptive results, explicit RQ answers, threats to
validity, ethics, critical reflection, R20, R21 and the stated objective outcomes.

## Research and evidence audit

The frozen RQ wording appears verbatim in the Introduction and as explicit answer headings in the
Discussion; the Conclusion answers the same three questions concisely. O1 and O2 remain achieved;
O3 and O4 remain partially achieved. R20 remains bounded informal researcher reflection about dense
overlap, and R21 remains the limitation that bounding-box area is an apparent-scale proxy rather than
metric depth.

The final manuscript preserves the canonical results:

- MOT17-02-DPM: 30,003 events, 26,960 cues and 3,043 intentional suppressions;
- KITTI Tracking 0000: 1,089 events, 711 cues and 378 intentional suppressions;
- 100% eligible-event coverage, complete cue/suppression traceability and zero maximum integer-sample
  error for both cases;
- cue density of 1,342.18 versus 46.11 cues/s and normalised overlap burden of 160.06 versus 4.53;
- repeated identical outputs only within the recorded Windows/AMD64/Python environment.

The canonical evaluation reports retain their Phase A SHA-256 hashes:

- MOT17: `d847e805d0b2d7ccd50cd315bbcecfc0ad525f40e7c4c2013938f955d20f13e5`;
- KITTI: `b5589590a8c645bd7b5654d0318bf90fdb412f987719c26c2374bf3e487f9ff2`.

No discrepancy was found and `docs/evaluation` has no Phase D modification. Claim-strength and
terminology review found all accessibility, navigation, usability and perceptual references bounded
as non-findings or literature context. Obsolete-history searches found no old result reported as
final evidence; the sole scheduler-ablation occurrence correctly identifies uncompleted work.

## Citation and reference audit

The final Markdown and transferred manuscript retain 21 unique cited sources and 21 UWE Harvard
reference entries. Citation-to-reference mismatches: 0. Reference-to-citation mismatches: 0.
Unresolved bibliographic issues or placeholders: 0. Word transfer preserved the reference text and
hanging indentation.

## Word manuscript

Because the discovered historical Word source pre-dated implementation, it was not overwritten. A
new private submission manuscript was built from the Phase D sources:

- final Word: `C:\Users\korif\OneDrive\Documents\MSc Project - Event-Based Sonification Workbench\Submission\24046378 report.docx`;
- preserved initial formatted candidate: `C:\Users\korif\OneDrive\Documents\MSc Project - Event-Based Sonification Workbench\Submission\backups\24046378 report - initial formatted candidate.docx`.

The document uses the full dissertation title, verified researcher/module metadata, A4 portrait,
2.54 cm margins, styled heading hierarchy, page-number field, Contents, List of Figures, List of
Tables, inline figures, repeating table headers and UWE Harvard references. Its verified navigation
map places the Abstract on page 2, Chapters 1–8 on pages 6, 7, 10, 12, 14, 18, 20 and 22, and
References on page 23. The package has one section, nine Heading 1 and 25 Heading 2 paragraphs, four
inline images, no comments and no tracked-change elements. Placeholder, replacement-character and
raw fenced-Markdown scans found no defect. The accessibility audit reported 0 high-, medium- or
low-severity findings.

## Figures and tables

The final candidates contain:

1. author-created implemented architecture and provenance flow;
2. audited event outcomes;
3. audited cue density;
4. audited normalised overlap burden;
5. documentary native-case/adapter comparison (Table 1);
6. documentary common-schema summary (Table 2);
7. documentary frozen mapping/renderer rules (Table 3);
8. audited event accounting and coverage (Table 4);
9. audited timing, traceability and reproducibility (Table 5);
10. audited density and overlap (Table 6).

The optional workbench screenshot remains excluded. Dissertation-only PNG conversion and scaling did
not alter the canonical SVGs, audited table sources or numerical values.

## PDF and layout QA

The exported candidate is
`C:\Users\korif\OneDrive\Documents\MSc Project - Event-Based Sonification Workbench\Submission\24046378 report.pdf`.
It contains 24 non-empty A4 pages. Every page of the final candidate was visually inspected at full
render resolution. Earlier iterations exposed and corrected cropped figures, unsuitable list styling,
reference alignment and an avoidable widow page. The final Contents/List page numbers match the
rendered document; figures and tables are readable and unclipped; captions remain attached; no blank
accidental page, comment, tracked change, placeholder or corrupted visible symbol remains.

Final private-file checksums:

- DOCX SHA-256: `3a3bde910edafcbb3c05543f6de28b4410bb2d93d4f556f7943fa0094da6a287`
  (138,972 bytes);
- PDF SHA-256: `3e2706b4075cd84dc33e51f4d841e380e0a869032d67b570e18c56f214f0b0c9`
  (407,795 bytes).

## Validation

- deterministic manuscript assembly: passed;
- local Markdown links: 104 checked, 0 missing;
- Ruff: passed;
- automated suite: 280 passed, 6 private-data integrations skipped;
- bidirectional citation/reference audit: passed, 21/21;
- Word XML tracked-change/comment/placeholder scan: passed;
- PDF structure/text extraction: 24 A4 pages, 0 empty-text pages;
- `git diff --check`: passed;
- frozen evaluation-report hashes: passed.

## Remaining researcher-controlled work

Phase D is complete, but Stage 5 is not closed. Remaining work is focused supervisor review of the
research gap, Literature Review synthesis, Discussion/RQ answers, critical reflection and Conclusion;
incorporation of any genuine feedback; final institutional submission requirements and upload;
repository-access verification where required; and viva preparation/rehearsal. No supervision or
submission action is claimed as completed.
