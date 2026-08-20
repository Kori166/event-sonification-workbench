# 7. Ethical Considerations and Critical Reflection

## 7.1 Ethical and professional decisions

No participants were recruited, but this did not remove ethical responsibility. Participant studies connect perceptual, accessibility and navigation claims to human evidence (Hu *et al.*, 2020; Neugebauer *et al.*, 2020; Ji *et al.*, 2021). The project therefore adopted a non-assistive boundary: it reports technical correctness, traceability and repeatability without inferring usability, accessibility or safety. This boundary shaped the evaluation contract, risk register and reporting language.

Public availability was not treated as permission for unrestricted redistribution. Full MOT17/KITTI data, generated packages and WAV files remained local; small committed fixtures carry attribution/licence records. Logical paths, hashes and environment-variable roots enable authorised reproduction without publishing machine-specific locations. The loopback-only inspection layer is read-only, and the optional screenshot remains excluded because depicted people are not anonymised and reproduction/privacy clearance is unresolved.

Evidence integrity was supported by versioned contracts, canonical serialisation, hashes, explicit suppressions and frozen Stage 3 reports. These mechanisms do not make a mapping ethically or perceptually valid; they make its decisions inspectable and reduce undocumented post-hoc manipulation.

The same restraint applies to representation. Object labels inherit assumptions and limitations from the source datasets, while sonifying each annotation can amplify their presence without conveying uncertainty or social context. The common schema preserves source labels and metadata rather than presenting harmonised categories as neutral ground truth. Because no participant evidence established benefit, the artefact is framed as a research inspection tool and not deployed for navigation, monitoring or consequential decision-making.

## 7.2 Critical reflection

Two integration failures illustrate the value of explicit acceptance gates. First, retained-path validation assumed one output root although real packages occupied separate stage roots; detection during retained-chain testing led to corrected binding before acceptance. Second, browser checks found unstable dense-timeline presentation and frame controls that exposed only the first ten cues. Caching/stable ordering and complete frame-scoped controls corrected the defects. The lesson was that package tests alone did not prove that a researcher could follow one event consistently across the inspection surface. The final 16 checks therefore support engineering acceptance, not usability.

Scope control was equally consequential. O1 and O2 were achieved, whereas O3 and O4 were partially achieved. One deterministic baseline and rigorous technical evaluation were completed; comparative presets, density controls, scheduler ablations and some proposed measures were not. Freezing one mapping enabled stronger evidence about transformation, provenance and reproduction without introducing an unsupported comparison of perceptual quality. Reporting partial achievement is more defensible than redefining the original objectives.

R20 and R21 reinforce that restraint. Informal researcher inspection suggested that dense overlaps may be difficult to distinguish, but cannot show that listeners find them unusable. Bounding-box area is an amplitude input and limited apparent-scale proxy, not depth; pose, occlusion, truncation and perspective can change it without physical approach. Track aggregation, controlled listening studies, height/smoothing or KITTI three-dimensional fields remain future work, not completed evidence.

The principal professional lesson is that preserving the frozen baseline while correcting its inspection layer and retaining limitations produced a narrower but more credible contribution.

Reproducibility also required practical judgement about disclosure. Publishing raw paths, private media or derived audio would have simplified demonstration but weakened licence, privacy and portability controls. Separating public code/fixtures from retained local evidence made the submission less self-contained, yet produced a more defensible evidence boundary. The session contract and audit records compensate by specifying exactly what authorised researchers must resolve and verify.
