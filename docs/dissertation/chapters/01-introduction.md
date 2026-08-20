# 1. Introduction

## 1.1 Problem and research gap

Annotated video datasets encode frame indices, track identities, classes and bounding-box geometry. These structured observations are plausible inputs to event-based sonification, the use of non-speech sound to represent data relationships (Hermann, Hunt and Neuhoff, 2011). However, MOTChallenge and KITTI were designed for different computer-vision tasks and use different indexing, geometry, ontology and metadata conventions (Dendorfer *et al.*, 2021; Geiger *et al.*, 2013). Their native annotations therefore require explicit interpretation before they can enter one reusable sonification workflow.

Parameter-mapping sonification also requires declared relationships between data and sound (Grond and Berger, 2011; Dubus and Bresin, 2013). For annotated video, a credible workflow must additionally account for observations that produce no cue, trace rendered samples to source rows and reproduce its decisions. Although reusable sonification and dataset-management tools address adjacent concerns, the reviewed literature does not provide an integrated workflow combining heterogeneous tracking annotations, a common sonification-ready event schema, deterministic cue generation, cue-level provenance and reproducibility-focused technical evaluation.

## 1.2 Aim, questions and objectives

The project aimed to design, implement and evaluate a reproducible workbench that converts annotated video data into normalised events, deterministic audio cues and traceable technical outputs. It addressed three questions:

1. **How can public annotated video datasets be transformed into a common event schema suitable for event-based sonification?**
2. **How can normalised visual events be mapped into deterministic and traceable audio cues?**
3. **How can event-based sonification outputs be evaluated using technical metrics for coverage, alignment, traceability and reproducibility?**

The objectives were to define a provenance-preserving event representation, implement MOT17 and KITTI Tracking adapters, generate deterministic cue/suppression and audio artefacts, and evaluate the chain technically. O1 and O2 were achieved. O3 and O4 were partially achieved because one baseline mapping and a rigorous subset of the proposed evaluation were completed, but planned comparative presets, density controls and some measures were not.

## 1.3 Scope and contribution

The study used MOT17-02-DPM and KITTI Tracking 0000, one frozen mapping and renderer, and no participants. It supports technical claims about accounting, alignment, traceability, load and same-environment reproducibility, not perceptual effectiveness, accessibility, navigation or safety.

The contribution is an auditable annotation-to-sonification workbench that separates dataset-specific ingestion from common events, makes cues and suppressions explicit, preserves provenance through rendering and evaluation, and exposes retained evidence through a read-only inspection layer. Chapters 2–5 develop the literature, method, implementation and results; Chapters 6–8 interpret the research questions, validity, ethics and contribution.

