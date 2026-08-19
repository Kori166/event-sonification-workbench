# Figures and Tables Plan

## Selection principles

Use only elements that advance the research argument. Canonical Stage 3 SVGs and tables must remain
unchanged in Phase A. New diagrams may reorganise documented architecture/provenance facts but must not
introduce results. A workbench screenshot is optional contextual evidence, not evaluation evidence.
All caption text counts toward the university word limit.

## Recommended figures

| No. | Purpose | Source evidence/path | Exists? | Canonical/audited? | Section | Transformation needed | Required caption provenance |
|---|---|---|---|---|---|---|---|
| Figure 1 | One combined architecture and provenance diagram: native MOT17/KITTI annotations -> schema `0.2.0` event/package -> preset cue or suppression -> renderer/WAV/log -> contract evaluation -> Stage 4 inspection. | README; data-model docs; Decisions 0010-0016; retained session declarations. | No | New explanatory diagram; no numerical claim | Methodology/Implementation | Create a restrained vector diagram; show hashes/logs and distinguish generated stages from read-only inspection. | “Author-created from the implemented contracts and retained session declarations; no experimental values.” |
| Figure 2 | Show complete event-outcome accounting and make suppression visibly distinct from missed/excluded outcomes. | [`figure-1-event-outcomes.svg`](../evaluation/reporting/figures/figure-1-event-outcomes.svg) and source CSV/caption. | Yes | Yes; generated and independently audited | Results | None beyond report placement/scaling; do not redraw or edit values. | Name canonical reports, contract `0.1.0`, selected sequences and valid-event denominator; state presentation derivative. |
| Figure 3 | Compare cue density for the two fixed-baseline case studies. | [`figure-2-cue-density.svg`](../evaluation/reporting/figures/figure-2-cue-density.svg) and data/caption. | Yes | Yes | Results | None. | State cues/second, rendered-timeline denominator, fixed preset/renderer and non-perceptual boundary. |
| Figure 4 | Compare normalised overlap burden and support the R20 discussion. | [`figure-3-overlap-burden.svg`](../evaluation/reporting/figures/figure-3-overlap-burden.svg) and data/caption. | Yes | Yes | Results/Discussion | None. | State excess concurrent cue-seconds per evaluated second, half-open intervals and that it is not a listener-difficulty measure. |
| Figure 5 (optional) | Orient the reader to Stage 4’s synchronized source/overlay/timeline/trace/metrics inspection layer. | Current workbench launched against one retained session; Stage 4 acceptance records. | No retained screenshot | No; illustrative only | Implementation | Capture after Phase A only if licensing/privacy and legibility permit; crop private/browser chrome; do not imply it is user-study evidence. | “Researcher-produced screenshot of the local read-only inspection layer; displayed metrics derive from the cited canonical report; not usability evidence.” |

Figure 5 should be omitted if a legally safe, legible screenshot cannot be made. The three audited
Stage 3 plots are intentionally separate because combining them would create a new unaudited derivative.

## Recommended tables

| No. | Purpose | Source evidence/path | Exists? | Canonical/audited? | Section | Transformation needed | Required caption provenance |
|---|---|---|---|---|---|---|---|
| Table 1 | Compare native MOT17/KITTI format differences and how they are preserved/mapped into the shared event core. | Adapter docs, Decisions 0007/0008, schema `0.2.0`. | No | New documentary summary | Methodology | Condense only verified fields: indexing, rate, geometry, class/metadata, `DontCare`, provenance. | “Author summary of dataset adapter contracts”; cite dataset documentation and repository decisions. |
| Table 2 | Summarise the common event schema fields and provenance roles without printing a full record. | [`common-event-schema.md`](../data-model/common-event-schema.md), schema JSON. | No | New documentary summary | Implementation | Group fields as identity/time/object/geometry/provenance/metadata. | State schema version `0.2.0` and that native ontology fields remain dataset-specific. |
| Table 3 | Summarise baseline mapping and renderer rules, including the two interpretation caveats. | Preset/renderer JSON and data-model docs. | No | New configuration summary | Implementation | Include start/pan/frequency/amplitude, suppression, PCM policy; flag class modifier trace-only and area not depth. | State exact config names, versions and hashes. |
| Table 4 | Report event accounting and coverage for both cases. | [`table-1-event-accounting-and-coverage.md`](../evaluation/reporting/tables/table-1-event-accounting-and-coverage.md). | Yes | Yes | Results | Use as-is or make only typographic formatting changes in the dissertation. | Cite both canonical report hashes and contract denominators; call it an audited presentation derivative. |
| Table 5 | Report timing maxima, traceability and reproducibility compactly. | [`table-2-timing-traceability-reproducibility.md`](../evaluation/reporting/tables/table-2-timing-traceability-reproducibility.md); Table 2a for appendix. | Yes | Yes | Results | Main table as-is; place complete descriptive timing statistics in appendix if needed. | Preserve sample/seconds distinction and recorded-environment limit. |
| Table 6 | Report density and overlap values. | [`table-3-density-and-overlap.md`](../evaluation/reporting/tables/table-3-density-and-overlap.md). | Yes | Yes | Results | Use as-is. | Preserve units, half-open interval semantics and non-perceptual interpretation boundary. |
| Table 7 (optional) | Give a compact RQ/objective evidence and completion summary for discussion/appendix. | [`evidence-map.md`](evidence-map.md). | No | Phase A synthesis, not experimental evidence | Discussion or appendix | Reduce to one line per RQ/objective; statuses must remain O1/O2 achieved, O3/O4 partial unless researcher supplies authoritative revised objectives. | “Author synthesis from repository evidence; objective status assessed against May 2026 proposal wording.” |

Avoid a separate limitations table in the main body unless prose becomes harder to scan; R20/R21 and
threats need explanation, not just labels. Avoid decorative code screenshots, console output, file-tree
screenshots and multiple UI views. Exact hashes and long timing statistics fit better in appendices.

## Caption and handling rules

- Refer to each figure/table before it appears and explain the argumentative point in prose.
- Use the source captions in [`figure-captions.md`](../evaluation/reporting/figures/figure-captions.md)
  and [`table-captions.md`](../evaluation/reporting/tables/table-captions.md) as the minimum provenance
  boundary for audited Stage 3 items.
- Never label a Stage 3 derivative “raw data”; the canonical JSON report is the numerical source.
- Never label the optional screenshot as evaluation, usability testing or participant evidence.
- Record any dissertation-only scaling/cropping as presentation transformation; do not edit the
  canonical SVG or source CSV.
