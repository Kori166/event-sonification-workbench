# 0015: Audited report-ready evaluation evidence

## Status

Accepted for Stage 3 Milestone 3 on 6 August 2026.

## Context

Stage 3 Milestone 2 retained two canonical real-data technical-evaluation reports under frozen
contract `0.1.0`. Dissertation tables, figures and findings need concise formatting, but manual
copying or undocumented rounding would weaken the chain from a displayed value to its source.

## Decision

- Treat the two canonical report JSON files as the primary numerical source and verify their
  expected hashes and schema before producing presentation material.
- Generate report-ready CSV, Markdown and SVG deterministically with no timestamp, private path,
  random identifier or environment-dependent metadata.
- Record every table value, figure datum and principal finding value in a machine-readable manifest
  with a structural JSON Pointer, raw value, displayed value, formula and interpretation boundary.
- Audit direct values, recalculated values, formatting, table and figure completeness, claims,
  source preservation, prohibited content and repeat bytes.
- Keep source representation distinct from eligible-event coverage because their denominators are
  different.
- Report timing in both samples and seconds. Exact sample placement does not imply that every
  decimal-seconds difference is zero.
- Limit comparisons to descriptive technical load under the selected case studies, baseline preset,
  baseline renderer and recorded environment.

## Consequences

- Tables and figures can be reused in the dissertation while retaining an auditable route to the
  canonical record and source-report hash.
- Presentation rounding does not replace the exact source value, and nulls or small non-zero values
  cannot silently become zero.
- The reporting package does not modify the frozen contract or canonical reports and does not add a
  perceptual, participant, accessibility, usability, navigation, mobility or safety claim.
- The terminal generated-file hash manifest explicitly excludes only its own impossible self-hash.
