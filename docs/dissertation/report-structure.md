# Final Dissertation Structure and Word Budget

## Planning basis

The module specification defines a 5,000-6,000-word written thesis. The university Assessment Content
Limit Policy counts headings, citations, text boxes, tables, graphs, figures/diagrams, quotations and
lists. It excludes the title, reference list, appendices, headers/footers, abstract and reference-only
footnotes/endnotes. Both PDFs were inspected externally (`UFCF9Y-60-M_CSCT_Masters_Project_2023.pdf`
and `assessment-content-limit-policy.pdf`); confirm that no newer course-specific brief overrides them.

The assessed-body target below is **5,500 words**, leaving a 500-word margin. Table/figure words must
be included manually where the word processor does not count embedded text. Appendices should contain
supporting reference material only; arguments required for marking must remain in the main body.

The final research questions must be reproduced verbatim:

1. **How can public annotated video datasets be transformed into a common event schema suitable for event-based sonification?**
2. **How can normalised visual events be mapped into deterministic and traceable audio cues?**
3. **How can event-based sonification outputs be evaluated using technical metrics for coverage, alignment, traceability and reproducibility?**

| Section | Purpose and questions answered | Evidence to use | Keep elsewhere | Budget |
|---|---|---|---|---:|
| Abstract (excluded if the policy applies) | Concise problem, method, artefact, two-case technical findings, contribution and evidence boundary. | Baseline and audited Stage 3 results. | Literature detail, implementation diary, new claims. | 200 excluded |
| **1. Introduction** | Why annotation-driven sonification infrastructure is a research problem; scope, aim, concise RQs, contribution and chapter route. | Project aim; Decision 0001; evidence map. | Detailed literature and results. | 550 |
| **2. Literature Review** | Synthesize sonification mapping/tooling, annotated-video datasets/provenance, reproducible research infrastructure and technical evaluation; establish the integration gap and need for claim restraint. | Verified primary literature from the proposal, rechecked before citation; dataset/tool documentation. | Project implementation description; unverified proposal references; generic background catalogue. | 950 |
| **3. Methodology and Research Design** | Explain design-science/software-artefact approach, secondary dataset selection, frozen contracts, case selection, deterministic design, Stage 3 metric definitions/oracle, validity/reliability and ethics-by-scope. | Decisions 0001, 0013-0015; evaluation protocol/contract; assessment/module outcomes. | Code-level details, numerical results, UI tour. | 800 |
| **4. Workbench Design and Implementation** | Show the native annotation -> event -> cue/suppression -> render/provenance pipeline; schema, adapters, mapping, renderer, package identities and Stage 4 inspection layer. Explain what was actually built. | Data-model docs, configs, Stage 1/2 close-outs, session contract and Stage 4 records. | Planned presets/ablations, evaluative conclusions, development chronology. | 1,000 |
| **5. Technical Evaluation and Results** | State cases/config/environment; report accounting/coverage, timing, traceability, density/overlap and reproducibility without interpretation inflation. | Canonical JSON reports and audited Tables 1-3/Figures 1-3 only. | Perceptual language, unsupported causal comparison, full raw values better placed in appendix. | 1,000 |
| **6. Discussion** | Answer RQ1, RQ2 and RQ3 explicitly; relate findings to literature and contribution; discuss threats, generalisability and scope changes. Address R20 dense cues and R21 area/apparent-scale. | Evidence map, claim matrix, risk register, RQ3 findings, reconciliation. | New results, long ethics narrative, implementation recap. | 750 |
| **7. Ethical Considerations and Critical Reflection** | Explain public secondary-data/licensing/privacy choices, non-assistive boundary, responsible communication, project management and reflective lessons from scope control/evidence discipline. | Decision 0001, risk/supervision/progress logs, licence records, module outcomes MO5/MO6. | Claims of user benefit; a diary-style chronology; future work not grounded in limitations. | 300 |
| **8. Conclusion and Future Work** | Direct one-paragraph answer to each RQ, concise contribution, objective status, limitations and prioritised future work. | Evidence map and boundaries. | New citations/results; claims that planned work occurred. | 150 |
| **Assessed body total** |  |  |  | **5,500** |

References and minimal appendices follow but are not numbered as argument-bearing chapters. Suggested
appendices are: exact contract/version/hash table; expanded timing statistics; objective/claim audit;
and reproduction commands. Do not move required explanations there to escape the limit.

## Chapter-level guidance

### 1. Introduction

Lead with the interoperability/reproducibility problem, not assistive benefit. State the final title,
project-plan aim, three selected RQs and contribution boundary. Mention MOT17/KITTI and the absence of
participant evaluation once, clearly.

### 2. Literature Review

Organise by arguments rather than tools: (1) sonification and parameter mapping; (2) annotated video,
tracking data and ontology/provenance differences; (3) reproducible sonification/research tooling;
(4) evaluation of technical outputs versus human-centred outcomes. End with the precise infrastructure
gap. Re-verify every external citation in Phase B; proposal bibliographies are leads, not evidence.

### 3. Methodology and Research Design

Justify two bounded real case studies and one fixed baseline. Define “event”, “cue”, “suppression”,
“technical evaluation” and the recorded-environment reproducibility scope. Explain the synthetic oracle
before the real cases. Include threats introduced by sequence selection, dataset differences and metric
construct validity.

### 4. Workbench Design and Implementation

Keep one coherent architecture narrative. Preserve native ontology differences. Explain deterministic
IDs, canonical serialisation, hashes and the event-to-render evidence chain. State class-modifier and
area limitations beside the mapping description. Treat Stage 4 as inspection/demonstration of frozen
evidence, not a fourth experimental method.

### 5. Technical Evaluation and Results

Use audited values without recalculation. Separate eligible coverage from source representation and
sample-domain from seconds-domain timing. Density/overlap values are descriptive loads. Report the
same-environment repeat evidence and explicitly state that cross-platform identity was untested.

### 6. Discussion

Use subheadings `RQ1`, `RQ2`, `RQ3`, then `Threats to validity and limitations`. RQ1 can conclude that
the common contract worked for the two selected formats, not all datasets. RQ2 can conclude that the
fixed contracts are deterministic and traceable, not perceptually effective. RQ3 can use the bounded
answer already audited. R20/R21 belong here because they constrain interpretation and motivate work.

### 7. Ethical Considerations and Critical Reflection

Connect public-data licensing, non-redistribution, identifiable imagery and avoidance of assistive
overclaiming to research conduct. Reflect critically on the deliberate change from ambitious multi-
preset experiments to a narrower, well-audited infrastructure contribution.

### 8. Conclusion and Future Work

Answer all RQs explicitly and state O1/O2 achieved and O3/O4 partially achieved against original
wording. Prioritise future participant/perceptual evaluation, alternative mapping/density management,
height/smoothed apparent-scale alternatives, broader sequences/datasets and cross-platform testing.
Do not imply that any is already underway or that one baseline is superior.
