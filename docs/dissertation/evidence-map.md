# Research Question and Objective Evidence Map

## 1. Project aim

The authoritative implemented-project aim is the wording in
[`project-plan.md`](../project-management/project-plan.md):

> Design, implement and evaluate a reproducible workbench that converts annotated video data into
> normalised events, deterministic audio cues and traceable technical outputs.

This supersedes broader proposal language about preset comparison and replay experimentation.

## 2. Research questions

The final research questions confirmed for the dissertation are:

- **RQ1:** How can public annotated video datasets be transformed into a common event schema suitable for event-based sonification?
- **RQ2:** How can normalised visual events be mapped into deterministic and traceable audio cues?
- **RQ3:** How can event-based sonification outputs be evaluated using technical metrics for coverage, alignment, traceability and reproducibility?

These questions remain bounded by the completed implementation: RQ1 concerns MOT17/KITTI Tracking
conversion while preserving native ontology and provenance; RQ2 concerns one versioned deterministic
mapping and renderer; RQ3 concerns technical metrics under contract `0.1.0` rather than participant or
perceptual evaluation.

## 3. RQ-to-evidence map

| RQ | Implementation | Evidence chain | Supported finding/conclusion | Limitation |
|---|---|---|---|---|
| RQ1 | Dataset-specific MOT17 and KITTI Tracking adapters emit common schema `0.2.0`; validation and deterministic event packages preserve source rows, hashes and dataset-specific metadata. | Adapter code/tests; [`common-event-schema.md`](../data-model/common-event-schema.md); [`stage-1-closeout.md`](../development/stage-1-closeout.md); retained event IDs/hashes | Two heterogeneous tracking annotation formats were transformed into the same validated event-record contract: 30,003 MOT17 and 1,089 KITTI events, with repeat-identical packages in the recorded environment. | One sequence per dataset; not all native semantics are harmonised; KITTI optional scores are not present in case 0000; MOT17 has 988 permitted geometry warnings; no third dataset. |
| RQ2 | Preset `0.1.0` deterministically maps event time/geometry to cue start, pan, pitch and amplitude; explicit policies create cue or suppression logs; renderer `0.1.0` creates PCM WAV/render provenance. | Preset/renderer configs; [`cue-schedule.md`](../data-model/cue-schedule.md); [`audio-rendering.md`](../data-model/audio-rendering.md); [`stage-2-closeout.md`](../development/stage-2-closeout.md); traceability audits | The same fixed mapping/rendering contracts produced fully accounted, traceable cue/render chains for both cases and repeated all event/cue/audio package bytes in the recorded environment. | One technical reference mapping; no perceptual validation or comparative superiority; class modifiers not applied; area is not depth; cross-platform bytes untested. |
| RQ3 | Frozen contract `0.1.0`, manual synthetic oracle, strict retained-chain preparation, two real case reports, three isolated repeats per dataset and audited presentation derivatives. | [`technical-evaluation-contract-v0.1.0.md`](../evaluation/technical-evaluation-contract-v0.1.0.md); [`stage-3-closeout.md`](../development/stage-3-closeout.md); canonical reports; [`rq3-findings.md`](../evaluation/reporting/rq3-findings.md); independent audit | The method produced complete outcome accounting, no missed eligible events, zero sample-domain timing error, complete required traceability, quantified density/overlap and repeat-identical reports for both selected chains in the recorded environment. | Descriptive two-case evaluation, not an inferential dataset comparison; seconds-domain MOT17 differences are non-zero; no participants, alternative presets or cross-platform repeat. |

## 4. Objective-to-evidence map

The closest formal objectives are the four numbered objectives in the external
`revised_sonification_project_proposal_template_aligned.docx` (19 May 2026). Their wording is retained
below. Later repository plans changed implementation detail but do not publish a replacement numbered
objective list. Status therefore assesses the original objective as written, not a softened version.

| Objective | Implementation/deliverable | Repository and evaluation evidence | Status | Qualification |
|---|---|---|---|---|
| **O1. Define and document a sonification-oriented event schema.** Create a JSON/Pydantic schema for event type, frame/time interval, class, track identity, geometry summary, cue-relevant attributes, source dataset and provenance. Evidence: schema documentation, examples and validation tests. | JSON Schema `0.2.0`, event validation, schema/adaptor documentation, fixtures and tests. | Schema/config; Stage 1 close-out; schema and collection-validation tests. | **ACHIEVED** | Implemented as a flat per-annotation event record rather than the proposal’s richer appearance/persistence interval ontology; native differences remain metadata. |
| **O2. Build and test two core dataset adapters.** Implement adapters for KITTI Tracking and MOT17, including explicit handling of frame indexing, timestamps where available, class mapping, bounding boxes and provenance. Evidence: unit tests, conversion reports and frozen sample logs. BDD100K and KITTI MOTS mask support are stretch extensions, not minimum success criteria. | MOT17/KITTI adapters, attributed fixtures, private integration checks and full selected-sequence packages. | Adapter code/docs/tests; Stage 1 close-out; session declarations. | **ACHIEVED** | Evidence is for selected formats/sequences; BDD100K/MOTS stretch work was not done. |
| **O3. Implement deterministic cue generation and export.** Create at least two core mapping presets plus one experimental preset, a deterministic scheduler with priority, refractory period and polyphony controls, and CLI exports for event logs, cue logs, rendered audio/config metadata and reproducibility hashes. Evidence: cue logs, audio examples, configuration files and golden-file tests. | One baseline preset, deterministic cue/suppression packages, deterministic PCM renderer, CLI exports, hashes and golden/real repeat evidence. | Stage 2 configs, tests and close-out; canonical traceability evidence. | **PARTIALLY ACHIEVED** | Core deterministic generation/export is evidenced, but the promised additional presets and priority/refractory/polyphony controls were not implemented or compared. |
| **O4. Evaluate the workbench technically and reflect on limits.** Evaluate fixed clip sets using schema validity, event coverage, time-to-first-cue, false-cue rate, overlap burden, fragmentation and hash-based reproducibility. Evidence: scripts, tables, plots, ablations and a written explanation of what the artefact can and cannot prove. | Frozen technical contract and oracle; two full-sequence case reports; audited tables/figures; limitations; Stage 4 inspection acceptance. | Stage 3 close-out, reports/audits, risk register and Stage 4 records. | **PARTIALLY ACHIEVED** | Strong technical evaluation exists, but it uses timing alignment, traceability and density rather than the planned named latency/false-cue/fragmentation measures; no preset ablations were run. |

No objective is **NOT ACHIEVED** because each has a material implemented core. Two remain partial when
judged against their unedited proposal wording. The final dissertation must not hide those scope
changes by rewriting the objectives retrospectively; it should explain the controlled narrowing.

## 5. Contribution supported by the evidence

The supported contribution is research infrastructure: a modular, versioned and reproducible bridge
from two heterogeneous public tracking-annotation formats to a shared event contract, explicit cue or
suppression outcomes, deterministic PCM audio, cross-stage provenance, frozen technical evaluation and
a read-only inspection layer. Novelty should be argued as the integration and evidence discipline of
this workflow, not as a new detector, universal ontology, optimal sonification mapping or validated
assistive system.

## 6. Claims outside the evidence boundary

The evidence cannot support claims of perceptual effectiveness or intelligibility, usability, user
preference, accessibility, navigation/mobility/safety benefit, clinical value, mapping superiority,
true depth inference, all-sequence/dataset generalisation, complete semantic harmonisation or
cross-platform byte identity. Stage 4 technical browser acceptance must not be converted into a user
study. Dense-cue distinguishability (R20) and bounding-box-area/apparent-scale interpretation (R21)
are limitations and future research prompts, not validated findings about listeners.
